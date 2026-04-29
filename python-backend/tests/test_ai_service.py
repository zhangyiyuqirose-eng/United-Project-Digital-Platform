"""Tests for app/services/ai_service.py — all methods with DB and pure logic."""

from __future__ import annotations

import json
from datetime import date, timedelta, timezone

import pytest

from app.models.business.models import Contract
from app.models.knowledge.models import KnowledgeDoc
from app.models.project.models import (
    PreInitiation, Project, ProjectClose, ProjectRisk, ProjectTask,
)
from app.models.quality.models import QualityDefect as Defect
from app.models.resource.models import OutsourcePerson
from app.models.timesheet.models import Timesheet
from app.services.ai_service import AIService


# ── Helper ──────────────────────────────────────────────────────────

async def _make_project(db, pid="proj-ai", **overrides):
    defaults = dict(
        project_id=pid,
        project_name="AI Test Project",
        project_code=f"AI-CODE-{pid}",
        status="active",
        progress=40,
        budget=500000.0,
        evm_cpi=1.05,
        evm_spi=0.98,
        end_date=date(2026, 12, 31),
    )
    defaults.update(overrides)
    p = Project(**defaults)
    db.add(p)
    await db.flush()
    return p


# ── F-1201: Smart Document Generation ───────────────────────────────

@pytest.mark.asyncio
async def test_generate_document(db_session):
    await _make_project(db_session)
    svc = AIService(db_session)
    result = await svc.generate_document({
        "project_id": "proj-ai",
        "document_type": "initiation",
        "template_id": "tpl-001",
    })
    assert result["documentType"] == "initiation"
    assert result["projectId"] == "proj-ai"
    assert "projectName" in result
    assert result["templateUsed"] == "tpl-001"


@pytest.mark.asyncio
async def test_generate_document_default_type(db_session):
    await _make_project(db_session)
    svc = AIService(db_session)
    result = await svc.generate_document({"project_id": "proj-ai"})
    assert result["documentType"] == "general"


@pytest.mark.asyncio
async def test_generate_document_not_found(db_session):
    svc = AIService(db_session)
    result = await svc.generate_document({"project_id": "nonexistent"})
    assert result["projectName"] == ""


# ── F-1202: Smart Report Generation ─────────────────────────────────

@pytest.mark.asyncio
async def test_generate_progress_report(db_session):
    await _make_project(db_session)
    svc = AIService(db_session)
    result = await svc.generate_report({
        "project_id": "proj-ai",
        "report_type": "progress",
    })
    assert result["reportType"] == "progress"
    assert "completedTasks" in result["data"]


@pytest.mark.asyncio
async def test_generate_cost_report(db_session):
    await _make_project(db_session, budget=200000.0, evm_cpi=0.95)
    svc = AIService(db_session)
    result = await svc.generate_report({
        "project_id": "proj-ai",
        "report_type": "cost",
    })
    assert result["reportType"] == "cost"
    assert result["data"]["budget"] == 200000.0


@pytest.mark.asyncio
async def test_generate_quality_report(db_session):
    await _make_project(db_session)
    svc = AIService(db_session)
    result = await svc.generate_report({
        "project_id": "proj-ai",
        "report_type": "quality",
    })
    assert result["reportType"] == "quality"


@pytest.mark.asyncio
async def test_generate_report_unknown_type(db_session):
    svc = AIService(db_session)
    result = await svc.generate_report({
        "project_id": "proj-ai",
        "report_type": "unknown_type",
    })
    assert result["reportType"] == "unknown_type"


# ── F-1203: Smart Risk Prediction ───────────────────────────────────

@pytest.mark.asyncio
async def test_predict_risks_cost_overrun(db_session):
    await _make_project(db_session, progress=20, evm_cpi=0.85)
    svc = AIService(db_session)
    result = await svc.predict_risks("proj-ai")
    types = [p["riskType"] for p in result["predictions"]]
    assert "cost_overrun" in types


