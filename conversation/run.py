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
    say("Hey there! What should I go find for you today?")
    print("Hey there! What should I go find for you today?")
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
    payload = details.to_payload()
    DATA_FILE.write_text(json.dumps(payload, indent=2))


def fill_missing_details(details: RequestDetails, speech: SpeechInterface) -> RequestDetails:
    """
    Prompt the user for missing location/trait details if the LLM response omitted them.
    """
    location = details.last_seen_location
    traits = details.traits

    if not location:
        say("Got it. Where did you last spot it?")
        location = speech.listen("Where did you last see it? (Enter to skip): ").strip()

    if not traits:
        say("Any colors or details that would help me identify it?")
        trait_text = speech.listen("List any visual traits (comma separated, enter to skip): ").strip()
        if trait_text:
            traits = [t.strip() for t in trait_text.split(",") if t.strip()]

    return RequestDetails(details.object, location, traits)


def describe_object(details: RequestDetails) -> str:
    """Build a conversational description of the request."""
    trait_text = ""
    if details.traits:
        trait_text = ", ".join(details.traits + [details.object])
    else:
        trait_text = details.object
    trait_text = trait_text.strip()
    if details.last_seen_location:
        return f"{trait_text} near {details.last_seen_location}".strip()
    return trait_text or "it"


def main() -> None:
    speech = SpeechInterface()
    parser = LLMRequestParser()
    r = Robot()
    try:
        utterance = prompt_for_request(speech)
        details = parser.parse(utterance)
        if not details.object:
            say("Hmm, I didn't catch what object you mentioned. Let's try again in a moment.")
            print("No clear object was detected.")
            return

        structured_payload = details.to_payload()
        print("Structured request (LLM output):")
        print(json.dumps(structured_payload, indent=2))

        enriched = fill_missing_details(details, speech)
        final_payload = enriched.to_payload()
        print("Final structured request:")
        print(json.dumps(final_payload, indent=2))

        if confirm_request(enriched.object, enriched.last_seen_location, enriched.traits, speech):
            save_request(enriched)
            desc = describe_object(enriched)
            say(f"Awesome! I'll start looking for {desc}. Give me just a second to get ready.")
            print(f"Confirmed: {enriched.object}")
            if enriched.last_seen_location:
                print(f"Last seen: {enriched.last_seen_location}")
            if enriched.traits:
                print(f"Details: {', '.join(enriched.traits)}")
            print("Ready to go.")
        else:
            say("No worries, we can try again whenever you're ready.")
            print("Object not confirmed.")
    finally:
        r.stop()


if __name__ == "__main__":
    main()
