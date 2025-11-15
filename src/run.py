# wherebot_basic/run.py
import json
from pathlib import Path

from audio_stt import listen
from voice import say
from robot import Robot
from intent import parse_intent, needs_clarification

DATA_FILE = Path(__file__).with_name("request_data.json")


def prompt_for_request() -> str:
    """Ask the user for a full sentence describing the target object."""
    say("Hi! Tell me what you want me to find.")
    print("Hi! Tell me what you want me to find.")
    return listen("Describe what to find: ").strip()


def ask_last_seen_location() -> str:
    """Prompt the user for where they last saw the item."""
    say("Where is the last time you seen it?")
    print("Where is the last time you seen it?")
    return listen("Last seen location (you can skip): ").strip()


def ask_traits() -> list[str]:
    """Gather optional descriptive details; returns a list."""
    say("Share any details or clues about it. You can skip this.")
    print("Tell me any traits or clues. (comma separated, optional)")
    response = listen("Details (press Enter to skip): ").strip()
    if not response:
        return []
    traits = [part.strip() for part in response.split(",")]
    return [t for t in traits if t]


def confirm_request(obj: str, location: str, traits: list[str]) -> bool:
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
    reply = listen("Is this correct? (yes/no): ").strip().lower()
    return reply.startswith("y")


def save_request(obj: str, location: str, traits: list[str]) -> None:
    """Persist the simple task description for future stages."""
    payload = {
        "object": obj,
        "inferred_clues": {
            "last_seen_location": location,
            "traits": traits,
        },
        "priority_zones": [],
        "if_found": False,
    }
    DATA_FILE.write_text(json.dumps(payload, indent=2))


def main() -> None:
    r = Robot()
    try:
        utterance = prompt_for_request()
        obj = parse_intent(utterance)
        if needs_clarification(obj):
            say("I didn't catch the object in that sentence.")
            print("No clear object was detected.")
            return

        location = ask_last_seen_location()
        traits = ask_traits()

        if confirm_request(obj, location, traits):
            save_request(obj, location, traits)
            say(f"Great! I'll start looking for {obj}. Ready to go.")
            print(f"Confirmed: {obj}")
            if location:
                print(f"Last seen: {location}")
            if traits:
                print(f"Details: {', '.join(traits)}")
            print("Ready to go.")
        else:
            say("Okay, let's try again later.")
            print("Object not confirmed.")
    finally:
        r.stop()


if __name__ == "__main__":
    main()