@pytest.mark.asyncio
async def test_predict_risks_schedule_delay(db_session):
    await _make_project(db_session, evm_spi=0.80)
    svc = AIService(db_session)
    result = await svc.predict_risks("proj-ai")
    types = [p["riskType"] for p in result["predictions"]]
    assert "schedule_delay" in types


@pytest.mark.asyncio
async def test_predict_risks_accumulation(db_session):
    await _make_project(db_session, project_id="proj-accum")
    db_session.add_all([
        ProjectRisk(risk_id="risk-acc-1", project_id="proj-accum", risk_name="R1", status="open", probability=2, impact=2),
        ProjectRisk(risk_id="risk-acc-2", project_id="proj-accum", risk_name="R2", status="open", probability=2, impact=2),
        ProjectRisk(risk_id="risk-acc-3", project_id="proj-accum", risk_name="R3", status="open", probability=2, impact=2),
    ])
    await db_session.flush()
    svc = AIService(db_session)
    result = await svc.predict_risks("proj-accum")
    types = [p["riskType"] for p in result["predictions"]]
    assert "risk_accumulation" in types
    assert result["totalOpenRisks"] == 3


@pytest.mark.asyncio
async def test_predict_risks_no_predictions(db_session):
    await _make_project(db_session, progress=80, evm_cpi=1.1, evm_spi=1.05)
    svc = AIService(db_session)
    result = await svc.predict_risks("proj-ai")
    assert result["predictions"] == []


@pytest.mark.asyncio
async def test_predict_risks_not_found(db_session):
    svc = AIService(db_session)
    result = await svc.predict_risks("nonexistent")
    assert result["predictions"] == []


# ── F-1204: Natural Language Query ──────────────────────────────────

@pytest.mark.asyncio
async def test_nlq_project_status(db_session):
    await _make_project(db_session)
    svc = AIService(db_session)
    result = await svc.nlq_query({"query": "项目状态怎么样"})
    assert result["intent"] == "project_status"


@pytest.mark.asyncio
async def test_nlq_cost_summary(db_session):
    svc = AIService(db_session)
    result = await svc.nlq_query({"query": "成本预算汇总"})
    assert result["intent"] == "cost_summary"
    assert "totalBudget" in result["result"]


@pytest.mark.asyncio
async def test_nlq_risk_overview(db_session):
    svc = AIService(db_session)
    result = await svc.nlq_query({"query": "风险概览"})
    assert result["intent"] == "risk_overview"
    assert "openRisks" in result["result"]


@pytest.mark.asyncio
async def test_nlq_unknown_intent(db_session):
    svc = AIService(db_session)
    result = await svc.nlq_query({"query": "hello world"})
    assert result["intent"] == "unknown"


# ── F-1205: Meeting Minutes Extraction ──────────────────────────────

@pytest.mark.asyncio
async def test_summarize_meeting(db_session):
    svc = AIService(db_session)
    content = "会议决定通过方案A\n待办：张三完成设计\n确认预算为100万"
    result = await svc.summarize_meeting({"meeting_content": content, "meeting_type": "review"})
    assert result["meetingType"] == "review"
    assert len(result["decisions"]) >= 1
    assert len(result["actionItems"]) >= 1


@pytest.mark.asyncio
async def test_summarize_meeting_empty(db_session):
    svc = AIService(db_session)
    result = await svc.summarize_meeting({"meeting_content": ""})
    assert result["actionItems"] == []
    assert result["decisions"] == []


@pytest.mark.asyncio
async def test_summarize_meeting_truncation(db_session):
    svc = AIService(db_session)
    long_content = "A\n" * 600
    result = await svc.summarize_meeting({"meeting_content": long_content})
    assert len(result["summary"]) <= 500


# ── F-1206: Smart Approval Suggestions ──────────────────────────────

@pytest.mark.asyncio
async def test_approval_suggest(db_session):
    svc = AIService(db_session)
    result = await svc.approval_suggest("process-001")
    assert result["processId"] == "process-001"
    assert result["suggestion"] == "review"
    assert result["confidence"] == 0.6
    assert len(result["checklist"]) == 3


# ── F-1207: Smart WBS Recommendation ────────────────────────────────

