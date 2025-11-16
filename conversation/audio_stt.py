
from __future__ import annotations

import os
from pathlib import Path
import sys
import tempfile
from typing import Optional, Tuple

try:
    import speech_recognition as sr  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    sr = None  # type: ignore

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

try:
    from llm_agent.whisper_agent import TTSAgent
except Exception:
    TTSAgent = None  # type: ignore

_WHISPER_AGENT: Optional["TTSAgent"] = None


def _get_whisper_agent() -> Optional["TTSAgent"]:
    global _WHISPER_AGENT
    if _WHISPER_AGENT is None and TTSAgent is not None:
        model_path = REPO_ROOT / "llm_agent" / "whisper_turbo_model.pth"
        try:
            _WHISPER_AGENT = TTSAgent(str(model_path))
        except Exception as exc:
            print(f"[WARN] Unable to bootstrap Whisper model: {exc}")
            _WHISPER_AGENT = None
    return _WHISPER_AGENT


def _capture_audio(prompt: str) -> Optional[Tuple["sr.Recognizer", "sr.AudioData"]]:
    """
    Collect one utterance from the default microphone using PyAudio.
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


def listen(prompt: str = "I'm listening… (or type and press Enter): ") -> str:
    """
    Capture audio via PyAudio and transcribe with Whisper; fall back to keyboard input.
    """
    if sr is None:
        return input(prompt)

    bundle = _capture_audio(prompt)
    if not bundle:
        return input(prompt)
    recognizer, audio = bundle

    agent = _get_whisper_agent()
    if agent is None:
        print("[WARN] Whisper unavailable; falling back to keyboard input.")
        return input(prompt)

    tmp_path = None
    try:
        wav_data = audio.get_wav_data()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(wav_data)
            tmp_path = tmp.name
        text = agent.transcribe_audio(tmp_path)
        if text:
            print(f"Heard: {text}")
            return text.strip()
    except Exception as exc:
        print(f"[WARN] Whisper transcription failed: {exc}")
    finally:
        if tmp_path:
            try:
                os.remove(tmp_path)
            except OSError:
                pass

    return input("(speech not understood) Please type: ")
