import sys
import argparse
from whisper_agent import TTSAgent
from llm_agent import LLMAgent
from stretch_audio import StretchAudio

def main(whisper_model_path):
    # << Initialization >>
    stretch_audio = StretchAudio()
    tts = TTSAgent(whisper_model_path)
    llm = LLMAgent()
    
    # << Talk to Stretch >>
    audio_file = stretch_audio.talk_to_stretch()
    if audio_file is None:
        print("[ERROR] No audio was captured from Stretch.")
        sys.exit(1)

    # << Whisper audio transcription >>
    audio_transcription = tts.transcribe_audio(audio_file)
    print(f"User: {audio_transcription}")

    # << LLM response >>
    conversation_id = llm.create_conversation()
    llm_response = llm.create_response(conversation_id, prompt=audio_transcription)
    print(f"LLM: {llm_response}")

    # << Exit >>
    sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--tts', type=str, required=False, help='Path to whisper tts model.')
    args = parser.parse_args()
    main(args.tts)
