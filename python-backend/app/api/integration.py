"""External system integration API endpoints."""

from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.schemas import ApiResponse
from app.dependencies import get_current_user
from app.integrations.devops_adapter import DevOpsAdapter
from app.integrations.finance_adapter import FinanceAdapter
from app.integrations.hr_adapter import HrAdapter

router = APIRouter(tags=["integration"])

_hr = HrAdapter()
_finance = FinanceAdapter()
_devops = DevOpsAdapter()


@router.get("/hr/employee/{employee_id}")
async def get_employee_info(
    employee_id: str,
    current_user: dict = Depends(get_current_user),
):
    data = await _hr.get_employee_info(employee_id)
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.post("/hr/sync-org")
async def sync_org_structure(
    current_user: dict = Depends(get_current_user),
):
    data = await _hr.sync_org_structure()
    return ApiResponse(code="SUCCESS", message="success", data={"message": "同步请求已发送", **data})


class SettlementPushRequest(BaseModel):
    projectId: str
    amount: Decimal


@router.post("/finance/settlement")
async def push_settlement(
    req: SettlementPushRequest,
    current_user: dict = Depends(get_current_user),
):
    data = await _finance.push_settlement(req.projectId, req.amount)
    return ApiResponse(code="SUCCESS", message="success", data={"message": "结算推送已发送", **data})


@router.get("/finance/payment/{settlement_id}")
async def query_payment_status(
    settlement_id: str,
    current_user: dict = Depends(get_current_user),
):
    data = await _finance.query_payment_status(settlement_id)
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.get("/devops/build/{project_id}")
async def get_build_status(
    project_id: str,
    current_user: dict = Depends(get_current_user),
):
    data = await _devops.get_build_status(project_id)
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.get("/devops/test/{project_id}")
async def get_test_results(
    project_id: str,
    current_user: dict = Depends(get_current_user),
):
    data = await _devops.get_test_results(project_id)
    return ApiResponse(code="SUCCESS", message="success", data=data)
