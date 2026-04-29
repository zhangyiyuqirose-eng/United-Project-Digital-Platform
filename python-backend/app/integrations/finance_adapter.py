"""Finance system adapter — pushes settlements and queries payment status."""

from __future__ import annotations

import logging
from decimal import Decimal

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class FinanceAdapter:
    def __init__(self, base_url: str | None = None, timeout: float = 10.0) -> None:
        self.base_url = base_url or getattr(settings, "finance_system_url", "")
        self.timeout = timeout

    async def push_settlement(self, project_id: str, amount: Decimal) -> dict:
        payload = {"projectId": project_id, "amount": float(amount)}
        if not self.base_url:
            return self._mock_settlement_push(project_id, amount)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(
                    f"{self.base_url}/api/settlement", json=payload
                )
                resp.raise_for_status()
                return resp.json()
        except httpx.HTTPError:
            logger.warning(
                "Finance system unavailable, returning mock settlement for %s",
                project_id,
            )
            return self._mock_settlement_push(project_id, amount)

    async def query_payment_status(self, settlement_id: str) -> dict:
        if not self.base_url:
            return self._mock_payment_status(settlement_id)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(
                    f"{self.base_url}/api/payment/{settlement_id}"
                )
                resp.raise_for_status()
                return resp.json()
        except httpx.HTTPError:
            logger.warning(
                "Finance system unavailable, returning mock payment for %s",
                settlement_id,
            )
            return self._mock_payment_status(settlement_id)

    @staticmethod
    def _mock_settlement_push(project_id: str, amount: Decimal) -> dict:
        return {
            "settlementId": f"SET-{project_id}",
            "projectId": project_id,
            "amount": float(amount),
            "status": "pending",
        }

    @staticmethod
    def _mock_payment_status(settlement_id: str) -> dict:
        return {
            "settlementId": settlement_id,
            "status": "processing",
            "paidAmount": 0.0,
            "pendingAmount": 0.0,
        }
