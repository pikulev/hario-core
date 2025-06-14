"""Pytest fixtures for HARP."""

from typing import Any, Dict, List, cast

import pytest

from hario_core.models import DevToolsEntry, Entry, HarLog
from hario_core.parse import validate

from .samples import CHROME_DEVTOOLS_HAR, CLEANED_HAR


@pytest.fixture
def chrome_devtools_har() -> Dict[str, Any]:
    return CHROME_DEVTOOLS_HAR


@pytest.fixture
def cleaned_har() -> Dict[str, Any]:
    return CLEANED_HAR


@pytest.fixture
def chrome_devtools_entry() -> Dict[str, Any]:
    return cast(Dict[str, Any], CHROME_DEVTOOLS_HAR["log"]["entries"][0])


@pytest.fixture
def cleaned_entry() -> Dict[str, Any]:
    return cast(Dict[str, Any], CLEANED_HAR["log"]["entries"][0])


@pytest.fixture
def chrome_devtools_entry_model() -> Entry:
    return DevToolsEntry.model_validate(CHROME_DEVTOOLS_HAR["log"]["entries"][0])


@pytest.fixture
def cleaned_entry_model() -> Entry:
    return Entry.model_validate(CLEANED_HAR["log"]["entries"][0])


@pytest.fixture
def cleaned_log() -> HarLog:
    return validate(CLEANED_HAR)


@pytest.fixture
def chrome_devtools_log() -> HarLog:
    return validate(CHROME_DEVTOOLS_HAR)


@pytest.fixture
def cleaned_entries(cleaned_log: HarLog) -> List[Dict[str, Any]]:
    return cast(List[Dict[str, Any]], cleaned_log.model_dump()["entries"])


@pytest.fixture
def chrome_devtools_entries(chrome_devtools_log: HarLog) -> List[Dict[str, Any]]:
    return cast(List[Dict[str, Any]], chrome_devtools_log.model_dump()["entries"])


@pytest.fixture
def entries_fixture(request: Any) -> Any:
    return request.getfixturevalue(request.param)
