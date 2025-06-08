"""Sample HAR data for testing purposes."""

import json
from typing import Any, Dict

# A standard, clean HAR 1.2 entry
CLEAN_HAR: Dict[str, Any] = {
    "log": {
        "version": "1.2",
        "creator": {"name": "TestHarness", "version": "1.0"},
        "entries": [
            {
                "startedDateTime": "2024-01-01T12:00:00.000Z",
                "time": 123.45,
                "request": {
                    "method": "GET",
                    "url": "http://example.com/clean",
                    "httpVersion": "HTTP/1.1",
                    "cookies": [],
                    "headers": [],
                    "queryString": [],
                    "headersSize": 100,
                    "bodySize": 0,
                },
                "response": {
                    "status": 200,
                    "statusText": "OK",
                    "httpVersion": "HTTP/1.1",
                    "cookies": [],
                    "headers": [],
                    "content": {"size": 123, "mimeType": "text/plain"},
                    "redirectURL": "",
                    "headersSize": 200,
                    "bodySize": 123,
                },
                "cache": {},
                "timings": {"send": 10, "wait": 100, "receive": 13.45},
            }
        ],
    }
}

# A HAR entry with Chrome DevTools-specific fields (prefixed with _)
DEVTOOLS_HAR: Dict[str, Any] = {
    "log": {
        "version": "1.2",
        "creator": {"name": "Chrome", "version": "120.0"},
        "entries": [
            {
                "_initiator": {"type": "script"},
                "_resourceType": "fetch",
                "startedDateTime": "2024-01-01T12:00:01.000Z",
                "time": 50,
                "request": {
                    "method": "POST",
                    "url": "http://api.example.com/data",
                    "httpVersion": "HTTP/2.0",
                    "cookies": [],
                    "headers": [],
                    "queryString": [],
                    "headersSize": 150,
                    "bodySize": 512,
                },
                "response": {
                    "status": 201,
                    "statusText": "Created",
                    "httpVersion": "HTTP/2.0",
                    "cookies": [],
                    "headers": [],
                    "content": {"size": 0, "mimeType": "application/json"},
                    "redirectURL": "",
                    "headersSize": 250,
                    "bodySize": 0,
                    "_transferSize": 812,
                },
                "cache": {},
                "timings": {"send": 5, "wait": 40, "receive": 5},
            },
            CLEAN_HAR["log"]["entries"][0],
        ],
    }
}

CLEAN_HAR_BYTES = json.dumps(CLEAN_HAR).encode("utf-8")
DEVTOOLS_HAR_BYTES = json.dumps(DEVTOOLS_HAR).encode("utf-8")
