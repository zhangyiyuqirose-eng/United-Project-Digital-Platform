"""Tests for core schemas: ApiResponse, PageResult, ErrorCode."""

import time

from app.core.schemas import ApiResponse, ErrorCode, PageResult


def test_api_response_success():
    resp = ApiResponse(code="SUCCESS", message="操作成功", data={"key": "value"})
    d = resp.model_dump()
    assert d["code"] == "SUCCESS"
    assert d["message"] == "操作成功"
    assert d["data"] == {"key": "value"}
    assert isinstance(d["timestamp"], int)


def test_api_response_error():
    resp = ApiResponse(code="NOT_FOUND", message="资源不存在", data=None)
    assert resp.code == "NOT_FOUND"
    assert resp.data is None


def test_api_response_timestamp():
    before = int(time.time() * 1000)
    resp = ApiResponse(code="SUCCESS", message="ok")
    after = int(time.time() * 1000)
    assert before <= resp.timestamp <= after


def test_page_result():
    pr = PageResult(total=100, page=1, size=10, records=[{"id": 1}, {"id": 2}])
    d = pr.model_dump()
    assert d["total"] == 100
    assert d["page"] == 1
    assert d["size"] == 10
    assert len(d["records"]) == 2


def test_error_codes():
    assert ErrorCode.SUCCESS == "SUCCESS"
    assert ErrorCode.PARAM_ERROR == "PARAM_ERROR"
    assert ErrorCode.NOT_FOUND == "NOT_FOUND"
    assert ErrorCode.SYSTEM_ERROR == "SYSTEM_ERROR"
