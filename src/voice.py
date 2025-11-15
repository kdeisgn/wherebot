# wherebot_basic/voice.py
import subprocess
import threading

try:
    import pyttsx3

    _engine = pyttsx3.init()
except Exception:
    _engine = None

_lock = threading.Lock()


def _mac_say(text: str) -> bool:
    """Try the built-in macOS `say` command if pyttsx3 fails."""
    try:
        subprocess.run(["say", text], check=True)
        return True
    except Exception:
        return False


def say(text: str) -> None:
    """Speak text aloud; if TTS unavailable, fall back to macOS `say` or print."""
    if _engine is not None:
        with _lock:
            _engine.stop()
            _engine.say(text)
            _engine.runAndWait(2)
        return

    if _mac_say(text):
        return

    print(f"[VOICE] {text}")
