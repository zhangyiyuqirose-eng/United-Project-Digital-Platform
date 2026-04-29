"""AI Domain Service — 11 F-12xx requirements implementation.

Provides intelligent features backed by LLM integration or rule-based fallback.
All methods return dict payloads suitable for ApiResponse wrapping.
"""

from __future__ import annotations

import json as json_module
import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project.models import Project, ProjectRisk, ProjectTask
from app.models.timesheet.models import Timesheet
from app.services.llm_client import LlmClient, RuleBasedClient

logger = logging.getLogger(__name__)


# ── System prompts for LLM-powered methods ──────────────────────────────

DOC_SYSTEM_PROMPT = """You are a professional project document writer. Generate formal,
well-structured project documents in Chinese. Follow the provided template structure.
Include all sections, fill in project-specific data, and maintain a professional tone.
Output only the document content, no meta-commentary."""

RISK_SYSTEM_PROMPT = """You are a project risk analyst. Based on the provided project metrics
(progress, CPI, SPI, open risks, health score), identify potential risks. For each risk,
provide: risk type, severity (high/medium/low), confidence (0.0-1.0), and a clear reason.
Respond in JSON array format: [{"riskType":"...", "severity":"...", "confidence":0.0, "reason":"..."}]."""

NLQ_SYSTEM_PROMPT = """You are a natural-language-to-data query engine. Convert the user's
natural language question about project data into a structured query intent classification.
Supported intents: project_status, cost_summary, risk_overview, task_progress, resource_utilization.
Respond in JSON: {"intent":"...", "parameters":{...}, "explanation":"..."}."""

MEETING_SYSTEM_PROMPT = """You are a meeting minutes analyst. Extract the following from
the meeting content: key discussion points, decisions made, and action items with owners.
Respond in JSON format:
{"keyPoints":["..."], "decisions":["..."], "actionItems":[{"item":"...","owner":"..."}], "summary":"..."}."""

KNOWLEDGE_SYSTEM_PROMPT = """You are a knowledge retrieval analyst. Analyze the user's search
query and the provided document results. Rank the results by relevance, provide a relevance
score (0-100) for each, and suggest related search terms. Respond in JSON format:
{"rankedResults":[...], "relevanceSummary":"...", "suggestedTerms":[...]}."""


