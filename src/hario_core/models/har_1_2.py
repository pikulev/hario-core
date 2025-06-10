"""Pydantic representation of the HAR 1.2 specification.
Only a subset of rarely‑used fields are omitted for brevity;
`model_config = ConfigDict(extra='allow')` keeps them anyway.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class Header(BaseModel):
    name: str
    value: str
    comment: Optional[str] = None


class Cookie(BaseModel):
    name: str
    value: str
    path: Optional[str] = None
    domain: Optional[str] = None
    expires: Optional[str] = None
    httpOnly: Optional[bool] = None
    secure: Optional[bool] = None
    sameSite: Optional[str] = Field(None, alias="sameSite")
    comment: Optional[str] = None


class QueryString(Header):
    pass


class PostParam(BaseModel):
    name: str
    value: str
    fileName: Optional[str] = None
    contentType: Optional[str] = None
    comment: Optional[str] = None


class PostData(BaseModel):
    mimeType: str
    params: Optional[List[PostParam]] = None
    text: str
    comment: Optional[str] = None


class Content(BaseModel):
    size: int
    compression: Optional[int] = None
    mimeType: str
    text: Optional[str] = None
    encoding: Optional[str] = None
    comment: Optional[str] = None


class Request(BaseModel):
    method: str
    url: str
    httpVersion: str
    headers: List[Header]
    queryString: List[QueryString]
    cookies: List[Cookie]
    headersSize: int
    bodySize: int
    postData: Optional[PostData] = Field(default=None)
    comment: Optional[str] = None


class Response(BaseModel):
    status: int
    statusText: str
    httpVersion: str
    headers: List[Header]
    cookies: List[Cookie]
    content: Content
    redirectURL: str
    headersSize: int
    bodySize: int
    comment: Optional[str] = None


class Timings(BaseModel):
    blocked: Optional[float] = None
    dns: Optional[float] = None
    connect: Optional[float] = None
    send: float
    wait: float
    receive: float
    ssl: Optional[float] = None
    comment: Optional[str] = None


class Entry(BaseModel):
    """HAR Entry object."""

    model_config = ConfigDict(
        extra="forbid",
    )

    pageref: Optional[str] = None
    startedDateTime: datetime
    time: float
    request: Request
    response: Response
    cache: Dict[str, Any]
    timings: Timings
    serverIPAddress: Optional[str] = None
    connection: Optional[str] = None
    comment: Optional[str] = None


class Creator(BaseModel):
    name: str
    version: str


class Browser(Creator):
    pass


class PageTimings(BaseModel):
    onContentLoad: Optional[float] = None
    onLoad: Optional[float] = None


class Page(BaseModel):
    startedDateTime: datetime
    id: str
    title: str
    pageTimings: PageTimings


class HarLog(BaseModel):
    model_config = ConfigDict(extra="forbid")  # strict: forbid vendor‑specific fields

    version: str
    creator: Creator
    browser: Optional[Browser] = None
    pages: List[Page] = []
    entries: List[Entry]
