"""Celery application for async task processing."""

from __future__ import annotations

from celery import Celery

from app.config import settings

celery_app = Celery(
    "updg",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    worker_prefetch_multiplier=1,
)