class AIService:
    """AI features: document generation, risk prediction, NLQ, etc."""

    def __init__(self, db: AsyncSession, llm_client: LlmClient = None) -> None:
        self.db = db
        if llm_client is None:
            self.llm = RuleBasedClient(self)
        else:
            self.llm = llm_client
            # If the fallback inside ResilientLlmClient is a RuleBasedClient,
            # inject self so it can access the db for rule-based responses.
            fallback = getattr(llm_client, "fallback", None)
            if isinstance(fallback, RuleBasedClient):
                fallback.set_ai_service(self)

    @property
    def _llm_enabled(self) -> bool:
        """True when a real LLM client (not pure rule-based) is configured."""
        return not isinstance(self.llm, RuleBasedClient)

    # ── F-1201: Smart Document Generation ───────────────────────────

    async def generate_document(self, req: dict) -> dict:
        """Generate a project document based on template and project data."""
        project = await self._get_project(req["project_id"])
        doc_type = req.get("document_type", "general")
        template_id = req.get("template_id", "default")
        extra = req.get("extra_context", {})

        # Try LLM generation when a real client is configured
        if self._llm_enabled:
            try:
                template = self._fill_document_template(project, doc_type, extra)
                project_data = self._serialise_project(project)
                user_msg = (
                    f"文档类型: {doc_type}\n"
                    f"模板ID: {template_id}\n"
                    f"项目名称: {project.project_name if project else 'Unknown'}\n\n"
                    f"参考模板:\n{template}\n\n"
                    f"项目数据:\n{json_module.dumps(project_data, ensure_ascii=False, default=str)}\n\n"
                    f"补充上下文:\n{json_module.dumps(extra, ensure_ascii=False, default=str) if extra else '无'}"
                )
                response = await self.llm.chat(
                    system_prompt=DOC_SYSTEM_PROMPT,
                    user_message=user_msg,
                    max_tokens=8192,
                    temperature=0.3,
                )
                if response.model != "rule-based":
                    return {
                        "documentType": doc_type,
                        "projectId": req["project_id"],
                        "projectName": project.project_name if project else "",
                        "content": response.content,
                        "generatedAt": datetime.utcnow().isoformat(),
                        "templateUsed": template_id,
                        "model": response.model,
                    }
            except Exception as exc:
                logger.warning("LLM document generation failed, using rule-based fallback: %s", exc)

        content = self._fill_document_template(project, doc_type, extra)
        return {
            "documentType": doc_type,
            "projectId": req["project_id"],
            "projectName": project.project_name if project else "",
            "content": content,
            "generatedAt": datetime.utcnow().isoformat(),
            "templateUsed": template_id,
        }

    # ── F-1202: Smart Report Generation ─────────────────────────────

    async def generate_report(self, req: dict) -> dict:
        """Generate a progress/cost/quality report."""
        project_id = req["project_id"]
        report_type = req.get("report_type", "progress")
        project = await self._get_project(project_id)

        if report_type == "progress":
            data = await self._build_progress_report(project_id)
        elif report_type == "cost":
            data = await self._build_cost_report(project_id)
        elif report_type == "quality":
            data = await self._build_quality_report(project_id)
        else:
            data = {"message": f"Report type '{report_type}' generated", "sections": []}

        return {
            "reportType": report_type,
            "projectId": project_id,
            "projectName": project.project_name if project else "",
            "data": data,
            "generatedAt": datetime.utcnow().isoformat(),
        }

    # ── F-1203: Smart Risk Prediction ───────────────────────────────

    async def predict_risks(self, project_id: str) -> dict:
        """Predict project risks based on historical data and current metrics."""
        project = await self._get_project(project_id)
        if not project:
            return {"projectId": project_id, "predictions": []}

        # Gather current state
        open_risks_stmt = select(ProjectRisk).where(
            ProjectRisk.project_id == project_id, ProjectRisk.status == "open"
        )
        open_risks = (await self.db.execute(open_risks_stmt)).scalars().all()

        progress = project.progress or 0
        cpi = float(project.evm_cpi or 1.0)
        spi = float(project.evm_spi or 1.0)

        # Try LLM risk analysis
        if self._llm_enabled:
            try:
                metrics = {
                    "projectId": project_id,
                    "projectName": project.project_name,
                    "progress": progress,
                    "cpi": cpi,
                    "spi": spi,
                    "healthScore": float(project.health_score) if project.health_score else None,
                    "openRisksCount": len(open_risks),
                    "openRiskTypes": [r.risk_type for r in open_risks if hasattr(r, "risk_type")],
                    "startDate": str(project.start_date) if project.start_date else None,
                    "endDate": str(project.end_date) if project.end_date else None,
                }
                user_msg = json_module.dumps(metrics, ensure_ascii=False, default=str)
                response = await self.llm.chat(
                    system_prompt=RISK_SYSTEM_PROMPT,
                    user_message=user_msg,
                    max_tokens=2048,
                    temperature=0.2,
                )
                # Parse LLM JSON response
                try:
                    llm_predictions = json_module.loads(response.content)
                    if isinstance(llm_predictions, list) and len(llm_predictions) > 0:
                        return {
                            "projectId": project_id,
                            "projectName": project.project_name,
                            "predictions": llm_predictions,
                            "totalOpenRisks": len(open_risks),
                            "healthScore": float(project.health_score) if project.health_score else None,
                            "model": response.model,
                        }
                except (json_module.JSONDecodeError, TypeError):
                    logger.warning("Failed to parse LLM risk response as JSON, falling back")
            except Exception as exc:
                logger.warning("LLM risk prediction failed, using rule-based fallback: %s", exc)

        # Rule-based risk scoring (fallback)
        predictions = []
        if progress < 30 and cpi < 0.9:
            predictions.append({
                "riskType": "cost_overrun",
                "severity": "high",
                "confidence": 0.85,
                "reason": "Low progress with poor cost efficiency indicates potential budget overrun",
            })
        if spi < 0.85:
            predictions.append({
                "riskType": "schedule_delay",
                "severity": "high",
                "confidence": 0.90,
                "reason": f"SPI={spi:.2f} indicates significant schedule slippage",
            })
        if len(open_risks) >= 3:
            predictions.append({
                "riskType": "risk_accumulation",
                "severity": "medium",
                "confidence": 0.75,
                "reason": f"{len(open_risks)} open risks may compound into delivery failure",
            })

        return {
            "projectId": project_id,
            "projectName": project.project_name,
            "predictions": predictions,
            "totalOpenRisks": len(open_risks),
            "healthScore": float(project.health_score) if project.health_score else None,
        }

    # ── F-1204: Natural Language Query ──────────────────────────────

    async def nlq_query(self, req: dict) -> dict:
        """Convert natural language to data query and return results."""
        query = req["query"]

        # Try LLM-based natural language understanding
        if self._llm_enabled:
            try:
                response = await self.llm.chat(
                    system_prompt=NLQ_SYSTEM_PROMPT,
                    user_message=query,
                    max_tokens=1024,
                    temperature=0.1,
                )
                parsed = json_module.loads(response.content)
                intent = parsed.get("intent", "unknown")
                if intent == "project_status":
                    result = await self._query_project_status(query)
                elif intent == "cost_summary":
                    result = await self._query_cost_summary()
                elif intent == "risk_overview":
                    result = await self._query_risk_overview()
                else:
                    result = {"message": f"Query understood: '{query}'", "data": [], "llmExplanation": parsed.get("explanation", "")}
                return {"query": query, "intent": intent, "result": result, "model": response.model}
            except Exception as exc:
                logger.warning("LLM NLQ parsing failed, using rule-based fallback: %s", exc)

        # Rule-based intent extraction from NL query (fallback)
        intent = self._extract_nlq_intent(query)
        if intent == "project_status":
            result = await self._query_project_status(query)
        elif intent == "cost_summary":
            result = await self._query_cost_summary()
        elif intent == "risk_overview":
            result = await self._query_risk_overview()
        else:
            result = {"message": f"Query understood: '{query}'", "data": []}

        return {"query": query, "intent": intent, "result": result}

    # ── F-1205: Meeting Minutes Extraction ──────────────────────────

    async def summarize_meeting(self, req: dict) -> dict:
        """Extract key information and action items from meeting content."""
        content = req.get("meeting_content", "")
        meeting_type = req.get("meeting_type", "general")

        # Try LLM meeting analysis
        if self._llm_enabled and content.strip():
            try:
                user_msg = f"会议类型: {meeting_type}\n\n会议内容:\n{content[:8000]}"
                response = await self.llm.chat(
                    system_prompt=MEETING_SYSTEM_PROMPT,
                    user_message=user_msg,
                    max_tokens=4096,
                    temperature=0.3,
                )
                parsed = json_module.loads(response.content)
                return {
                    "meetingType": meeting_type,
                    "actionItems": parsed.get("actionItems", []),
                    "decisions": parsed.get("decisions", []),
                    "keyPoints": parsed.get("keyPoints", []),
                    "summary": parsed.get("summary", content[:500]),
                    "model": response.model,
                }
            except Exception as exc:
                logger.warning("LLM meeting summarization failed, using rule-based fallback: %s", exc)

        # Rule-based extraction (fallback)
        action_items = self._extract_action_items(content)
        decisions = self._extract_decisions(content)
        return {
            "meetingType": meeting_type,
            "actionItems": action_items,
            "decisions": decisions,
            "keyPoints": self._extract_key_points(content),
            "summary": content[:500] if len(content) > 500 else content,
        }

    # ── F-1206: Smart Approval Suggestions ──────────────────────────

    async def approval_suggest(self, process_id: str) -> dict:
        """Generate approval suggestion based on process materials."""
        # Placeholder: in production, analyze process materials via LLM
        return {
            "processId": process_id,
            "suggestion": "review",  # approve / reject / review
            "confidence": 0.6,
            "reasoning": "Manual review recommended: process requires human judgment",
            "checklist": [
                {"item": "Document completeness", "status": "pending"},
                {"item": "Budget compliance", "status": "pending"},
                {"item": "Risk assessment", "status": "pending"},
            ],
        }

    # ── F-1207: Smart WBS Recommendation ────────────────────────────

    async def recommend_wbs(self, project_type: str, project_name: Optional[str] = None) -> dict:
        """Recommend WBS structure based on project type and history."""
        templates = {
            "software": [
                {"name": "需求分析", "level": 1, "children": ["需求调研", "需求文档", "需求评审"]},
                {"name": "系统设计", "level": 1, "children": ["架构设计", "数据库设计", "接口设计"]},
                {"name": "开发实现", "level": 1, "children": ["前端开发", "后端开发", "接口联调"]},
                {"name": "测试验证", "level": 1, "children": ["单元测试", "集成测试", "UAT"]},
                {"name": "上线部署", "level": 1, "children": ["环境准备", "部署实施", "上线验证"]},
            ],
            "infrastructure": [
                {"name": "需求调研", "level": 1},
                {"name": "方案设计", "level": 1},
                {"name": "设备采购", "level": 1},
                {"name": "实施部署", "level": 1},
                {"name": "验收测试", "level": 1},
            ],
            "consulting": [
                {"name": "项目启动", "level": 1},
                {"name": "现状调研", "level": 1},
                {"name": "方案设计", "level": 1},
                {"name": "方案评审", "level": 1},
                {"name": "交付验收", "level": 1},
            ],
        }

        wbs = templates.get(project_type, templates["software"])
        return {
            "projectType": project_type,
            "projectName": project_name,
            "wbsStructure": wbs,
            "recommendedPhases": len(wbs),
        }

    # ── F-1208: Smart Timesheet Forecast ────────────────────────────

    async def forecast_timesheet(self, project_id: str, user_id: Optional[str] = None) -> dict:
        """Forecast timesheet hours based on historical data."""
        filters = [Timesheet.project_id == project_id]
        if user_id:
            filters.append(Timesheet.staff_id == user_id)

        stmt = select(func.avg(Timesheet.hours), func.sum(Timesheet.hours)).where(*filters)
        result = await self.db.execute(stmt)
        row = result.first()
        avg_hours = float(row[0]) if row and row[0] else 8.0
        total_hours = float(row[1]) if row and row[1] else 0.0

        return {
            "projectId": project_id,
            "userId": user_id,
            "averageDailyHours": round(avg_hours, 1),
            "totalLoggedHours": round(total_hours, 1),
            "forecastedRemaining": round(avg_hours * 20, 1),  # Next 20 working days
            "recommendation": "Based on historical average of {:.1f} hours/day".format(avg_hours),
        }

    # ── F-1209: Smart Knowledge Retrieval ───────────────────────────

    async def search_knowledge(self, req: dict) -> dict:
        """Semantic knowledge base search."""
        from app.models.knowledge.models import KnowledgeDoc

        query = req.get("query", "")
        category = req.get("category")
        top_k = req.get("top_k", 10)

        # Execute keyword search first (RAG vector search requires embedding model)
        stmt = select(KnowledgeDoc).where(KnowledgeDoc.status == "published")
        if category:
            stmt = stmt.where(KnowledgeDoc.doc_type == category)
        if query:
            stmt = stmt.where(KnowledgeDoc.title.ilike(f"%{query}%"))
        stmt = stmt.limit(top_k)

        result = await self.db.execute(stmt)
        docs = result.scalars().all()

        base_results = [
            {"docId": d.doc_id, "docName": d.title, "docType": d.doc_type,
             "tags": getattr(d, "category", ""), "downloadCount": 0}
            for d in docs
        ]

        # Try LLM-powered relevance ranking and query expansion
        if self._llm_enabled and query.strip() and base_results:
            try:
                docs_text = json_module.dumps(
                    [{"id": r["docId"], "title": r["docName"], "type": r["docType"]} for r in base_results],
                    ensure_ascii=False,
                )
                user_msg = f"用户查询: {query}\n\n检索结果:\n{docs_text}"
                response = await self.llm.chat(
                    system_prompt=KNOWLEDGE_SYSTEM_PROMPT,
                    user_message=user_msg,
                    max_tokens=2048,
                    temperature=0.2,
                )
                parsed = json_module.loads(response.content)
                return {
                    "query": query,
                    "category": category,
                    "totalMatches": len(docs),
                    "results": base_results,
                    "relevanceSummary": parsed.get("relevanceSummary", ""),
                    "suggestedTerms": parsed.get("suggestedTerms", []),
                    "model": response.model,
                }
            except Exception as exc:
                logger.warning("LLM knowledge search ranking failed, using keyword results: %s", exc)

        return {
            "query": query,
            "category": category,
            "totalMatches": len(docs),
            "results": base_results,
        }

    # ── F-1210: Smart Compliance Check ──────────────────────────────

    async def compliance_check(self, req: dict) -> dict:
        """Automated compliance check for project documents and processes."""
        from app.models.project.models import ProjectClose, PreInitiation

        project_id = req["project_id"]
        check_type = req.get("check_type", "all")
        project = await self._get_project(project_id)

        checks = []

        # Pre-initiation check
        pi_stmt = select(PreInitiation).where(PreInitiation.project_id == project_id)
        pi = (await self.db.execute(pi_stmt)).scalar_one_or_none()
        checks.append({
            "checkName": "预立项文档",
            "status": "pass" if pi else "fail",
            "details": "预立项申请已提交" if pi else "缺少预立项申请文档",
        })

        # Project status check
        if project:
            checks.append({
                "checkName": "项目状态",
                "status": "pass" if project.status not in ("cancelled",) else "fail",
                "details": f"当前状态: {project.status}",
            })

        # Closeout check
        if check_type in ("closeout", "all"):
            close_stmt = select(ProjectClose).where(ProjectClose.project_id == project_id)
            close = (await self.db.execute(close_stmt)).scalar_one_or_none()
            checks.append({
                "checkName": "结项文档",
                "status": "pass" if close else "pending",
                "details": "结项申请已提交" if close else "尚未提交结项申请",
            })

        overall = all(c["status"] == "pass" for c in checks)
        return {
            "projectId": project_id,
            "projectName": project.project_name if project else "",
            "checkType": check_type,
            "overall": "pass" if overall else "fail",
            "checks": checks,
        }

    # ── F-1211: Smart Data Insights ─────────────────────────────────

    async def data_insights(self, req: dict) -> dict:
        """Generate data insights based on analysis scope."""
        scope = req.get("scope", "project")
        project_ids = req.get("project_ids")

        if scope == "project" and project_ids:
            insights = []
            for pid in project_ids[:10]:  # Limit to avoid heavy queries
                project = await self._get_project(pid)
                if project:
                    if project.progress and project.progress < 50:
                        insights.append({
                            "projectId": pid,
                            "insight": f"项目进度偏低 ({project.progress}%)",
                            "severity": "warning",
                        })
                    if project.evm_cpi and float(project.evm_cpi) < 0.9:
                        insights.append({
                            "projectId": pid,
                            "insight": f"成本效率偏低 (CPI={project.evm_cpi})",
                            "severity": "high",
                        })
            return {"scope": scope, "insights": insights, "analyzedProjects": len(project_ids)}

        # Portfolio-level insight
        total_stmt = select(func.count(Project.project_id))
        total = (await self.db.execute(total_stmt)).scalar() or 0
        active_stmt = select(func.count(Project.project_id)).where(Project.status == "active")
        active = (await self.db.execute(active_stmt)).scalar() or 0

        return {
            "scope": scope,
            "insights": [
                {"insight": f"共有 {total} 个项目，其中 {active} 个活跃", "severity": "info"},
            ],
        }

    # ── Internal helpers ────────────────────────────────────────────

    @staticmethod
    def _serialise_project(project) -> dict:
        """Convert a Project ORM object to a JSON-safe dict for LLM prompts."""
        if project is None:
            return {}
        return {
            "projectId": project.project_id,
            "projectName": project.project_name,
            "status": project.status,
            "progress": project.progress,
            "budget": float(project.budget) if project.budget else 0,
            "evmCpi": float(project.evm_cpi) if project.evm_cpi else 1.0,
            "evmSpi": float(project.evm_spi) if project.evm_spi else 1.0,
            "healthScore": float(project.health_score) if project.health_score else None,
            "startDate": str(project.start_date) if project.start_date else None,
            "endDate": str(project.end_date) if project.end_date else None,
        }

    async def _get_project(self, project_id: str):
        stmt = select(Project).where(Project.project_id == project_id)
        return (await self.db.execute(stmt)).scalar_one_or_none()

    def _fill_document_template(self, project, doc_type: str, context: dict | None) -> str:
        """Rule-based document template filling."""
        name = project.project_name if project else "Unknown"
        templates = {
            "initiation": f"项目立项报告 - {name}\n\n一、项目概况\n二、可行性分析\n三、预算规划",
            "proposal": f"项目建议书 - {name}\n\n一、背景分析\n二、目标设定\n三、实施方案",
            "summary": f"项目总结报告 - {name}\n\n一、项目回顾\n二、成果总结\n三、经验教训",
        }
        return templates.get(doc_type, f"文档内容 - {name}\n\n通用模板内容")

    async def _build_progress_report(self, project_id: str) -> dict:
        stmt = select(func.count(ProjectTask.task_id)).where(
            ProjectTask.project_id == project_id, ProjectTask.status == "completed"
        )
        completed = (await self.db.execute(stmt)).scalar() or 0
        return {"completedTasks": completed, "reportType": "progress"}

    async def _build_cost_report(self, project_id: str) -> dict:
        project = await self._get_project(project_id)
        return {
            "budget": float(project.budget) if project and project.budget else 0,
            "evmCpi": float(project.evm_cpi) if project and project.evm_cpi else 1.0,
            "reportType": "cost",
        }

    async def _build_quality_report(self, project_id: str) -> dict:
        return {"projectId": project_id, "reportType": "quality", "sections": []}

    def _extract_nlq_intent(self, query: str) -> str:
        q = query.lower()
        if "项目" in q and ("状态" in q or "进度" in q):
            return "project_status"
        if "成本" in q or "费用" in q or "预算" in q:
            return "cost_summary"
        if "风险" in q:
            return "risk_overview"
        return "unknown"

    async def _query_project_status(self, query: str) -> dict:
        stmt = select(Project).limit(10)
        result = await self.db.execute(stmt)
        projects = result.scalars().all()
        return [
            {"projectId": p.project_id, "name": p.project_name, "status": p.status, "progress": p.progress}
            for p in projects
        ]

    async def _query_cost_summary(self) -> dict:
        total = await self.db.execute(select(func.sum(Project.budget)))
        return {"totalBudget": float(total.scalar() or 0)}

    async def _query_risk_overview(self) -> dict:
        stmt = select(func.count(ProjectRisk.risk_id)).where(ProjectRisk.status == "open")
        count = (await self.db.execute(stmt)).scalar() or 0
        return {"openRisks": count}

    def _extract_action_items(self, content: str) -> list[str]:
        """Simple action item extraction from meeting content."""
        items = []
        for line in content.split("\n"):
            line = line.strip()
            if any(marker in line for marker in ["待办", "TODO", "行动项", "负责人"]):
                items.append(line)
        return items

    def _extract_decisions(self, content: str) -> list[str]:
        decisions = []
        for line in content.split("\n"):
            line = line.strip()
            if any(marker in line for marker in ["决定", "决策", "通过", "确认"]):
                decisions.append(line)
        return decisions

    def _extract_key_points(self, content: str) -> list[str]:
        return [line.strip() for line in content.split("\n") if line.strip()][:10]

    # ── F-1212: Scenario Analysis ───────────────────────────────────

    async def assess_project_risk(self, req: dict) -> dict:
        """Comprehensive project risk assessment based on schedule, cost, resource."""
        project_id = req.get("project_id")
        project = await self._get_project(project_id)
        if not project:
            return {"projectId": project_id, "overallRisk": "unknown", "factors": []}

        factors = []
        cpi = float(project.evm_cpi or 1.0)
        spi = float(project.evm_spi or 1.0)
        progress = project.progress or 0

        # Cost risk
        if cpi < 0.9:
            factors.append({"factor": "cost", "risk": "high", "value": cpi, "reason": "CPI低于0.9，存在成本超支风险"})
        elif cpi < 1.0:
            factors.append({"factor": "cost", "risk": "medium", "value": cpi, "reason": "CPI略低于1.0，成本效率偏低"})
        else:
            factors.append({"factor": "cost", "risk": "low", "value": cpi, "reason": "成本控制在预期范围内"})

        # Schedule risk
        if spi < 0.85:
            factors.append({"factor": "schedule", "risk": "high", "value": spi, "reason": "SPI低于0.85，进度严重滞后"})
        elif spi < 1.0:
            factors.append({"factor": "schedule", "risk": "medium", "value": spi, "reason": "SPI略低于1.0，进度稍有延迟"})
        else:
            factors.append({"factor": "schedule", "risk": "low", "value": spi, "reason": "进度符合或超前计划"})

        # Resource risk (check for open risks count)
        risk_stmt = select(func.count(ProjectRisk.risk_id)).where(
            ProjectRisk.project_id == project_id, ProjectRisk.status == "open"
        )
        open_risks = (await self.db.execute(risk_stmt)).scalar() or 0
        if open_risks >= 5:
            factors.append({"factor": "resource", "risk": "high", "value": open_risks, "reason": "存在大量未关闭风险"})
        elif open_risks >= 2:
            factors.append({"factor": "resource", "risk": "medium", "value": open_risks, "reason": "存在若干未关闭风险"})
        else:
            factors.append({"factor": "resource", "risk": "low", "value": open_risks, "reason": "风险处于可控范围"})

        overall = "high" if any(f["risk"] == "high" for f in factors) else "medium" if any(f["risk"] == "medium" for f in factors) else "low"
        return {"projectId": project_id, "overallRisk": overall, "factors": factors}

    async def suggest_cost_optimization(self, req: dict) -> dict:
        """Suggest cost optimization strategies for a project."""
        project_id = req.get("project_id")
        project = await self._get_project(project_id)
        if not project:
            return {"projectId": project_id, "strategies": []}

        strategies = []
        cpi = float(project.evm_cpi or 1.0)
        budget = float(project.budget or 0)

        if cpi < 1.0:
            strategies.append({
                "strategy": "资源优化", "priority": "high",
                "description": "当前成本效率偏低，建议优化资源利用率，减少闲置资源",
                "expectedSaving": round(budget * 0.05, 2),
            })
        if budget > 1000000:
            strategies.append({
                "strategy": "采购优化", "priority": "medium",
                "description": "项目预算较大，建议采用集中采购降低单价成本",
                "expectedSaving": round(budget * 0.03, 2),
            })
        strategies.append({
            "strategy": "定期审计", "priority": "low",
            "description": "建议每月进行成本审计，及时发现偏差",
            "expectedSaving": None,
        })
        return {"projectId": project_id, "strategies": strategies, "currentCPI": cpi}

    async def suggest_schedule_optimization(self, req: dict) -> dict:
        """Suggest schedule improvements."""
        project_id = req.get("project_id")
        project = await self._get_project(project_id)
        if not project:
            return {"projectId": project_id, "suggestions": []}

        spi = float(project.evm_spi or 1.0)
        suggestions = []
        if spi < 0.9:
            suggestions.append({
                "suggestion": "关键路径压缩", "priority": "high",
                "description": "当前SPI严重偏低，建议识别关键路径任务并压缩工期",
            })
            suggestions.append({
                "suggestion": "并行任务识别", "priority": "high",
                "description": "分析WBS中可并行执行的任务，缩短整体工期",
            })
        elif spi < 1.0:
            suggestions.append({
                "suggestion": "资源补充", "priority": "medium",
                "description": "适度增加关键任务的资源投入",
            })
        return {"projectId": project_id, "suggestions": suggestions, "currentSPI": spi}

    async def recommend_resource_allocation(self, req: dict) -> dict:
        """Recommend optimal resource assignments."""
        project_id = req.get("project_id")
        required_skills = req.get("required_skills", [])
        from app.models.resource.models import OutsourcePerson
        stmt = select(OutsourcePerson).where(OutsourcePerson.pool_status == 0)
        result = await self.db.execute(stmt)
        available = result.scalars().all()

        recommendations = []
        for p in available:
            match_score = 0
            try:
                import json
                tags = json.loads(p.skill_tags) if p.skill_tags else []
                match_score = len(set(required_skills) & set(tags)) * 20
            except (json.JSONDecodeError, TypeError):
                pass
            if match_score > 0 or not required_skills:
                recommendations.append({
                    "personId": p.person_id, "name": p.name,
                    "level": p.level, "matchScore": min(match_score, 100),
                })
        recommendations.sort(key=lambda r: r["matchScore"], reverse=True)
        return {"projectId": project_id, "recommendations": recommendations[:10]}

    async def review_quality(self, req: dict) -> dict:
        """Review deliverable quality metrics."""
        from app.models.quality.models import QualityDefect as Defect
        project_id = req.get("project_id")
        stmt = select(func.count(Defect.defect_id)).where(Defect.project_id == project_id)
        total_defects = (await self.db.execute(stmt)).scalar() or 0
        open_stmt = select(func.count(Defect.defect_id)).where(
            Defect.project_id == project_id, Defect.status == "open"
        )
        open_defects = (await self.db.execute(open_stmt)).scalar() or 0

        quality_score = max(0, 100 - open_defects * 10 - total_defects * 2)
        return {
            "projectId": project_id,
            "qualityScore": quality_score,
            "totalDefects": total_defects,
            "openDefects": open_defects,
            "rating": "good" if quality_score >= 80 else "fair" if quality_score >= 60 else "poor",
        }

    async def forecast_progress(self, req: dict) -> dict:
        """Predict project completion date based on current progress and EVM."""
        project = await self._get_project(req.get("project_id"))
        if not project:
            return {"projectId": req.get("project_id"), "forecast": None}

        progress = project.progress or 0
        spi = float(project.evm_spi or 1.0)
        end_date = project.end_date
        if end_date:
            remaining_days = max(0, (end_date - datetime.utcnow().date()).days)
        else:
            remaining_days = 90

        if spi > 0:
            adjusted_remaining = int(remaining_days / spi)
        else:
            adjusted_remaining = remaining_days * 2

        forecast_completion = datetime.utcnow().date().isoformat()
        from datetime import timedelta
        forecast_date = datetime.utcnow().date() + timedelta(days=adjusted_remaining)
        forecast_completion = forecast_date.isoformat()

        return {
            "projectId": project.project_id,
            "currentProgress": progress,
            "currentSPI": spi,
            "originalEndDate": str(end_date) if end_date else None,
            "forecastedCompletionDate": forecast_completion,
            "delay": adjusted_remaining - remaining_days if end_date else None,
        }

    async def forecast_budget(self, req: dict) -> dict:
        """Predict final project cost."""
        project = await self._get_project(req.get("project_id"))
        if not project:
            return {"projectId": req.get("project_id"), "forecast": None}

        budget = float(project.budget or 0)
        cpi = float(project.evm_cpi or 1.0)

        if cpi > 0 and cpi != 1.0:
            forecasted_final = budget / cpi
        else:
            forecasted_final = budget

        variance = forecasted_final - budget
        variance_pct = (variance / budget * 100) if budget > 0 else 0

        return {
            "projectId": project.project_id,
            "originalBudget": round(budget, 2),
            "currentCPI": cpi,
            "forecastedFinalCost": round(forecasted_final, 2),
            "budgetVariance": round(variance, 2),
            "budgetVariancePct": round(variance_pct, 1),
        }
