"""File domain service — wraps MinIO storage operations.

Provides upload, download, list, delete, and archive operations backed by
MinIO object storage with metadata persisted in FileInfo.
"""

from __future__ import annotations

import uuid
from io import BytesIO

from fastapi import UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from minio import Minio

from app.config import settings
from app.core.schemas import PageResult
from app.exceptions import ResourceNotFoundError
from app.models.file.models import FileInfo


def _build_minio_client() -> Minio:
    """Create a MinIO client from application settings."""
    endpoint = settings.minio_endpoint.replace("http://", "").replace("https://", "")
    return Minio(
        endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure,
    )


class FileService:
    """Encapsulates file storage operations (MinIO + FileInfo metadata)."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self._minio: Minio | None = None

    @property
    def minio(self) -> Minio:
        """Lazy-initialized MinIO client."""
        if self._minio is None:
            self._minio = _build_minio_client()
        return self._minio

    # ── Upload ──────────────────────────────────────────────────────────

    async def upload(
        self,
        uploader_id: str,
        project_id: str,
        file: UploadFile,
    ) -> dict:
        """Upload a file to MinIO and persist its metadata."""
        content = await file.read()
        file_size = len(content)

        # Ensure bucket exists
        bucket = settings.minio_bucket
        if not self.minio.bucket_exists(bucket):
            self.minio.make_bucket(bucket)

        object_name = f"{uuid.uuid4().hex}_{file.filename}"
        self.minio.put_object(
            bucket, object_name, BytesIO(content), file_size
        )

        file_path = f"{bucket}/{object_name}"
        fi = FileInfo(
            file_id=str(uuid.uuid4()),
            file_name=file.filename or "unknown",
            file_path=file_path,
            file_type=file.content_type,
            file_size=file_size,
            project_id=project_id,
            uploader_id=uploader_id,
            download_count=0,
        )
        self.db.add(fi)
        await self.db.flush()

        return {
            "fileId": fi.file_id,
            "fileName": fi.file_name,
            "fileSize": fi.file_size,
            "filePath": fi.file_path,
        }

    # ── Download ────────────────────────────────────────────────────────

    async def download(self, file_id: str) -> dict:
        """Generate a presigned download URL and increment download count."""
        fi = await self._file_or_404(file_id)
        fi.download_count = (fi.download_count or 0) + 1
        await self.db.flush()

        bucket, object_name = fi.file_path.split("/", 1) if "/" in (fi.file_path or "") else (settings.minio_bucket, fi.file_path or "")
        url = self.minio.presigned_get_object(bucket, object_name)

        return {"downloadUrl": url, "fileName": fi.file_name}

    async def preview(self, file_id: str, expires: int = 3600) -> dict:
        """Generate a temporary presigned preview URL."""
        fi = await self._file_or_404(file_id)
        bucket, object_name = fi.file_path.split("/", 1) if "/" in (fi.file_path or "") else (settings.minio_bucket, fi.file_path or "")
        url = self.minio.presigned_get_object(bucket, object_name, expires=expires)
        return {"previewUrl": url, "fileName": fi.file_name}

    # ── List ────────────────────────────────────────────────────────────

    async def list_files(
        self,
        project_id: str | None = None,
        uploader_id: str | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> PageResult:
        """Paginated list of file metadata."""
        base = select(FileInfo).order_by(FileInfo.create_time.desc())
        if project_id:
            base = base.where(FileInfo.project_id == project_id)
        if uploader_id:
            base = base.where(FileInfo.uploader_id == uploader_id)

        total = await self.db.scalar(
            select(func.count()).select_from(base.subquery())
        )
        offset = (page - 1) * limit
        result = await self.db.execute(base.offset(offset).limit(limit))
        items = result.scalars().all()

        return PageResult(
            total=total or 0,
            page=page,
            size=limit,
            records=[
                {
                    "fileId": f.file_id,
                    "fileName": f.file_name,
                    "fileType": f.file_type,
                    "fileSize": f.file_size,
                    "projectId": f.project_id,
                    "uploaderId": f.uploader_id,
                    "downloadCount": f.download_count,
                    "createTime": str(f.create_time) if f.create_time else None,
                }
                for f in items
            ],
        )

    # ── Delete ──────────────────────────────────────────────────────────

    async def delete(self, file_id: str) -> None:
        """Delete a file from both MinIO and the database."""
        fi = await self._file_or_404(file_id)

        # Remove from MinIO
        if fi.file_path and "/" in fi.file_path:
            bucket, object_name = fi.file_path.split("/", 1)
            self.minio.remove_object(bucket, object_name)

        # Remove metadata
        await self.db.delete(fi)
        await self.db.flush()

    # ── Archive ─────────────────────────────────────────────────────────

    async def archive_project_files(self, project_id: str) -> dict:
        """Mark all files belonging to a project as archived."""
        stmt = select(FileInfo).where(FileInfo.project_id == project_id)
        result = await self.db.execute(stmt)
        items = result.scalars().all()

        archived = 0
        for fi in items:
            if not (fi.file_path or "").startswith("archived/"):
                fi.file_path = f"archived/{fi.file_path}"
                archived += 1

        await self.db.flush()
        return {"projectId": project_id, "archived": archived}

    # ── Internal helpers ────────────────────────────────────────────────

    async def _file_or_404(self, file_id: str) -> FileInfo:
        fi = await self.db.get(FileInfo, file_id)
        if not fi:
            raise ResourceNotFoundError("文件", file_id)
        return fi
