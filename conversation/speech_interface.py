from __future__ import annotations

import os
from pathlib import Path
import sys
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

from audio_stt import listen as fallback_listen


class SpeechInterface:
    """
    Prefer the Stretch + Whisper audio path but gracefully fall back to the
    SpeechRecognition/input() helper when the hardware or model is unavailable.
    """

    def __init__(self, whisper_model_path: Optional[str] = None, use_stretch_audio: Optional[bool] = None):
        self._stretch_audio = None
        self._tts_agent = None
        self._whisper_model_path = whisper_model_path or self._default_model_path()
        self._latest_audio_path = Path(__file__).with_name("latest_request.wav")
        env_preference = os.environ.get("USE_STRETCH_AUDIO")
        if use_stretch_audio is None:
            use_stretch_audio = bool(env_preference) and env_preference not in {"0", "false", "False"}
        self._prefer_stretch = use_stretch_audio
        if self._prefer_stretch:
            self._bootstrap_whisper_stack()

    def _default_model_path(self) -> str:
        return str(Path(__file__).resolve().parents[1] / "llm_agent" / "whisper_turbo_model.pth")

    def _bootstrap_whisper_stack(self) -> None:
        try:
            from llm_agent.stretch_audio import StretchAudio
            from llm_agent.whisper_agent import TTSAgent

            self._stretch_audio = StretchAudio()
            self._tts_agent = TTSAgent(self._whisper_model_path)
        except Exception as exc:
            self._stretch_audio = None
            self._tts_agent = None
            print(f"[WARN] Stretch microphone pipeline unavailable: {exc}")

    @property
    def available(self) -> bool:
        return self._stretch_audio is not None and self._tts_agent is not None

    def listen(self, prompt: str) -> str:
        """
        Capture audio with the richest available pipeline.
        Always falls back to keyboard/microphone input helper.
        """
        if self._prefer_stretch and self.available:
            try:
                print(prompt)
                audio_path = self._latest_audio_path
                recorded_path = self._stretch_audio.talk_to_stretch(str(audio_path))
                if recorded_path:
                    transcript = self._transcribe_stretch_audio(recorded_path)
                    if transcript:
                        print(f"Heard: {transcript}")
                        return transcript.strip()
            except Exception as exc:
                print(f"[WARN] Whisper-based transcription failed: {exc}")
        return fallback_listen(prompt)

    def _transcribe_stretch_audio(self, audio_path: str) -> str:
        if self._tts_agent:
            try:
                whisper_text = self._tts_agent.transcribe_audio(audio_path)
                if whisper_text:
                    return whisper_text
            except Exception as exc:
                print(f"[WARN] Whisper transcription fallback failed: {exc}")
        try:
            os.remove(audio_path)
        except OSError:
            pass
        return ""
