"""Sample HAR data for testing purposes."""

from typing import Any, Dict, List

import orjson

# Common pages for both samples
PAGES: List[Dict[str, Any]] = [
    {
        "startedDateTime": "2025-06-05T19:27:31.869Z",
        "id": "page_2",
        "title": "https://test.test/1",
        "pageTimings": {
            "onContentLoad": 1969.645000062883,
            "onLoad": 3605.7870000367984,
        },
    },
    {
        "startedDateTime": "2025-06-05T19:27:27.514Z",
        "id": "page_1",
        "title": "https://test.test/2",
        "pageTimings": {
            "onContentLoad": 501.66700000409037,
            "onLoad": 1302.6639999588951,
        },
    },
]

# Real Chrome DevTools HAR (with _initiator, _resourceType, etc.)
CHROME_DEVTOOLS_HAR: Dict[str, Any] = {
    "log": {
        "version": "1.2",
        "creator": {"name": "WebInspector", "version": "537.36"},
        "pages": PAGES,
        "entries": [
            {
                "_connectionId": "1270162",
                "_initiator": {
                    "type": "parser",
                    "url": "https://test.test/?param1=19704cee&param2=false",
                    "lineNumber": 11,
                },
                "_priority": "VeryHigh",
                "_resourceType": "stylesheet",
                "pageref": "page_1",
                "cache": {},
                "connection": "443",
                "request": {
                    "method": "GET",
                    "url": "https://test.test/assets/css/f2aaccf1.css",
                    "httpVersion": "http/2.0",
                    "headers": [
                        {"name": ":authority", "value": "test.test"},
                        {"name": ":method", "value": "GET"},
                        {"name": ":path", "value": "/assets/css/f2aaccf1.css"},
                        {"name": ":scheme", "value": "https"},
                        {"name": "accept", "value": "text/css,*/*;q=0.1"},
                        {"name": "accept-encoding", "value": "gzip, deflate, br, zstd"},
                        {
                            "name": "accept-language",
                            "value": "en-US,en;q=0.9,hy;q=0.8,ru;q=0.7",
                        },
                        {"name": "cache-control", "value": "no-cache"},
                        {"name": "pragma", "value": "no-cache"},
                        {"name": "priority", "value": "u=0"},
                        {
                            "name": "referer",
                            "value": "https://test.test/?param1=19704cee&param2=false",
                        },
                        {
                            "name": "sec-ch-ua",
                            "value": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
                        },
                        {"name": "sec-ch-ua-mobile", "value": "?0"},
                        {"name": "sec-ch-ua-platform", "value": '"macOS"'},
                        {"name": "sec-fetch-dest", "value": "style"},
                        {"name": "sec-fetch-mode", "value": "no-cors"},
                        {"name": "sec-fetch-site", "value": "same-origin"},
                        {
                            "name": "user-agent",
                            "value": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
                        },
                    ],
                    "queryString": [],
                    "cookies": [],
                    "headersSize": -1,
                    "bodySize": 0,
                },
                "response": {
                    "status": 200,
                    "statusText": "",
                    "httpVersion": "http/2.0",
                    "headers": [
                        {"name": "cache-control", "value": "max-age=3600"},
                        {"name": "content-encoding", "value": "gzip"},
                        {
                            "name": "content-security-policy",
                            "value": "frame-ancestors 'self';",
                        },
                        {
                            "name": "content-security-policy",
                            "value": "frame-ancestors 'self';",
                        },
                        {"name": "content-type", "value": "text/css"},
                        {"name": "date", "value": "Thu, 05 Jun 2025 16:29:09 GMT"},
                        {"name": "etag", "value": 'W/"684032a3-82d2c"'},
                        {"name": "expires", "value": "Thu, 05 Jun 2025 17:29:09 GMT"},
                        {
                            "name": "last-modified",
                            "value": "Wed, 04 Jun 2025 11:48:51 GMT",
                        },
                        {"name": "server", "value": "nginx"},
                        {
                            "name": "strict-transport-security",
                            "value": "max-age=63072000",
                        },
                        {"name": "vary", "value": "Accept-Encoding"},
                        {"name": "vary", "value": "Accept-Encoding"},
                        {"name": "x-cache-status", "value": "HIT"},
                        {"name": "x-content-type-options", "value": "nosniff"},
                        {"name": "x-content-type-options", "value": "nosniff"},
                        {"name": "x-frame-options", "value": "SAMEORIGIN"},
                        {"name": "x-frame-options", "value": "SAMEORIGIN"},
                        {"name": "x-sp-crid", "value": "17982016700:4"},
                        {"name": "x-xss-protection", "value": "1; mode=block"},
                        {"name": "x-xss-protection", "value": "1; mode=block"},
                    ],
                    "cookies": [],
                    "content": {"size": 535852, "mimeType": "text/css"},
                    "redirectURL": "",
                    "headersSize": -1,
                    "bodySize": -1,
                    "_transferSize": 116558,
                    "_error": None,
                    "_fetchedViaServiceWorker": False,
                },
                "serverIPAddress": "111.111.111.111",
                "startedDateTime": "2025-06-05T16:29:09.173Z",
                "time": 1142.6669999491423,
                "timings": {
                    "blocked": 30.817999938607215,
                    "dns": -1,
                    "ssl": -1,
                    "connect": -1,
                    "send": 3.2020000000000017,
                    "wait": 1061.3869999893382,
                    "receive": 47.2600000211969,
                    "_blocked_queueing": 14.454999938607216,
                    "_workerStart": -12.923,
                    "_workerReady": -12.011,
                    "_workerFetchStart": -1,
                    "_workerRespondWithSettled": -1,
                },
            }
        ],
    }
}

