# Stretch Robot voice output
import threading

try:
    import pyttsx3

    _engine = pyttsx3.init()
except Exception:
    _engine = None

_lock = threading.Lock()


def say(text: str) -> None:
    """Speak text aloud; if TTS unavailable, log to console."""
    if _engine is not None:
        with _lock:
            _engine.stop()
            _engine.say(text)
            _engine.runAndWait()
        return

    print(f"[VOICE] {text}")
