"""Tests for enrichment logic."""
from typing import Any, Dict

from hario_core.interfaces import HarEntry
from hario_core.models.har_1_2 import Entry, Request, Response, Timings
from hario_core.utils.enricher import apply_enrichment, domain_enricher, extract_domain


def test_extract_domain() -> None:
    """Tests domain extraction from a URL."""
    assert extract_domain("http://example.com/path") == "example.com"


def test_apply_enrichment_with_domain_enricher() -> None:
    """Tests enrichment with the default domain enricher."""
    entry = Entry(
        startedDateTime="2022-01-01T00:00:00Z",
        time=100,
        request=Request(
            method="GET",
            url="https://example.com/api",
            headers=[],
            queryString=[],
        ),
        response=Response(
            status=200,
            content={"size": 0, "mimeType": ""},
            headers=[],
            cookies=[],
        ),
        cache={},
        timings=Timings(send=1, wait=1, receive=1),
    )

    enriched = apply_enrichment(entry, enrichers=[domain_enricher])
    assert enriched["domain"] == "example.com"
    assert enriched["request"]["url"] == "https://example.com/api"


def test_apply_enrichment_with_no_enrichers() -> None:
    """Tests that no enrichment is applied when no enrichers are provided."""
    entry = Entry(
        startedDateTime="2022-01-01T00:00:00Z",
        time=100,
        request=Request(
            method="GET", url="https://example.com/api", headers=[], queryString=[]
        ),
        response=Response(
            status=200,
            content={"size": 0, "mimeType": ""},
            headers=[],
            cookies=[],
        ),
        cache={},
        timings=Timings(send=1, wait=1, receive=1),
    )
    enriched = apply_enrichment(entry, enrichers=[])
    assert "domain" not in enriched
    assert enriched["request"]["url"] == "https://example.com/api"


def test_apply_enrichment_with_custom_enricher() -> None:
    """Tests enrichment with a custom user-defined enricher."""
    entry = Entry(
        startedDateTime="2022-01-01T00:00:00Z",
        time=100,
        request=Request(
            method="GET", url="https://example.com/api", headers=[], queryString=[]
        ),
        response=Response(
            status=200,
            content={"size": 0, "mimeType": ""},
            headers=[],
            cookies=[],
        ),
        cache={},
        timings=Timings(send=1, wait=1, receive=1),
    )

    def custom_enricher(entry: HarEntry, data: Dict[str, Any]) -> None:
        data["custom_field"] = "custom_value"
        data["request_method"] = entry.request.method

    enriched = apply_enrichment(entry, enrichers=[domain_enricher, custom_enricher])
    assert enriched["domain"] == "example.com"
    assert enriched["custom_field"] == "custom_value"
    assert enriched["request_method"] == "GET" 