@pytest.mark.asyncio
async def test_recommend_wbs_software(db_session):
    svc = AIService(db_session)
    result = await svc.recommend_wbs("software", "My Project")
    assert result["projectType"] == "software"
    assert result["projectName"] == "My Project"
    assert result["recommendedPhases"] == 5
    assert len(result["wbsStructure"]) == 5


@pytest.mark.asyncio
async def test_recommend_wbs_infrastructure(db_session):
    svc = AIService(db_session)
    result = await svc.recommend_wbs("infrastructure")
    assert result["recommendedPhases"] == 5


@pytest.mark.asyncio
async def test_recommend_wbs_consulting(db_session):
    svc = AIService(db_session)
    result = await svc.recommend_wbs("consulting")
    assert result["recommendedPhases"] == 5


@pytest.mark.asyncio
async def test_recommend_wbs_default(db_session):
    svc = AIService(db_session)
    result = await svc.recommend_wbs("unknown_type")
    # Falls back to software template
    assert result["recommendedPhases"] == 5


# ── F-1208: Smart Timesheet Forecast ────────────────────────────────

@pytest.mark.asyncio
async def test_forecast_timesheet_with_data(db_session):
    await _make_project(db_session, project_id="proj-ts")
    db_session.add(Timesheet(
        timesheet_id="ts-1", project_id="proj-ts", staff_id="u1", hours=6.0,
    ))
    db_session.add(Timesheet(
        timesheet_id="ts-2", project_id="proj-ts", staff_id="u1", hours=10.0,
    ))
    await db_session.flush()
    svc = AIService(db_session)
    result = await svc.forecast_timesheet("proj-ts", "u1")
    assert result["projectId"] == "proj-ts"
    assert result["averageDailyHours"] == 8.0


@pytest.mark.asyncio
async def test_forecast_timesheet_empty(db_session):
    await _make_project(db_session, project_id="proj-ts2")
    svc = AIService(db_session)
    result = await svc.forecast_timesheet("proj-ts2")
    assert result["averageDailyHours"] == 8.0  # default
    assert result["totalLoggedHours"] == 0.0


# ── F-1209: Smart Knowledge Retrieval ───────────────────────────────

@pytest.mark.asyncio
async def test_search_knowledge(db_session):
    db_session.add_all([
        KnowledgeDoc(doc_id="doc-1", title="Python Guide", doc_type="guide", status="published", category="python"),
        KnowledgeDoc(doc_id="doc-2", title="Java Guide", doc_type="guide", status="published", category="java"),
        KnowledgeDoc(doc_id="doc-3", title="Draft Doc", doc_type="draft", status="draft"),
    ])
    await db_session.flush()
    svc = AIService(db_session)
    result = await svc.search_knowledge({"query": "Python", "top_k": 10})
    assert result["totalMatches"] >= 1
    assert any(r["docName"] == "Python Guide" for r in result["results"])


@pytest.mark.asyncio
async def test_search_knowledge_by_category(db_session):
    db_session.add_all([
        KnowledgeDoc(doc_id="doc-cat-1", title="Cat Doc", doc_type="template", status="published"),
    ])
    await db_session.flush()
    svc = AIService(db_session)
    result = await svc.search_knowledge({"category": "template"})
    assert result["totalMatches"] >= 1


@pytest.mark.asyncio
async def test_search_knowledge_empty(db_session):
    svc = AIService(db_session)
    result = await svc.search_knowledge({"query": ""})
    assert result["totalMatches"] == 0


# ── F-1210: Smart Compliance Check ──────────────────────────────────

@pytest.mark.asyncio
async def test_compliance_check_pass(db_session):
    await _make_project(db_session, project_id="proj-comp")
    db_session.add(PreInitiation(
        pre_id="pre-1", project_id="proj-comp", feasibility_study="Feasible",
    ))
    await db_session.flush()
    svc = AIService(db_session)
    # With default check_type="all", closeout check is included and returns "pending"
    result = await svc.compliance_check({"project_id": "proj-comp", "check_type": "general"})
    assert result["overall"] == "pass"


