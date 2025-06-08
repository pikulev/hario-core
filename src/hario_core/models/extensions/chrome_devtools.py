"""Pydantic models for Chrome DevTools HAR extensions."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from ..har_1_2 import Entry, Request, Response, Timings


class DevToolsCallFrame(BaseModel):
    """DevTools call frame."""

    functionName: str
    scriptId: str
    url: str
    lineNumber: int
    columnNumber: int
    stack: Optional[DevToolsStackTrace] = None


class DevToolsStackTrace(BaseModel):
    """DevTools stack trace."""

    callFrames: List[DevToolsCallFrame]
    parent: Optional[DevToolsStackTrace] = None


class DevToolsInitiator(BaseModel):
    """DevTools initiator object."""

    type: str
    stack: Optional[DevToolsStackTrace] = None


class DevToolsTimings(Timings):
    """Timings model with DevTools extensions."""

    blocked_queueing: Optional[float] = Field(None, alias="_blocked_queueing")
    push_start: Optional[float] = Field(None, alias="_push_start")
    push_end: Optional[float] = Field(None, alias="_push_end")


class DevToolsResponse(Response):
    """HAR Response object with DevTools extensions."""

    transferSize: Optional[int] = Field(None, alias="_transferSize")
    error: Optional[str] = Field(None, alias="_error")
    fromDiskCache: Optional[bool] = Field(None, alias="_fromDiskCache")
    fromServiceWorker: Optional[bool] = Field(None, alias="_fromServiceWorker")
    fromPrefetchCache: Optional[bool] = Field(None, alias="_fromPrefetchCache")


class DevToolsRequest(Request):
    """HAR Request object with DevTools extensions."""

    requestId: Optional[str] = Field(None, alias="_requestId")


class DevToolsEntry(Entry):
    """HAR Entry object with DevTools extensions."""

    initiator: Optional[DevToolsInitiator] = Field(None, alias="_initiator")
    priority: Optional[str] = Field(None, alias="_priority")
    resourceType: str = Field(alias="_resourceType")
    connectionId: Optional[str] = Field(None, alias="_connectionId")

    # Override fields from base Entry to use the extended models
    request: DevToolsRequest
    response: DevToolsResponse
    timings: DevToolsTimings


# Rebuild models to resolve forward references
DevToolsStackTrace.model_rebuild()
Entry.model_rebuild()