# Valid HAR 1.2
CLEANED_HAR: Dict[str, Any] = {
    "log": {
        "version": "1.2",
        "creator": {"name": "WebInspector", "version": "537.36"},
        "pages": [],
        "entries": [
            {
                "cache": {},
                "connection": "443",
                "request": {
                    "method": "GET",
                    "url": "https://test.test/assets/css/f2aaccf1.css",
                    "httpVersion": "http/2.0",
                    "headers": [
                        {"name": ":authority", "value": "test.test"},
                        {"name": ":method", "value": "GET"},
                        {"name": ":path", "value": "/assets/css/f2aaccf1.css"},
                        {"name": ":scheme", "value": "https"},
                        {"name": "accept", "value": "text/css,*/*;q=0.1"},
                        {"name": "accept-encoding", "value": "gzip, deflate, br, zstd"},
                        {
                            "name": "accept-language",
                            "value": "en-US,en;q=0.9,hy;q=0.8,ru;q=0.7",
                        },
                        {"name": "cache-control", "value": "no-cache"},
                        {"name": "pragma", "value": "no-cache"},
                        {"name": "priority", "value": "u=0"},
                        {
                            "name": "referer",
                            "value": "https://test.test/?param1=19704cee&param2=false",
                        },
                        {
                            "name": "sec-ch-ua",
                            "value": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
                        },
                        {"name": "sec-ch-ua-mobile", "value": "?0"},
                        {"name": "sec-ch-ua-platform", "value": '"macOS"'},
                        {"name": "sec-fetch-dest", "value": "style"},
                        {"name": "sec-fetch-mode", "value": "no-cors"},
                        {"name": "sec-fetch-site", "value": "same-origin"},
                        {
                            "name": "user-agent",
                            "value": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
                        },
                    ],
                    "queryString": [],
                    "cookies": [],
                    "headersSize": -1,
                    "bodySize": 0,
                },
                "response": {
                    "status": 200,
                    "statusText": "",
                    "httpVersion": "http/2.0",
                    "headers": [
                        {"name": "cache-control", "value": "max-age=3600"},
                        {"name": "content-encoding", "value": "gzip"},
                        {
                            "name": "content-security-policy",
                            "value": "frame-ancestors 'self';",
                        },
                        {
                            "name": "content-security-policy",
                            "value": "frame-ancestors 'self';",
                        },
                        {"name": "content-type", "value": "text/css"},
                        {"name": "date", "value": "Thu, 05 Jun 2025 16:29:09 GMT"},
                        {"name": "etag", "value": 'W/"684032a3-82d2c"'},
                        {"name": "expires", "value": "Thu, 05 Jun 2025 17:29:09 GMT"},
                        {
                            "name": "last-modified",
                            "value": "Wed, 04 Jun 2025 11:48:51 GMT",
                        },
                        {"name": "server", "value": "nginx"},
                        {
                            "name": "strict-transport-security",
                            "value": "max-age=63072000",
                        },
                        {"name": "vary", "value": "Accept-Encoding"},
                        {"name": "vary", "value": "Accept-Encoding"},
                        {"name": "x-cache-status", "value": "HIT"},
                        {"name": "x-content-type-options", "value": "nosniff"},
                        {"name": "x-content-type-options", "value": "nosniff"},
                        {"name": "x-frame-options", "value": "SAMEORIGIN"},
                        {"name": "x-frame-options", "value": "SAMEORIGIN"},
                        {"name": "x-sp-crid", "value": "17982016700:4"},
                        {"name": "x-xss-protection", "value": "1; mode=block"},
                        {"name": "x-xss-protection", "value": "1; mode=block"},
                    ],
                    "cookies": [],
                    "content": {"size": 535852, "mimeType": "text/css"},
                    "redirectURL": "",
                    "headersSize": -1,
                    "bodySize": -1,
                },
                "serverIPAddress": "111.111.111.111",
                "startedDateTime": "2025-06-05T16:29:09.173Z",
                "pageref": "page_2",
                "time": 1142.6669999491423,
                "timings": {
                    "blocked": 30.817999938607215,
                    "dns": -1,
                    "ssl": -1,
                    "connect": -1,
                    "send": 3.2020000000000017,
                    "wait": 1061.3869999893382,
                    "receive": 47.2600000211969,
                },
            }
        ],
    }
}

CLEANED_HAR_BYTES: bytes = orjson.dumps(CLEANED_HAR)

CHROME_DEVTOOLS_HAR_BYTES: bytes = orjson.dumps(CHROME_DEVTOOLS_HAR)

# Edge-case: HAR without log field (based on real HAR)
INVALID_HAR_NO_LOG: Dict[str, Any] = {
    k: v for k, v in CHROME_DEVTOOLS_HAR.items() if k != "log"
}

# Edge-case: HAR without version field (based on real HAR)
INVALID_HAR_NO_VERSION: Dict[str, Any] = {
    "log": {k: v for k, v in CHROME_DEVTOOLS_HAR["log"].items() if k != "version"}
}

# Edge-case: HAR without entries field (based on real HAR)
INVALID_HAR_NO_ENTRIES: Dict[str, Any] = {
    "log": {k: v for k, v in CHROME_DEVTOOLS_HAR["log"].items() if k != "entries"}
}

# Edge-case: log empty (based on real HAR)
INVALID_HAR_LOG_EMPTY: Dict[str, Any] = {"log": {}}

# Edge-case: log with version and creator, but without entries (based on real HAR)
INVALID_HAR_LOG_WITH_VERSION_BUT_NO_ENTRIES: Dict[str, Any] = {
    "log": {
        "version": CHROME_DEVTOOLS_HAR["log"]["version"],
        "creator": CHROME_DEVTOOLS_HAR["log"]["creator"],
    }
}

# Edge-case: root is not dict
INVALID_HAR_ROOT_NOT_DICT: int = 123