@pytest.mark.asyncio
async def test_compliance_check_fail(db_session):
    await _make_project(db_session, project_id="proj-comp2")
    svc = AIService(db_session)
    result = await svc.compliance_check({"project_id": "proj-comp2"})
    assert result["overall"] == "fail"


@pytest.mark.asyncio
async def test_compliance_check_closeout(db_session):
    await _make_project(db_session, project_id="proj-comp3")
    db_session.add(PreInitiation(
        pre_id="pre-3", project_id="proj-comp3", feasibility_study="Feasible",
    ))
    db_session.add(ProjectClose(
        close_id="close-1", project_id="proj-comp3", close_type="normal",
    ))
    await db_session.flush()
    svc = AIService(db_session)
    result = await svc.compliance_check({"project_id": "proj-comp3", "check_type": "closeout"})
    assert result["overall"] == "pass"


@pytest.mark.asyncio
async def test_compliance_check_no_project(db_session):
    svc = AIService(db_session)
    result = await svc.compliance_check({"project_id": "nonexistent"})
    assert result["projectName"] == ""


# ── F-1211: Smart Data Insights ─────────────────────────────────────

@pytest.mark.asyncio
async def test_data_insights_project_scope(db_session):
    await _make_project(db_session, project_id="proj-di1", progress=30)
    svc = AIService(db_session)
    result = await svc.data_insights({"scope": "project", "project_ids": ["proj-di1"]})
    assert len(result["insights"]) >= 1
    assert result["analyzedProjects"] == 1


@pytest.mark.asyncio
async def test_data_insights_cpi(db_session):
    await _make_project(db_session, project_id="proj-di2", evm_cpi=0.85)
    svc = AIService(db_session)
    result = await svc.data_insights({"scope": "project", "project_ids": ["proj-di2"]})
    severities = [i["severity"] for i in result["insights"]]
    assert "high" in severities


@pytest.mark.asyncio
async def test_data_insights_portfolio(db_session):
    svc = AIService(db_session)
    result = await svc.data_insights({"scope": "portfolio"})
    assert len(result["insights"]) >= 1
    assert "scope" in result


# ── F-1212: Scenario Analysis ───────────────────────────────────────

@pytest.mark.asyncio
async def test_assess_project_risk_low(db_session):
    await _make_project(db_session, evm_cpi=1.1, evm_spi=1.05, project_id="proj-ar-low")
    svc = AIService(db_session)
    result = await svc.assess_project_risk({"project_id": "proj-ar-low"})
    assert result["overallRisk"] == "low"
    assert len(result["factors"]) == 3  # cost, schedule, resource


@pytest.mark.asyncio
async def test_assess_project_risk_high_cost(db_session):
    await _make_project(db_session, evm_cpi=0.85, project_id="proj-ar-hc")
    svc = AIService(db_session)
    result = await svc.assess_project_risk({"project_id": "proj-ar-hc"})
    assert result["overallRisk"] == "high"
    cost_factor = next(f for f in result["factors"] if f["factor"] == "cost")
    assert cost_factor["risk"] == "high"


@pytest.mark.asyncio
async def test_assess_project_risk_high_schedule(db_session):
    await _make_project(db_session, evm_spi=0.80, project_id="proj-ar-hs")
    svc = AIService(db_session)
    result = await svc.assess_project_risk({"project_id": "proj-ar-hs"})
    assert result["overallRisk"] == "high"


@pytest.mark.asyncio
async def test_assess_project_risk_medium(db_session):
    await _make_project(db_session, evm_cpi=0.95, evm_spi=0.95, project_id="proj-ar-med")
    svc = AIService(db_session)
    result = await svc.assess_project_risk({"project_id": "proj-ar-med"})
    assert result["overallRisk"] == "medium"


@pytest.mark.asyncio
async def test_assess_project_risk_not_found(db_session):
    svc = AIService(db_session)
    result = await svc.assess_project_risk({"project_id": "nonexistent"})
    assert result["overallRisk"] == "unknown"


