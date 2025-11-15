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
    stretch_audio.talk_to_stretch()

    # << Whisper audio transcription >>
    audio_file = "output.wav"
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