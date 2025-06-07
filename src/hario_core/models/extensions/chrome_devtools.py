"""Pydantic models for Chrome DevTools HAR extensions."""
from __future__ import annotations
from typing import Any, Dict, Optional, List
import json

from pydantic import BaseModel, Field, ConfigDict, field_validator, ValidationInfo, model_validator
from ..har_1_2 import Entry, Request, Response, Timings


class DevToolsCallFrame(BaseModel):
    """DevTools call frame information."""

    functionName: str
    scriptId: str
    url: str
    lineNumber: int
    columnNumber: int


class DevToolsStack(BaseModel):
    """DevTools stack information."""

    callFrames: List[DevToolsCallFrame]
    parent: Optional["DevToolsStack"] = None  # рекурсивно!


DevToolsStack.model_rebuild()


class DevToolsInitiator(BaseModel):
    """DevTools initiator information."""

    type: Optional[str] = None
    url: Optional[str] = None
    lineNumber: Optional[int] = None
    stack: Optional[DevToolsStack] = None  # The stack trace is a complex object


class _DevToolsEntryMixin(BaseModel):
    """Mixin for DevTools-specific fields in the Entry object."""
    connectionId: Optional[str] = Field(None, alias="_connectionId")
    resourceType: Optional[str] = Field(None, alias="_resourceType")
    initiator: Optional[DevToolsInitiator] = Field(None, alias="_initiator")
    priority: Optional[str] = Field(None, alias="_priority")

    # pylint: disable=too-many-ancestors
    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
    )

    @model_validator(mode="before")
    @classmethod
    def parse_json_fields(cls, values: dict[str, Any]) -> dict[str, Any]:
        for field in ("request", "response"):
            if field in values and isinstance(values[field], str):
                values[field] = json.loads(
                    values[field], parse_constant=lambda c: None
                )
        return values

    @field_validator("*", mode="before")
    @classmethod
    def empty_str_to_none(cls, v: Any, info: ValidationInfo) -> Any:
        if v == "":
            return None
        return v


class _DevToolsRequestMixin(BaseModel):
    """Mixin for DevTools-specific fields in the Request object."""
    request_id: Optional[str] = Field(None, alias="_requestId")


class _DevToolsResponseMixin(BaseModel):
    """Mixin for DevTools-specific fields in the Response object."""
    transferSize: Optional[int] = Field(None, alias="_transferSize")
    error: Optional[str] = Field(None, alias="_error")
    fetchedViaServiceWorker: Optional[bool] = Field(
        None, alias="_fetchedViaServiceWorker"
    )
    headers_text: Optional[str] = Field(None, alias="_headersText")


class _DevToolsTimingsMixin(BaseModel):
    """Mixin for DevTools-specific fields in the Timings object."""
    blocked_queueing: Optional[float] = Field(None, alias="_blocked_queueing")
    push_start: Optional[float] = Field(None, alias="_push_start")
    push_end: Optional[float] = Field(None, alias="_push_end")


class DevToolsRequest(Request, _DevToolsRequestMixin):
    """Request model with DevTools extensions."""
    priority: Optional[str] = Field(None, alias="_priority")


class DevToolsResponse(Response, _DevToolsResponseMixin):
    """Response model with DevTools extensions."""
    request_id: Optional[str] = Field(alias="_requestId", default=None)
    headers_text: Optional[str] = Field(alias="_headersText", default=None)


class DevToolsTimings(Timings, _DevToolsTimingsMixin):
    """Timings model with DevTools extensions."""
    pass


class DevToolsEntry(Entry, _DevToolsEntryMixin):
    """Entry model with DevTools extensions."""
    request: DevToolsRequest
    response: DevToolsResponse
    timings: DevToolsTimings 