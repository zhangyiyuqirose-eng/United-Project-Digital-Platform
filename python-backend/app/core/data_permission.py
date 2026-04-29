"""Data permission filter: row-level access control based on user's data scope.

Implements scope-based filtering: all / self / dept / dept_tree / custom.
Used as a SQLAlchemy query modifier injected into list endpoints.
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Optional

from sqlalchemy import ColumnElement, and_, or_

from app.core.rbac import DataScopeType, UserInfo

logger = logging.getLogger(__name__)


def build_data_filter(
    user_info: UserInfo,
    owner_field: str = "owner_id",
    dept_field: str = "dept_id",
) -> ColumnElement[bool] | None:
    """Build a SQLAlchemy filter expression based on user's data scope.

    Args:
        user_info: Resolved user info from RBAC manager.
        owner_field: Column name for the record owner (usually user_id).
        dept_field: Column name for the record's department.

    Returns:
        A filter expression to be applied to a select() query, or None for ALL scope.
    """
    scope = user_info.data_scope

    if scope == DataScopeType.ALL.value:
        return None  # No filter needed

    if scope == DataScopeType.SELF.value:
        # Only records owned by this user
        from sqlalchemy import column
        return column(owner_field) == user_info.user_id

    if scope == DataScopeType.DEPT.value:
        # Records from user's department
        if not user_info.dept_id:
            return column(owner_field) == user_info.user_id
        from sqlalchemy import column
        return column(dept_field) == user_info.dept_id

    if scope == DataScopeType.DEPT_TREE.value:
        # Records from user's department and all sub-departments
        if not user_info.dept_ids:
            if user_info.dept_id:
                from sqlalchemy import column
                return column(dept_field) == user_info.dept_id
            return column(owner_field) == user_info.user_id
        from sqlalchemy import column
        return column(dept_field).in_(user_info.dept_ids)

    if scope == DataScopeType.CUSTOM.value:
        # Custom filter based on user's assigned departments
        if not user_info.dept_ids:
            return column(owner_field) == user_info.user_id
        from sqlalchemy import column
        return column(dept_field).in_(user_info.dept_ids)

    # Fallback: self-only
    from sqlalchemy import column
    return column(owner_field) == user_info.user_id


def apply_data_filter(
    query,
    user_info: UserInfo,
    model_cls,
    owner_field: str = "owner_id",
    dept_field: str = "dept_id",
):
    """Apply data permission filter to an existing SQLAlchemy select query.

    Returns the original query if scope is ALL, otherwise adds a .where() clause.
    """
    filter_expr = build_data_filter(user_info, owner_field, dept_field)
    if filter_expr is None:
        return query
    return query.where(filter_expr)


class DataPermissionError(Exception):
    """Raised when data permission check fails."""
