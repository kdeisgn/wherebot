
def listen(prompt: str = "I'm listening… (or type and press Enter): ") -> str:
    """
    Try the default microphone via SpeechRecognition; if not available, fall back to input().
    """
    try:
        import speech_recognition as sr  # type: ignore
    except ImportError:
        # fallback: keyboard
        return input(prompt)

    r = sr.Recognizer()
    r.energy_threshold = 300
    r.dynamic_energy_threshold = True
    
    try:
        with sr.Microphone() as source:
            print(prompt)
            # Shorter adjustment time for faster response
            r.adjust_for_ambient_noise(source, duration=0.5)
            print("Listening...")
            audio = r.listen(source, timeout=4, phrase_time_limit=5)
        try:
            # Prefer Google (better accuracy, needs internet)
            # Fallback to Sphinx if Google fails
            try:
                text = r.recognize_google(audio)
                print(f"Heard: {text}")
                return text
            except sr.UnknownValueError:
                print("Could not understand audio")
                return input("(speech not understood) Please type: ")
            except sr.RequestError as e:
                print(f"Error with speech recognition service: {e}")
                # Try Sphinx as fallback
                try:
                    text = r.recognize_sphinx(audio)
                    print(f"Heard (offline): {text}")
                    return text
                except Exception:
                    return input("(speech service unavailable) Please type: ")
        except Exception as e:
            print(f"Recognition error: {e}")
            return input("(speech not understood) Please type: ")
    except OSError:
        # No microphone available
        print("No microphone detected. Using keyboard input.")
        return input(prompt)
    except Exception as e:
        # Other errors -> keyboard
        print(f"Microphone error: {e}. Using keyboard input.")
        return input(prompt)
