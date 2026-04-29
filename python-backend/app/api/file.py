"""File API router — replicates FileController with MinIO integration."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, UploadFile
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas import ApiResponse, PageResult
from app.config import settings
from app.database import get_db
from app.exceptions import ResourceNotFoundError
from app.models.file.models import FileInfo

router = APIRouter(tags=["file"])


@router.get("")
async def list_files(
    project_id: str | None = None, uploader_id: str | None = None,
    page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(FileInfo).order_by(FileInfo.create_time.desc())
    if project_id:
        stmt = stmt.where(FileInfo.project_id == project_id)
    if uploader_id:
        stmt = stmt.where(FileInfo.uploader_id == uploader_id)
    total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
    offset = (page - 1) * size
    result = await db.execute(stmt.offset(offset).limit(size))
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=PageResult(
        total=total, page=page, size=size,
        records=[{"fileId": f.file_id, "fileName": f.file_name, "fileType": f.file_type,
                 "fileSize": f.file_size, "projectId": f.project_id,
                 "uploaderId": f.uploader_id, "downloadCount": f.download_count,
                 "createTime": str(f.create_time) if f.create_time else None} for f in items],
    ))


@router.post("/upload")
async def upload_file(
    file: UploadFile,
    project_id: str | None = None,
    uploader_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    # Read file content
    content = await file.read()
    file_size = len(content)

    # Upload to MinIO
    from minio import Minio
    minio_client = Minio(
        settings.minio_endpoint.replace("http://", "").replace("https://", ""),
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=False,
    )
    bucket = settings.minio_bucket
    if not minio_client.bucket_exists(bucket):
        minio_client.make_bucket(bucket)

    object_name = f"{uuid.uuid4().hex}_{file.filename}"
    from io import BytesIO
    minio_client.put_object(bucket, object_name, BytesIO(content), file_size)

    # Save metadata
    file_path = f"{bucket}/{object_name}"
    fi = FileInfo(
        file_id=str(uuid.uuid4()), file_name=file.filename or "unknown",
        file_path=file_path, file_type=file.content_type,
        file_size=file_size, project_id=project_id,
        uploader_id=uploader_id, download_count=0,
    )
    db.add(fi)
    await db.flush()

    return ApiResponse(code="SUCCESS", message="上传成功", data={
        "fileId": fi.file_id, "fileName": fi.file_name,
        "fileSize": fi.file_size, "filePath": fi.file_path,
    })


@router.get("/{file_id}/download")
async def download_file(file_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(FileInfo).where(FileInfo.file_id == file_id)
    fi = (await db.execute(stmt)).scalar_one_or_none()
    if not fi:
        raise ResourceNotFoundError("文件", file_id)

    # Increment download count
    fi.download_count += 1
    await db.flush()

    # Get presigned URL from MinIO
    from minio import Minio
    minio_client = Minio(
        settings.minio_endpoint.replace("http://", "").replace("https://", ""),
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=False,
    )
    bucket, object_name = fi.file_path.split("/", 1)
    url = minio_client.presigned_get_object(bucket, object_name)

    return ApiResponse(code="SUCCESS", message="success", data={"downloadUrl": url, "fileName": fi.file_name})


@router.delete("/{file_id}")
async def delete_file(file_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(FileInfo).where(FileInfo.file_id == file_id)
    fi = (await db.execute(stmt)).scalar_one_or_none()
    if not fi:
        raise ResourceNotFoundError("文件", file_id)

    # Delete from MinIO
    from minio import Minio
    minio_client = Minio(
        settings.minio_endpoint.replace("http://", "").replace("https://", ""),
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=False,
    )
    bucket, object_name = fi.file_path.split("/", 1)
    minio_client.remove_object(bucket, object_name)

    # Delete from DB
    await db.delete(fi)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


@router.get("/{file_id}/preview")
async def preview_file(file_id: str, db: AsyncSession = Depends(get_db)):
    """File preview — generate a temporary presigned URL."""
    from fastapi.responses import RedirectResponse
    stmt = select(FileInfo).where(FileInfo.file_id == file_id)
    fi = (await db.execute(stmt)).scalar_one_or_none()
    if not fi:
        raise ResourceNotFoundError("文件", file_id)

    from minio import Minio
    minio_client = Minio(
        settings.minio_endpoint.replace("http://", "").replace("https://", ""),
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=False,
    )
    bucket, object_name = fi.file_path.split("/", 1)
    url = minio_client.presigned_get_object(bucket, object_name, expires=3600)
    return ApiResponse(code="SUCCESS", message="success", data={"previewUrl": url})


@router.post("/archive/{project_id}")
async def archive_project_files(project_id: str, db: AsyncSession = Depends(get_db)):
    """Archive all files for a project (mark as archived)."""
    stmt = select(FileInfo).where(FileInfo.project_id == project_id)
    result = await db.execute(stmt)
    items = result.scalars().all()
    archived = 0
    for fi in items:
        if not fi.file_path.startswith("archived/"):
            fi.file_path = f"archived/{fi.file_path}"
            archived += 1
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"archived": archived})


# ── Legacy aliases (frontend compatibility) ──────────────────────────

@router.get("/list")
async def list_files_alias(page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
                            db: AsyncSession = Depends(get_db)):
    return await list_files(page=page, size=size, db=db)


@router.get("/download/{file_id}")
async def download_file_alias(file_id: str, db: AsyncSession = Depends(get_db)):
    return await download_file(file_id, db)
