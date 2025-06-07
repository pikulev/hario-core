"""Pydantic representation of the HAR 1.2 specification.
Only a subset of rarely‑used fields are omitted for brevity;
`model_config = ConfigDict(extra='allow')` keeps them anyway.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class Header(BaseModel):
    name: str
    value: str


class Cookie(BaseModel):
    name: str
    value: str
    path: Optional[str] = None
    domain: Optional[str] = None
    expires: Optional[str] = None
    httpOnly: Optional[bool] = None
    secure: Optional[bool] = None
    sameSite: Optional[str] = Field(None, alias="sameSite")


class QueryString(Header):
    pass


class PostParam(Header):
    pass


class Content(BaseModel):
    size: int
    mimeType: str = Field("application/octet-stream", alias="mimeType")
    text: Optional[str] = None
    encoding: Optional[str] = None


class Request(BaseModel):
    method: str
    url: str
    httpVersion: Optional[str] = Field(None, alias="httpVersion")
    headers: List[Header] = []
    queryString: List[QueryString] = []
    cookies: List[Cookie] = []
    headersSize: int | None = Field(None, alias="headersSize")
    bodySize: int | None = Field(None, alias="bodySize")
    postData: Optional[Dict[str, Any]] = Field(None, alias="postData")


class Response(BaseModel):
    status: int
    statusText: str = Field("", alias="statusText")
    httpVersion: Optional[str] = Field(None, alias="httpVersion")
    headers: List[Header] = []
    cookies: List[Cookie] = []
    content: Content
    redirectURL: str = Field("", alias="redirectURL")
    headersSize: int | None = Field(None, alias="headersSize")
    bodySize: int | None = Field(None, alias="bodySize")


class Timings(BaseModel):
    blocked: Optional[float] = None
    dns: Optional[float] = None
    connect: Optional[float] = None
    send: float
    wait: float
    receive: float
    ssl: Optional[float] = None


class Entry(BaseModel):
    startedDateTime: str
    time: float
    request: Request
    response: Response
    cache: Dict[str, Any]
    timings: Timings
    serverIPAddress: Optional[str] = Field(None, alias="serverIPAddress")
    connection: Optional[str] = None
    pageref: Optional[str] = None


class Creator(BaseModel):
    name: str
    version: str


class Browser(Creator):
    pass


class PageTimings(BaseModel):
    onContentLoad: Optional[float] = None
    onLoad: Optional[float] = None


class Page(BaseModel):
    startedDateTime: str
    id: str
    title: str
    pageTimings: PageTimings


class HarLog(BaseModel):
    model_config = ConfigDict(extra="allow")  # keep vendor‑specific fields

    version: str
    creator: Creator
    browser: Optional[Browser] = None
    pages: List[Page] = []
    entries: List[Entry]
