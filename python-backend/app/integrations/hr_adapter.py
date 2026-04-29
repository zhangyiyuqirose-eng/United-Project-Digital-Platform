"""HR system adapter — fetches employee info and syncs org structure."""

from __future__ import annotations

import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class HrAdapter:
    def __init__(self, base_url: str | None = None, timeout: float = 10.0) -> None:
        self.base_url = base_url or getattr(settings, "hr_system_url", "")
        self.timeout = timeout

    async def get_employee_info(self, employee_id: str) -> dict:
        if not self.base_url:
            return self._mock_employee(employee_id)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(f"{self.base_url}/api/employee/{employee_id}")
                resp.raise_for_status()
                return resp.json()
        except httpx.HTTPError:
            logger.warning("HR system unavailable, returning mock data for %s", employee_id)
            return self._mock_employee(employee_id)

    async def sync_org_structure(self) -> dict:
        if not self.base_url:
            return self._mock_sync_result()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(f"{self.base_url}/api/org/sync")
                resp.raise_for_status()
                return resp.json()
        except httpx.HTTPError:
            logger.warning("HR system unavailable, returning mock sync result")
            return self._mock_sync_result()

    @staticmethod
    def _mock_employee(employee_id: str) -> dict:
        return {
            "employeeId": employee_id,
            "name": f"Employee {employee_id}",
            "department": "Engineering",
            "position": "Software Engineer",
            "status": "active",
        }

    @staticmethod
    def _mock_sync_result() -> dict:
        return {"synced": True, "orgCount": 12, "staffCount": 156}
