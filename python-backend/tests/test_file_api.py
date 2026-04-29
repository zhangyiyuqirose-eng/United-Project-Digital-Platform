"""Tests for file API endpoints with mocked MinIO."""

import pytest
from datetime import datetime, timezone
from io import BytesIO
from unittest.mock import MagicMock, patch, patch as mock_patch

from app.models.file.models import FileInfo

MODULE_PATCH = "minio.Minio"


def _make_file(file_id, project_id=None, uploader_id=None, file_name="test.pdf",
               file_path="mybucket/obj123", file_type="application/pdf", file_size=1024,
               download_count=0, create_time=None):
    return FileInfo(
        file_id=file_id,
        file_name=file_name,
        file_path=file_path,
        file_type=file_type,
        file_size=file_size,
        project_id=project_id,
        uploader_id=uploader_id,
        download_count=download_count,
        create_time=create_time or datetime.now(timezone.utc),
    )


@pytest.fixture
def mock_minio():
    with mock_patch(MODULE_PATCH) as cls:
        instance = MagicMock()
        cls.return_value = instance
        instance.bucket_exists.return_value = True
        instance.presigned_get_object.return_value = "https://minio.example.com/presigned-url"
        yield instance


@pytest.mark.asyncio
async def test_list_files_empty(client):
    resp = await client.get("/api/file")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == "SUCCESS"
    assert data["data"]["total"] == 0


@pytest.mark.asyncio
async def test_list_files_pagination(client, db_session):
    for i in range(15):
        db_session.add(_make_file(f"f-{i}"))
    await db_session.flush()

    resp = await client.get("/api/file", params={"page": 1, "size": 10})
    assert resp.status_code == 200
    data = resp.json()
    assert data["data"]["total"] == 15
    assert len(data["data"]["records"]) == 10


