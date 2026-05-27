"""Pydantic v2 schemas for Job Alert request/response payloads."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AlertCreate(BaseModel):
    name: str
    query: str
    filters: Optional[dict] = None
    frequency: str = "daily"
    channel: str = "email"


class AlertUpdate(BaseModel):
    name: Optional[str] = None
    query: Optional[str] = None
    filters: Optional[dict] = None
    frequency: Optional[str] = None
    channel: Optional[str] = None
    is_active: Optional[bool] = None


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    query: str
    filters: Optional[dict] = None
    frequency: str
    channel: str
    is_active: bool
    last_triggered_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
