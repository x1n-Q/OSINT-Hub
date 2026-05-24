"""
Console utilities for cross-platform text output.
"""

from __future__ import annotations

import sys
from typing import Any


def configure_console() -> None:
    """Avoid hard failures when the active console cannot print Unicode."""
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(errors="replace")
            except Exception:
                pass


def _stream_encoding(stream) -> str:
    return getattr(stream, "encoding", None) or "utf-8"


def safe_text(value: Any, stream=None) -> str:
    """Return text that can be encoded by the destination stream."""
    text = "" if value is None else str(value)
    target_stream = stream or sys.stdout
    encoding = _stream_encoding(target_stream)

    try:
        text.encode(encoding)
        return text
    except UnicodeEncodeError:
        return text.encode(encoding, errors="replace").decode(encoding)


def print_safe(*values: Any, sep: str = " ", end: str = "\n", file=None, flush: bool = False) -> None:
    """Print text without crashing on cp1252 and other limited encodings."""
    stream = file or sys.stdout
    rendered = sep.join(safe_text(value, stream=stream) for value in values)
    print(rendered, sep="", end=end, file=stream, flush=flush)