@pytest.mark.asyncio
async def test_list_files_filter_by_project_id(client, db_session):
    db_session.add(_make_file("f-p1", project_id="proj-a"))
    db_session.add(_make_file("f-p2", project_id="proj-b"))
    db_session.add(_make_file("f-p3", project_id="proj-a"))
    await db_session.flush()

    resp = await client.get("/api/file", params={"project_id": "proj-a"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["data"]["total"] == 2
    for r in data["data"]["records"]:
        assert r["projectId"] == "proj-a"


@pytest.mark.asyncio
async def test_list_files_filter_by_uploader_id(client, db_session):
    db_session.add(_make_file("f-u1", uploader_id="uploader-a"))
    db_session.add(_make_file("f-u2", uploader_id="uploader-b"))
    await db_session.flush()

    resp = await client.get("/api/file", params={"uploader_id": "uploader-a"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["data"]["total"] == 1


@pytest.mark.asyncio
async def test_upload_file(client, db_session, mock_minio):
    content = b"test file content here"
    resp = await client.post(
        "/api/file/upload",
        params={"project_id": "proj-1", "uploader_id": "user-1"},
        files={"file": ("report.pdf", BytesIO(content), "application/pdf")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == "SUCCESS"
    assert data["data"]["fileName"] == "report.pdf"
    assert data["data"]["fileSize"] == len(content)
    assert "fileId" in data["data"]

    # Verify MinIO put_object was called
    mock_minio.put_object.assert_called_once()
    call_args = mock_minio.put_object.call_args
    assert call_args[0][0] == "updg-files"


@pytest.mark.asyncio
async def test_upload_file_creates_db_record(client, db_session, mock_minio):
    content = b"upload test"
    resp = await client.post(
        "/api/file/upload",
        params={"project_id": "proj-x", "uploader_id": "user-x"},
        files={"file": ("doc.txt", BytesIO(content), "text/plain")},
    )
    assert resp.status_code == 200
    data = resp.json()
    file_id = data["data"]["fileId"]

    from sqlalchemy import select
    stmt = select(FileInfo).where(FileInfo.file_id == file_id)
    fi = (await db_session.execute(stmt)).scalar_one_or_none()
    assert fi is not None
    assert fi.file_name == "doc.txt"
    assert fi.file_size == len(content)
    assert fi.project_id == "proj-x"
    assert fi.uploader_id == "user-x"
    assert fi.download_count == 0


@pytest.mark.asyncio
async def test_download_file_success(client, db_session, mock_minio):
    db_session.add(_make_file("dl-1", file_path="mybucket/some_object.pdf"))
    await db_session.flush()

    resp = await client.get("/api/file/dl-1/download")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == "SUCCESS"
    assert "downloadUrl" in data["data"]
    assert data["data"]["fileName"] == "test.pdf"

    # Verify download count incremented
    from sqlalchemy import select
    stmt = select(FileInfo).where(FileInfo.file_id == "dl-1")
    fi = (await db_session.execute(stmt)).scalar_one()
    assert fi.download_count == 1


@pytest.mark.asyncio
async def test_download_file_not_found(client):
    resp = await client.get("/api/file/nonexistent/download")
    assert resp.status_code == 404
    data = resp.json()
    assert data["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_delete_file_success(client, db_session, mock_minio):
    db_session.add(_make_file("del-1", file_path="mybucket/to_delete.pdf"))
    await db_session.flush()

    resp = await client.delete("/api/file/del-1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == "SUCCESS"

    # Verify MinIO remove_object called
    mock_minio.remove_object.assert_called_once_with("mybucket", "to_delete.pdf")

    # Verify DB record removed
    from sqlalchemy import select
    stmt = select(FileInfo).where(FileInfo.file_id == "del-1")
    fi = (await db_session.execute(stmt)).scalar_one_or_none()
    assert fi is None


@pytest.mark.asyncio
async def test_delete_file_not_found(client):
    resp = await client.delete("/api/file/nonexistent")
    assert resp.status_code == 404
    data = resp.json()
    assert data["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_preview_file_success(client, db_session, mock_minio):
    db_session.add(_make_file("prev-1", file_path="mybucket/preview.pdf"))
    await db_session.flush()

    resp = await client.get("/api/file/prev-1/preview")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == "SUCCESS"
    assert "previewUrl" in data["data"]

    mock_minio.presigned_get_object.assert_called_once()
    call_kwargs = mock_minio.presigned_get_object.call_args[1]
    assert call_kwargs["expires"] == 3600


@pytest.mark.asyncio
async def test_preview_file_not_found(client):
    resp = await client.get("/api/file/nonexistent/preview")
    assert resp.status_code == 404
    data = resp.json()
    assert data["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_archive_project_files(client, db_session):
    db_session.add(_make_file("arch-1", project_id="proj-archive", file_path="mybucket/f1.pdf"))
    db_session.add(_make_file("arch-2", project_id="proj-archive", file_path="mybucket/f2.pdf"))
    db_session.add(_make_file("arch-other", project_id="other-proj", file_path="mybucket/f3.pdf"))
    await db_session.flush()

    resp = await client.post("/api/file/archive/proj-archive")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == "SUCCESS"
    assert data["data"]["archived"] == 2

    from sqlalchemy import select
    stmt = select(FileInfo).where(FileInfo.file_id == "arch-1")
    fi = (await db_session.execute(stmt)).scalar_one()
    assert fi.file_path.startswith("archived/")


@pytest.mark.asyncio
async def test_archive_project_files_already_archived(client, db_session):
    db_session.add(_make_file("arch-done", project_id="proj-done", file_path="archived/mybucket/old.pdf"))
    await db_session.flush()

    resp = await client.post("/api/file/archive/proj-done")
    assert resp.status_code == 200
    data = resp.json()
    assert data["data"]["archived"] == 0


@pytest.mark.asyncio
async def test_archive_no_files(client, db_session):
    resp = await client.post("/api/file/archive/empty-proj")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == "SUCCESS"
    assert data["data"]["archived"] == 0


@pytest.mark.asyncio
async def test_list_files_alias(client, db_session):
    db_session.add(_make_file("alias-1"))
    await db_session.flush()

    resp = await client.get("/api/file/list", params={"page": 1, "size": 10})
    assert resp.status_code == 200
    data = resp.json()
    assert data["data"]["total"] == 1


@pytest.mark.asyncio
async def test_download_file_alias(client, db_session, mock_minio):
    db_session.add(_make_file("alias-dl", file_path="mybucket/alias_obj.pdf"))
    await db_session.flush()

    resp = await client.get("/api/file/download/alias-dl")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == "SUCCESS"
    assert "downloadUrl" in data["data"]
