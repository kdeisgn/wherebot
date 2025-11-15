from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import List

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

from intent import parse_intent

try:
    from llm_agent.llm_agent import LLMAgent
except Exception as exc:  # pragma: no cover - guard for missing deps
    LLMAgent = None  # type: ignore
    _LLM_IMPORT_ERROR = exc
else:
    _LLM_IMPORT_ERROR = None


@dataclass
class RequestDetails:
    object: str
    last_seen_location: str
    traits: List[str]


class LLMRequestParser:
    """
    Wraps the LLMAgent so we get consistent structured data.
    Falls back to the simple keyword parser when the LLM stack is unavailable.
    """

    def __init__(self) -> None:
        self._agent = None
        if LLMAgent is None:
            print(f"[WARN] LLMAgent import failed: {_LLM_IMPORT_ERROR}")
            return
        try:
            self._agent = LLMAgent()
        except Exception as exc:
            print(f"[WARN] Could not initialize LLMAgent: {exc}")
            self._agent = None

    def parse(self, utterance: str) -> RequestDetails:
        utterance = (utterance or "").strip()
        if not utterance:
            return RequestDetails("", "", [])

        if self._agent:
            payload = self._agent.extract_object_details(utterance)
            return RequestDetails(
                object=payload.get("object", ""),
                last_seen_location=payload.get("last_seen_location", ""),
                traits=payload.get("traits", []),
            )

        print("[WARN] Falling back to keyword intent parsing.")
        return RequestDetails(parse_intent(utterance), "", [])
