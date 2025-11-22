import os
import sys
import torch
import whisper

class TTSAgent:
    def __init__(self, whisper_model_path):
        self.tts_model = self._load_whisper_model(whisper_model_path)

    def _load_whisper_model(self, whisper_model_path):
        '''
            Load the local whisper model. Downloads it, if model not available locally.
            Inputs: local whisper model path.
            Output: model object.
        '''
        print("[INFO] Loading whisper...")
        try:
            if not os.path.exists(whisper_model_path) or not os.path.isfile(whisper_model_path):  # If model not found, load model
                model_name = "turbo"
                model = whisper.load_model(model_name)  # loads turbo model
                torch.save(model, whisper_model_path)
            
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            model = torch.load(whisper_model_path, weights_only=False, map_location=device)
            print('[INFO] Whisper model loaded successfully!')
            return model
        except Exception as e:
            print(f"[ERROR] Error loading Whisper model: {e}")
            return None

    def transcribe_audio(self, audio_file="user_audio.wav"):
        '''
            Transcribes the audio using the Whisper model.
            Input: audio file path.
            Output: transcription.
        '''
        if self.tts_model is not None:
            if os.path.exists(audio_file) and os.path.isfile(audio_file):
                return self.tts_model.transcribe(audio_file)['text']
            else:
                print("[ERROR] Audio file not found or invalid path.")
        else:
            print("[ERROR] Failed to load Whisper model.")
            sys.exit(1)
