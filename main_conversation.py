import sys
import time
import argparse
from whisper_agent import TTSAgent
from llm_agent import LLMAgent
from stretch_audio import StretchAudio

def main(whisper_model_path):
    # << Initialization >>
    stretch_audio = StretchAudio()
    tts = TTSAgent(whisper_model_path)
    llm = LLMAgent()
    
    try:
        while True:
            # << Talk to Stretch >>
            stretch_audio.talk_to_stretch()

            # << Whisper audio transcription >>
            audio_transcription = tts.transcribe_audio("user_audio.wav")
            print(f"User: {audio_transcription}")

            # << LLM response >>
            conversation_id = llm.create_conversation()
            llm_response = llm.create_response(conversation_id, prompt=audio_transcription)
            print(f"LLM: {llm_response}")
            # TODO: Add a confirmation response before starting to search

            # <<Playing LLM response>>
            llm.convert_response_to_audio(llm_response)
            audio_frames = stretch_audio.load_audio("llm_audio.wav")
            stretch_audio.play_audio(audio_frames)
            time.sleep(0.1)
    except KeyboardInterrupt:
        # << Exit >>
        print("[INFO] User interrupted. Exiting...")
        llm.delete_conversation()
        sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--tts', type=str, required=False, help='Path to whisper tts model.')
    args = parser.parse_args()
    main(args.tts)