from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
import re
from typing import Any, Dict, List

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

    def to_payload(self) -> Dict[str, Any]:
        """Return a JSON-serializable payload for downstream stages."""
        return {
            "object": self.object,
            "inferred_clues": {
                "last_seen_location": self.last_seen_location,
                "traits": self.traits,
            },
            "priority_zones": [],
            "if_found": False,
        }


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
                object=_core_object_word(payload.get("object", "")),
                last_seen_location=payload.get("last_seen_location", ""),
                traits=payload.get("traits", []),
            )

        print("[WARN] Falling back to keyword intent parsing.")
        return RequestDetails(_core_object_word(parse_intent(utterance)), "", [])


_TOKEN_RE = re.compile(r"[A-Za-z0-9']+")
_LOCATION_CUES = {
    "at",
    "on",
    "in",
    "inside",
    "near",
    "next",
    "nextto",
    "by",
    "beside",
    "under",
    "over",
    "behind",
    "around",
    "beneath",
    "below",
    "above",
    "between",
    "toward",
}


def _core_object_word(phrase: str) -> str:
    """
    Reduce a phrase to a single representative word describing the object.
    Stops once a location cue appears.
    """
    phrase = (phrase or "").strip().lower()
    if not phrase:
        return ""

    tokens = _TOKEN_RE.findall(phrase)
    object_tokens: List[str] = []
    for token in tokens:
        if token in _LOCATION_CUES:
            break
        object_tokens.append(token)
    if not object_tokens:
        return ""
    return object_tokens[-1]