@pytest.mark.asyncio
async def test_suggest_cost_optimization_cpi_low(db_session):
    await _make_project(db_session, evm_cpi=0.90, budget=2000000.0, project_id="proj-co")
    svc = AIService(db_session)
    result = await svc.suggest_cost_optimization({"project_id": "proj-co"})
    assert len(result["strategies"]) >= 2
    assert result["currentCPI"] == 0.90


@pytest.mark.asyncio
async def test_suggest_cost_optimization_good(db_session):
    await _make_project(db_session, evm_cpi=1.1, project_id="proj-co-good")
    svc = AIService(db_session)
    result = await svc.suggest_cost_optimization({"project_id": "proj-co-good"})
    # Only the default "定期审计" strategy
    assert len(result["strategies"]) == 1


@pytest.mark.asyncio
async def test_suggest_cost_optimization_not_found(db_session):
    svc = AIService(db_session)
    result = await svc.suggest_cost_optimization({"project_id": "nonexistent"})
    assert result["strategies"] == []


@pytest.mark.asyncio
async def test_suggest_schedule_optimization_high(db_session):
    await _make_project(db_session, evm_spi=0.85, project_id="proj-so")
    svc = AIService(db_session)
    result = await svc.suggest_schedule_optimization({"project_id": "proj-so"})
    assert len(result["suggestions"]) >= 2


@pytest.mark.asyncio
async def test_suggest_schedule_optimization_medium(db_session):
    await _make_project(db_session, evm_spi=0.95, project_id="proj-so-med")
    svc = AIService(db_session)
    result = await svc.suggest_schedule_optimization({"project_id": "proj-so-med"})
    assert len(result["suggestions"]) >= 1


@pytest.mark.asyncio
async def test_suggest_schedule_optimization_good(db_session):
    await _make_project(db_session, evm_spi=1.05, project_id="proj-so-good")
    svc = AIService(db_session)
    result = await svc.suggest_schedule_optimization({"project_id": "proj-so-good"})
    assert result["suggestions"] == []


@pytest.mark.asyncio
async def test_suggest_schedule_not_found(db_session):
    svc = AIService(db_session)
    result = await svc.suggest_schedule_optimization({"project_id": "nonexistent"})
    assert result["suggestions"] == []


@pytest.mark.asyncio
async def test_recommend_resource_allocation(db_session):
    db_session.add(OutsourcePerson(
        person_id="person-1", name="Alice", emp_code="EMP001", id_card="110101199001011234",
        skill_tags=json.dumps(["python", "fastapi", "sql"]),
        pool_status=0, level=3, daily_rate=1000.0,
    ))
    db_session.add(OutsourcePerson(
        person_id="person-2", name="Bob", emp_code="EMP002", id_card="110101199001011235",
        skill_tags=json.dumps(["java"]),
        pool_status=0, level=2, daily_rate=800.0,
    ))
    await db_session.flush()
    svc = AIService(db_session)
    result = await svc.recommend_resource_allocation({
        "project_id": "proj-ra",
        "required_skills": ["python", "fastapi"],
    })
    assert len(result["recommendations"]) >= 1
    assert result["recommendations"][0]["matchScore"] > 0


@pytest.mark.asyncio
async def test_recommend_resource_allocation_no_skills_filter(db_session):
    db_session.add(OutsourcePerson(
        person_id="person-3", name="Charlie", emp_code="EMP003", id_card="110101199001011236",
        pool_status=0, level=2, daily_rate=600.0,
    ))
    await db_session.flush()
    svc = AIService(db_session)
    result = await svc.recommend_resource_allocation({"project_id": "proj-ra2"})
    # Without required_skills, all available persons match
    assert len(result["recommendations"]) >= 1


@pytest.mark.asyncio
async def test_recommend_resource_allocation_invalid_json(db_session):
    db_session.add(OutsourcePerson(
        person_id="person-4", name="Dave", emp_code="EMP004", id_card="110101199001011237",
        skill_tags="not-valid-json", pool_status=0, level=3, daily_rate=1200.0,
    ))
    await db_session.flush()
    svc = AIService(db_session)
    result = await svc.recommend_resource_allocation({
        "project_id": "proj-ra3",
        "required_skills": ["python"],
    })
    assert isinstance(result["recommendations"], list)


