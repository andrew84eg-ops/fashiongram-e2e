"""Recognise TanStack Start server-function calls in network traffic.

The app calls its backend through URLs like `/_serverFn/<base64url>`, where the
encoded part is JSON naming the source file and the exported function, e.g.
`{"file": "/src/lib/server/fashion.ts?...", "export": "ensureProfile_..."}`.
Decoding it lets a test wait for, or hold back, one specific backend call.
"""

import base64
import json
from urllib.parse import urlparse

_PREFIX = "/_serverFn/"


def server_fn_name(url: str) -> str | None:
    """Return the exported function name behind a server-function URL, or None."""
    path = urlparse(url).path
    if not path.startswith(_PREFIX):
        return None
    token = path[len(_PREFIX):].split("/")[0]
    token += "=" * (-len(token) % 4)
    try:
        meta = json.loads(base64.urlsafe_b64decode(token))
    except (ValueError, json.JSONDecodeError):
        return None
    export = str(meta.get("export", ""))
    return export.split("_")[0] or None


def is_server_fn(url: str, name: str) -> bool:
    return server_fn_name(url) == name
