"""Pytest fixtures for HARP."""

from typing import Any

import pytest

from hario_core.models.har_1_2 import Entry, HarLog

from .samples import CLEAN_HAR


@pytest.fixture
def har_log() -> HarLog:
    return HarLog.model_validate(CLEAN_HAR["log"])


@pytest.fixture
def har_entry() -> Entry:
    return Entry.model_validate(CLEAN_HAR["log"]["entries"][0])


class TestEntryMixin:
    @staticmethod
    def make_entry(data: dict[str, Any]) -> Entry:
        return Entry.model_validate(data)

    @staticmethod
    def base_dict() -> dict[str, Any]:
        from copy import deepcopy

        from .samples import CLEAN_HAR

        return deepcopy(CLEAN_HAR["log"]["entries"][0])
