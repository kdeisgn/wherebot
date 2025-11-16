
from __future__ import annotations

from typing import Optional, Tuple

try:
    import speech_recognition as sr  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    sr = None  # type: ignore


def _capture_audio(prompt: str) -> Optional[Tuple["sr.Recognizer", "sr.AudioData"]]:
    """
    Collect one utterance from the default microphone.
    Returns (recognizer, audio) or None if audio could not be captured.
    """
    if sr is None:
        return None

    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True
    try:
        with sr.Microphone() as source:
            print(prompt)
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print("Listening...")
            audio = recognizer.listen(source, timeout=4, phrase_time_limit=5)
            return recognizer, audio
    except OSError:
        print("No microphone detected.")
    except Exception as exc:
        print(f"Microphone error: {exc}")
    return None


def google_transcribe(prompt: str) -> Optional[str]:
    """
    Try a single pass of Google speech recognition.
    Returns None if the speech service or microphone was unavailable.
    """
    bundle = _capture_audio(prompt)
    if not bundle:
        return None
    recognizer, audio = bundle
    try:
        text = recognizer.recognize_google(audio)
        print(f"Heard: {text}")
        return text
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as exc:
        print(f"Error with speech recognition service: {exc}")
    return None


def google_transcribe_file(audio_path: str) -> Optional[str]:
    """
    Run Google's recognizer on an audio file recorded elsewhere (e.g. Stretch mic).
    """
    if sr is None:
        return None

    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio)
        print(f"Heard: {text}")
        return text
    except FileNotFoundError:
        print(f"[WARN] Audio file not found: {audio_path}")
    except sr.UnknownValueError:
        print("Could not understand Stretch audio")
    except sr.RequestError as exc:
        print(f"Google speech service error: {exc}")
    except Exception as exc:
        print(f"[WARN] Failed to transcribe Stretch audio: {exc}")
    return None


def listen(prompt: str = "I'm listening… (or type and press Enter): ") -> str:
    """
    Try the default microphone via Google; if that fails, use Sphinx or keyboard input.
    """
    if sr is None:
        return input(prompt)

    bundle = _capture_audio(prompt)
    if not bundle:
        return input(prompt)
    recognizer, audio = bundle

    try:
        text = recognizer.recognize_google(audio)
        print(f"Heard: {text}")
        return text
    except sr.UnknownValueError:
        print("Could not understand audio")
        return input("(speech not understood) Please type: ")
    except sr.RequestError as exc:
        print(f"Error with speech recognition service: {exc}")
        try:
            text = recognizer.recognize_sphinx(audio)
            print(f"Heard (offline): {text}")
            return text
        except Exception:
            return input("(speech service unavailable) Please type: ")
