"""Privacy-preserving structured turn logging."""

from __future__ import annotations

import json
import os
import sys
from typing import Any


def log_turn(*, user_message: str, conversation_history_length: int, retrieved_chunks: list[dict[str, Any]], tool_calls: list[dict[str, Any]], final_response: str | None, any_errors: list[str]) -> None:
    if os.getenv("DEBUG") != "1":
        return
    print(json.dumps({"user_message": user_message, "conversation_history_length": conversation_history_length, "retrieved_chunks": retrieved_chunks, "tool_calls": tool_calls, "final_response": final_response, "any_errors": any_errors}, ensure_ascii=True), file=sys.stdout)