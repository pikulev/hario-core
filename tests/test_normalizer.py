"""Tests for normalization logic."""
from hario_core.models.har_1_2 import Entry, Request, Response, Timings
from hario_core.utils.normalizer import normalize_har_entry


def test_normalize_har_negative_values() -> None:
    """Checks that negative values are correctly replaced with None."""
    entry = Entry(
        startedDateTime="2022-01-01T00:00:00Z",
        time=-1,
        request=Request(
            method="GET", url="/", headersSize=-1, bodySize=-1, headers=[], queryString=[]
        ),
        response=Response(
            status=200, content={"size": 0, "mimeType": ""}, headersSize=-1, bodySize=-1, headers=[], cookies=[]
        ),
        cache={},
        timings=Timings(
            blocked=-1, dns=-10, connect=-0.5, send=1, wait=1, receive=1
        ),
    )
    normalized = normalize_har_entry(entry)
    assert normalized.time is None
    assert normalized.request.headersSize is None
    assert normalized.request.bodySize is None
    assert normalized.response.headersSize is None
    assert normalized.response.bodySize is None
    assert normalized.timings.blocked is None
    assert normalized.timings.dns is None
    assert normalized.timings.connect is None


def test_normalize_har_positive_and_zero_values() -> None:
    """Checks that positive and zero values are not changed."""
    entry = Entry(
        startedDateTime="2022-01-01T00:00:00Z",
        time=100,
        request=Request(
            method="GET", url="/", headersSize=0, bodySize=50, headers=[], queryString=[]
        ),
        response=Response(
            status=200, content={"size": 0, "mimeType": ""}, headersSize=100, bodySize=0, headers=[], cookies=[]
        ),
        cache={},
        timings=Timings(send=1, wait=1, receive=1),
    )
    original_entry = entry.model_copy(deep=True)
    normalized = normalize_har_entry(entry)
    assert normalized == original_entry 