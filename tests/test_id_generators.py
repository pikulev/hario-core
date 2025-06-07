"""Tests for the ID generator."""
from hashlib import blake2b

from hario_core.id_generators import DeterministicIdGenerator
from hario_core.models.har_1_2 import Entry, Request, Response, Timings


def test_deterministic_id_generator() -> None:
    """Tests that the ID is generated deterministically."""
    entry = Entry(
        startedDateTime="2022-01-01T00:00:00Z",
        time=100,
        request=Request(
            method="GET",
            url="http://example.com/some-path",
            headers=[],
            queryString=[],
        ),
        response=Response(
            status=200, content={"size": 0, "mimeType": ""}, headers=[], cookies=[]
        ),
        cache={},
        timings=Timings(send=1, wait=1, receive=1),
    )
    generator = DeterministicIdGenerator()
    doc_id = generator.generate_id(entry)
    expected_id = blake2b(
        b"2022-01-01T00:00:00Z:http://example.com/some-path", digest_size=16
    ).hexdigest()
    assert doc_id == expected_id
