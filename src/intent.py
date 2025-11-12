import re
from typing import Final

_FILLERS: Final = {
    "hey",
    "hi",
    "hello",
    "robot",
    "please",
    "thanks",
    "thank",
    "you",
    "can",
    "could",
    "would",
    "should",
    "like",
    "to",
    "me",
    "for",
    "find",
    "look",
    "locate",
    "search",
    "get",
    "fetch",
    "help",
    "my",
    "the",
    "a",
    "an",
    "some",
    "is",
    "where",
    "please",
    "need",
    "want",
    "i"
}


def parse_intent(utterance: str) -> str:
    """
    Reduce a spoken sentence to just the object phrase.
    Strips filler/command words and returns whatever remains.
    """
    if not utterance:
        return ""

    tokens = re.findall(r"[a-zA-Z0-9']+", utterance.lower())
    object_words = [t for t in tokens if t not in _FILLERS]
    return " ".join(object_words).strip()


def needs_clarification(obj_phrase: str) -> bool:
    """We need clarification if the filtered phrase is empty."""
    return obj_phrase == ""
