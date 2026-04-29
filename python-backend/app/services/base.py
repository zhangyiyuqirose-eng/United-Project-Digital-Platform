"""Base service with common CRUD operations."""

from __future__ import annotations

from typing import Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas import PageResult
from app.exceptions import ResourceNotFoundError

T = TypeVar("T")


class BaseService(Generic[T]):
    """Generic base service providing standard CRUD for a single SQLAlchemy model.

    Domain services extend this by specifying their model type:

        class TimesheetService(BaseService[Timesheet]):
            def __init__(self, db: AsyncSession):
                super().__init__(db, Timesheet)
    """

    def __init__(self, db: AsyncSession, model: type[T]) -> None:
        self.db = db
        self.model = model

    # ── Read ────────────────────────────────────────────────────────────

    async def get_or_404(self, id: str) -> T:
        """Fetch a single entity by primary key, raise 404 if missing."""
        obj = await self.db.get(self.model, id)
        if not obj:
            raise ResourceNotFoundError(self.model.__name__, id)
        return obj

    async def get_optional(self, id: str) -> T | None:
        """Fetch a single entity by primary key, return None if missing."""
        return await self.db.get(self.model, id)

    # ── List / Page ─────────────────────────────────────────────────────

    async def list_page(self, page: int = 1, limit: int = 20, **filters) -> PageResult:
        """Generic paginated list with optional string/equality filters.

        String filter values produce ILIKE wildcard matches; non-string values
        use exact equality.
        """
        base = select(self.model)

        for field, value in filters.items():
            if value is not None and hasattr(self.model, field):
                col = getattr(self.model, field)
                if isinstance(value, str):
                    base = base.where(col.ilike(f"%{value}%"))
                else:
                    base = base.where(col == value)

        total = await self.db.scalar(
            select(func.count()).select_from(base.subquery())
        )

        result = await self.db.execute(
            base.offset((page - 1) * limit).limit(limit)
        )

        return PageResult(
            total=total or 0,
            page=page,
            size=limit,
            records=result.scalars().all(),
        )

    async def list_all(self, **filters) -> list[T]:
        """Return all matching rows (no pagination)."""
        base = select(self.model)
        for field, value in filters.items():
            if value is not None and hasattr(self.model, field):
                col = getattr(self.model, field)
                base = base.where(col == value)
        result = await self.db.execute(base)
        return list(result.scalars().all())

    # ── Create / Update / Delete ────────────────────────────────────────

    async def create(self, **kwargs) -> T:
        """Create and persist a new entity from keyword arguments."""
        obj = self.model(**kwargs)
        self.db.add(obj)
        await self.db.flush()
        return obj

    async def update(self, id: str, **kwargs) -> T:
        """Partially update an existing entity by primary key."""
        obj = await self.get_or_404(id)
        for k, v in kwargs.items():
            if v is not None and hasattr(obj, k):
                setattr(obj, k, v)
        await self.db.flush()
        return obj

    async def delete(self, id: str) -> None:
        """Delete an entity by primary key."""
        obj = await self.get_or_404(id)
        await self.db.delete(obj)
        await self.db.flush()

    # ── Count ───────────────────────────────────────────────────────────

    async def count(self, **filters) -> int:
        """Return the count of rows matching optional equality filters."""
        stmt = select(func.count()).select_from(self.model)
        for field, value in filters.items():
            if value is not None and hasattr(self.model, field):
                stmt = stmt.where(getattr(self.model, field) == value)
        return (await self.db.execute(stmt)).scalar() or 0
