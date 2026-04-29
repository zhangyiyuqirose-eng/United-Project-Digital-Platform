"""AI Digital Employee API router — 11 F-12xx requirements."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas import ApiResponse
from app.database import get_db
from app.dependencies import get_current_user
from app.services.ai_service import AIService
from app.services.llm_client import OpenAICompatibleClient, ResilientLlmClient, RuleBasedClient
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["ai"])


async def get_ai_service(db: AsyncSession = Depends(get_db)) -> AIService:
    """FastAPI dependency: create AIService with real LLM integration.

    Uses Finna (Minimax M2.7) when FINNA_API_KEY is configured.
    Falls back to rule-based engine when no API key is available.
    """
    api_key = settings.finna_api_key
    if api_key:
        primary = OpenAICompatibleClient(
            api_key=api_key,
            base_url=settings.finna_api_url,
            model=settings.finna_api_model,
        )
        fallback = RuleBasedClient(None)
        llm = ResilientLlmClient(primary, fallback)
        logger.info("AI service using %s @ %s", settings.finna_api_model, settings.finna_api_url)
    else:
        llm = None  # AIService will default to RuleBasedClient

    return AIService(db, llm_client=llm)


# ── F-1201: Smart Document Generation ───────────────────────────────

@router.post("/document/generate")
async def generate_document(req: DocumentGenerateRequest, service: AIService = Depends(get_ai_service)):
    """智能文档生成: 基于模板和上下文自动生成项目文档."""
    result = await service.generate_document(req.model_dump())
    return ApiResponse(code="SUCCESS", message="success", data=result)


# ── F-1202: Smart Report Generation ─────────────────────────────────

@router.post("/report/generate")
async def generate_report(req: ReportGenerateRequest, service: AIService = Depends(get_ai_service)):
    """智能报告生成: 自动生成项目进度/成本/质量报告."""
    result = await service.generate_report(req.model_dump())
    return ApiResponse(code="SUCCESS", message="success", data=result)


# ── F-1203: Smart Risk Prediction ───────────────────────────────────

@router.post("/risk/predict")
async def predict_risks(project_id: str, service: AIService = Depends(get_ai_service)):
    """智能风险预测: 基于历史数据和当前指标预测项目风险."""
    result = await service.predict_risks(project_id)
    return ApiResponse(code="SUCCESS", message="success", data=result)


# ── F-1204: Natural Language Query (NLQ) ────────────────────────────

@router.post("/nlq/query")
async def nlq_query(req: NLQRequest, service: AIService = Depends(get_ai_service)):
    """自然语言数据查询: 用自然语言查询项目数据."""
    result = await service.nlq_query(req.model_dump())
    return ApiResponse(code="SUCCESS", message="success", data=result)


# ── F-1205: Meeting Minutes Extraction ──────────────────────────────

@router.post("/meeting/summarize")
async def summarize_meeting(req: MeetingSummarizeRequest, service: AIService = Depends(get_ai_service)):
    """会议纪要提取: 从会议记录中自动提取关键信息和行动项."""
    result = await service.summarize_meeting(req.model_dump())
    return ApiResponse(code="SUCCESS", message="success", data=result)


# ── F-1206: Smart Approval Suggestions ──────────────────────────────

@router.post("/approval/suggest")
async def approval_suggest(process_id: str, service: AIService = Depends(get_ai_service)):
    """智能审批建议: 基于审批材料和历史记录生成审批建议."""
    result = await service.approval_suggest(process_id)
    return ApiResponse(code="SUCCESS", message="success", data=result)


# ── F-1207: Smart WBS Recommendation ────────────────────────────────

@router.post("/wbs/recommend")
async def recommend_wbs(project_type: str, project_name: Optional[str] = None, service: AIService = Depends(get_ai_service)):
    """智能WBS推荐: 基于项目类型和历史项目推荐WBS结构."""
    result = await service.recommend_wbs(project_type, project_name)
    return ApiResponse(code="SUCCESS", message="success", data=result)


# ── F-1208: Smart Timesheet Forecast ────────────────────────────────

@router.post("/timesheet/forecast")
async def forecast_timesheet(project_id: str, user_id: Optional[str] = None, service: AIService = Depends(get_ai_service)):
    """智能工时预测: 基于历史工时数据预测未来工时需求."""
    result = await service.forecast_timesheet(project_id, user_id)
    return ApiResponse(code="SUCCESS", message="success", data=result)


# ── F-1209: Smart Knowledge Retrieval ───────────────────────────────

@router.post("/knowledge/search")
async def search_knowledge(req: KnowledgeSearchRequest, service: AIService = Depends(get_ai_service)):
    """智能知识检索: 基于语义搜索的知识库检索."""
    result = await service.search_knowledge(req.model_dump())
    return ApiResponse(code="SUCCESS", message="success", data=result)


# ── F-1210: Smart Compliance Check ──────────────────────────────────

@router.post("/compliance/check")
async def compliance_check(req: ComplianceCheckRequest, service: AIService = Depends(get_ai_service)):
    """智能合规检查: 自动检查项目文档和流程的合规性."""
    result = await service.compliance_check(req.model_dump())
    return ApiResponse(code="SUCCESS", message="success", data=result)


# ── F-1211: Smart Data Insights ─────────────────────────────────────

@router.post("/insights/query")
async def data_insights(req: InsightsRequest, service: AIService = Depends(get_ai_service)):
    """智能数据洞察: 基于数据分析生成洞察报告."""
    result = await service.data_insights(req.model_dump())
    return ApiResponse(code="SUCCESS", message="success", data=result)


# ── Health check ────────────────────────────────────────────────────

@router.get("/health")
async def ai_health():
    return {"status": "ok", "service": "ai"}


# ── F-1212: AI Scenario Analysis ────────────────────────────────────

@router.get("/scenario")
async def list_scenarios(service: AIService = Depends(get_ai_service)):
    """List all available AI scenarios."""
    scenarios = [
        {"key": "project-risk-assessment", "name": "项目风险评估",
         "description": "基于进度、成本、资源等多维度进行项目风险综合评估"},
        {"key": "cost-optimization", "name": "成本优化建议",
         "description": "分析项目成本结构，提供成本优化策略"},
        {"key": "schedule-optimization", "name": "进度优化建议",
         "description": "基于关键路径分析提供进度优化方案"},
        {"key": "resource-allocation", "name": "资源分配推荐",
         "description": "基于技能和可用性推荐最优资源分配"},
        {"key": "quality-review", "name": "质量评审",
         "description": "评审交付物质量指标，识别质量问题"},
        {"key": "progress-forecast", "name": "进度预测",
         "description": "基于当前进度和EVM指标预测项目完成日期"},
        {"key": "budget-forecast", "name": "预算预测",
         "description": "预测项目最终成本和预算偏差"},
        {"key": "compliance-check", "name": "合规检查",
         "description": "自动检查项目文档和流程合规性"},
    ]
    return ApiResponse(code="SUCCESS", message="success", data={"scenarios": scenarios})


@router.post("/scenario/project-risk-assessment")
async def scenario_project_risk_assessment(req: ScenarioProjectRiskRequest, service: AIService = Depends(get_ai_service)):
    """Assess project risk based on schedule, cost, resource."""
    result = await service.assess_project_risk(req.model_dump())
    return ApiResponse(code="SUCCESS", message="success", data=result)


@router.post("/scenario/cost-optimization")
async def scenario_cost_optimization(req: ScenarioProjectRequest, service: AIService = Depends(get_ai_service)):
    """Suggest cost optimization strategies."""
    result = await service.suggest_cost_optimization(req.model_dump())
    return ApiResponse(code="SUCCESS", message="success", data=result)


@router.post("/scenario/schedule-optimization")
async def scenario_schedule_optimization(req: ScenarioProjectRequest, service: AIService = Depends(get_ai_service)):
    """Suggest schedule improvements."""
    result = await service.suggest_schedule_optimization(req.model_dump())
    return ApiResponse(code="SUCCESS", message="success", data=result)


@router.post("/scenario/resource-allocation")
async def scenario_resource_allocation(req: ScenarioResourceRequest, service: AIService = Depends(get_ai_service)):
    """Recommend optimal resource assignments."""
    result = await service.recommend_resource_allocation(req.model_dump())
    return ApiResponse(code="SUCCESS", message="success", data=result)


@router.post("/scenario/quality-review")
async def scenario_quality_review(req: ScenarioQualityRequest, service: AIService = Depends(get_ai_service)):
    """Review deliverable quality metrics."""
    result = await service.review_quality(req.model_dump())
    return ApiResponse(code="SUCCESS", message="success", data=result)


@router.post("/scenario/progress-forecast")
async def scenario_progress_forecast(req: ScenarioProjectRequest, service: AIService = Depends(get_ai_service)):
    """Predict project completion date."""
    result = await service.forecast_progress(req.model_dump())
    return ApiResponse(code="SUCCESS", message="success", data=result)


@router.post("/scenario/budget-forecast")
async def scenario_budget_forecast(req: ScenarioProjectRequest, service: AIService = Depends(get_ai_service)):
    """Predict final project cost."""
    result = await service.forecast_budget(req.model_dump())
    return ApiResponse(code="SUCCESS", message="success", data=result)


# ── Request schemas ─────────────────────────────────────────────────

class DocumentGenerateRequest(BaseModel):
    project_id: str
    document_type: str  # initiation, proposal, summary, etc.
    template_id: str | None = None
    extra_context: dict | None = None

class ReportGenerateRequest(BaseModel):
    project_id: str
    report_type: str  # progress, cost, quality, etc.
    period_start: str | None = None
    period_end: str | None = None

class NLQRequest(BaseModel):
    query: str
    context: dict | None = None

class MeetingSummarizeRequest(BaseModel):
    meeting_content: str
    meeting_type: str | None = None
    project_id: str | None = None

class KnowledgeSearchRequest(BaseModel):
    query: str
    category: str | None = None
    top_k: int = 10

class ComplianceCheckRequest(BaseModel):
    project_id: str
    check_type: str | None = None  # initiation, change, closeout
    document_ids: list[str] | None = None

class InsightsRequest(BaseModel):
    scope: str  # project, portfolio, resource
    focus: str | None = None  # cost, schedule, quality, risk
    project_ids: list[str] | None = None

class ScenarioProjectRequest(BaseModel):
    project_id: str

class ScenarioProjectRiskRequest(BaseModel):
    project_id: str
    schedule_score: float | None = None
    cost_score: float | None = None
    resource_score: float | None = None

class ScenarioResourceRequest(BaseModel):
    project_id: str
    required_skills: list[str] | None = None
    head_count: int | None = None

class ScenarioQualityRequest(BaseModel):
    project_id: str
    deliverable_type: str | None = None
    metrics: dict | None = None
