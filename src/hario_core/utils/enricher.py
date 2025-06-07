"""Extensible enrichment logic for HAR data."""
from typing import Any, Dict, List
from urllib.parse import urlparse

from hario_core.interfaces import Enricher, HarEntry


def extract_domain(url: str) -> str:
    """Extracts the domain from a URL."""
    return urlparse(url).netloc


def domain_enricher(entry: HarEntry, data: Dict[str, Any]) -> None:
    """
    An enricher that adds the 'domain' field to the data,
    extracted from the request URL.
    """
    if entry.request and entry.request.url:
        data["domain"] = extract_domain(entry.request.url)


def apply_enrichment(
    entry: HarEntry, enrichers: List[Enricher] | None = None
) -> Dict[str, Any]:
    """Enriches a HAR entry model by applying a list of enricher functions.

    It first converts the Pydantic model to a dictionary and then applies
    each provided enricher function to it in sequence. If no enrichers are
    provided, no enrichment is performed, and a plain dictionary
    representation of the entry is returned.

    Args:
        entry: The HAR entry model to enrich.
        enrichers: An optional list of enricher functions to apply.

    Returns:
        A dictionary with the enriched data.
    """
    data = entry.model_dump()

    if not enrichers:
        return data

    for enricher in enrichers:
        enricher(entry, data)
    return data 