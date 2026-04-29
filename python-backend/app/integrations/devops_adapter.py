"""DevOps system adapter — fetches build status and test results."""

from __future__ import annotations

import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class DevOpsAdapter:
    def __init__(self, base_url: str | None = None, timeout: float = 10.0) -> None:
        self.base_url = base_url or getattr(settings, "devops_system_url", "")
        self.timeout = timeout

    async def get_build_status(self, project_id: str) -> dict:
        if not self.base_url:
            return self._mock_build_status(project_id)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(
                    f"{self.base_url}/api/build/{project_id}"
                )
                resp.raise_for_status()
                return resp.json()
        except httpx.HTTPError:
            logger.warning(
                "DevOps system unavailable, returning mock build for %s", project_id
            )
            return self._mock_build_status(project_id)

    async def get_test_results(self, project_id: str) -> dict:
        if not self.base_url:
            return self._mock_test_results(project_id)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(
                    f"{self.base_url}/api/test/{project_id}"
                )
                resp.raise_for_status()
                return resp.json()
        except httpx.HTTPError:
            logger.warning(
                "DevOps system unavailable, returning mock test for %s", project_id
            )
            return self._mock_test_results(project_id)

    @staticmethod
    def _mock_build_status(project_id: str) -> dict:
        return {
            "projectId": project_id,
            "buildNumber": 42,
            "status": "success",
            "duration": 180,
            "lastBuiltAt": "2026-04-28T10:00:00Z",
        }

    @staticmethod
    def _mock_test_results(project_id: str) -> dict:
        return {
            "projectId": project_id,
            "total": 156,
            "passed": 150,
            "failed": 4,
            "skipped": 2,
            "coverage": 82.5,
        }