@pytest.mark.asyncio
async def test_review_quality(db_session):
    await _make_project(db_session, project_id="proj-qr")
    svc = AIService(db_session)
    result = await svc.review_quality({"project_id": "proj-qr"})
    assert result["qualityScore"] == 100  # no defects
    assert result["rating"] == "good"


@pytest.mark.asyncio
async def test_review_quality_with_defects(db_session):
    await _make_project(db_session, project_id="proj-qr2")
    db_session.add_all([
        Defect(defect_id="def-1", project_id="proj-qr2", defect_name="High severity bug", severity="high", status="open"),
        Defect(defect_id="def-2", project_id="proj-qr2", defect_name="Low severity bug", severity="low", status="closed"),
        Defect(defect_id="def-3", project_id="proj-qr2", defect_name="Medium severity bug", severity="medium", status="open"),
    ])
    await db_session.flush()
    svc = AIService(db_session)
    result = await svc.review_quality({"project_id": "proj-qr2"})
    assert result["totalDefects"] == 3
    assert result["openDefects"] == 2
    assert result["qualityScore"] == 74  # 100 - 2*10 - 3*2 = 74


@pytest.mark.asyncio
async def test_review_quality_poor(db_session):
    await _make_project(db_session, project_id="proj-qr3")
    for i in range(10):
        db_session.add(Defect(
            defect_id=f"def-poor-{i}", project_id="proj-qr3",
            defect_name=f"Bug {i}", severity="high", status="open",
        ))
    await db_session.flush()
    svc = AIService(db_session)
    result = await svc.review_quality({"project_id": "proj-qr3"})
    assert result["rating"] == "poor"


@pytest.mark.asyncio
async def test_forecast_progress(db_session):
    future = date.today() + timedelta(days=90)
    await _make_project(db_session, progress=50, evm_spi=1.0,
                         end_date=future, project_id="proj-fp")
    svc = AIService(db_session)
    result = await svc.forecast_progress({"project_id": "proj-fp"})
    assert result["currentProgress"] == 50
    assert result["currentSPI"] == 1.0
    assert result["originalEndDate"] is not None


@pytest.mark.asyncio
async def test_forecast_progress_delayed(db_session):
    future = date.today() + timedelta(days=90)
    await _make_project(db_session, progress=30, evm_spi=0.5,
                         end_date=future, project_id="proj-fp-delayed")
    svc = AIService(db_session)
    result = await svc.forecast_progress({"project_id": "proj-fp-delayed"})
    assert result["delay"] > 0  # delayed


@pytest.mark.asyncio
async def test_forecast_progress_not_found(db_session):
    svc = AIService(db_session)
    result = await svc.forecast_progress({"project_id": "nonexistent"})
    assert result["forecast"] is None


@pytest.mark.asyncio
async def test_forecast_budget(db_session):
    await _make_project(db_session, budget=100000.0, evm_cpi=0.8, project_id="proj-fb")
    svc = AIService(db_session)
    result = await svc.forecast_budget({"project_id": "proj-fb"})
    assert result["originalBudget"] == 100000.0
    assert result["currentCPI"] == 0.8
    assert result["forecastedFinalCost"] > 100000.0  # CPI < 1 means overrun


@pytest.mark.asyncio
async def test_forecast_budget_good_cpi(db_session):
    await _make_project(db_session, budget=100000.0, evm_cpi=1.2, project_id="proj-fb-good")
    svc = AIService(db_session)
    result = await svc.forecast_budget({"project_id": "proj-fb-good"})
    assert result["forecastedFinalCost"] < 100000.0  # CPI > 1 means under budget


@pytest.mark.asyncio
async def test_forecast_budget_not_found(db_session):
    svc = AIService(db_session)
    result = await svc.forecast_budget({"project_id": "nonexistent"})
    assert result["forecast"] is None
