#!/usr/bin/env python3
import json
from pathlib import Path

from request_parser import LLMRequestParser, RequestDetails
from speech_interface import SpeechInterface
from voice import say
from robot import Robot

DATA_FILE = Path(__file__).with_name("request_data.json")


def prompt_for_request(speech: SpeechInterface) -> str:
    """Ask the user for a full sentence describing the target object."""
    say("Hi! Tell me what you want me to find.")
    print("Hi! Tell me what you want me to find.")
    return speech.listen("Describe what to find: ").strip()


def confirm_request(obj: str, location: str, traits: list[str], speech: SpeechInterface) -> bool:
    """Confirm the full search request with the user in natural language."""
    voice_parts = [f"you're looking for the {obj}"]
    if location:
        voice_parts.append(f"you last saw it {location}")
    if traits:
        trait_text = ", ".join(traits)
        voice_parts.append(f"it sounds like {trait_text}")
    voice_summary = ", and ".join(voice_parts)

    text_parts = [f"object: {obj}"]
    if location:
        text_parts.append(f"last seen {location}")
    if traits:
        text_parts.append(f"traits: {', '.join(traits)}")
    text_summary = "; ".join(text_parts)

    say(f"So just to make sure, {voice_summary}. Did I get that right?")
    print(f"Just to confirm, {text_summary}. (yes/no)")
    reply = speech.listen("Is this correct? (yes/no): ").strip().lower()
    return reply.startswith("y")


def save_request(details: RequestDetails) -> None:
    """Persist the simple task description for future stages."""
    payload = {
        "object": details.object,
        "inferred_clues": {
            "last_seen_location": details.last_seen_location,
            "traits": details.traits,
        },
        "priority_zones": [],
        "if_found": False,
    }
    DATA_FILE.write_text(json.dumps(payload, indent=2))


def main() -> None:
    speech = SpeechInterface()
    parser = LLMRequestParser()
    r = Robot()
    try:
        utterance = prompt_for_request(speech)
        details = parser.parse(utterance)
        if not details.object:
            say("I didn't catch the object in that sentence.")
            print("No clear object was detected.")
            return

        if confirm_request(details.object, details.last_seen_location, details.traits, speech):
            save_request(details)
            say(f"Great! I'll start looking for {details.object}. Ready to go.")
            print(f"Confirmed: {details.object}")
            if details.last_seen_location:
                print(f"Last seen: {details.last_seen_location}")
            if details.traits:
                print(f"Details: {', '.join(details.traits)}")
            print("Ready to go.")
        else:
            say("Okay, let's try again later.")
            print("Object not confirmed.")
    finally:
        r.stop()


if __name__ == "__main__":
    main()
