import speech_recognition as sr

def recognize_speech(audio_file=None):
    recognizer = sr.Recognizer()
    
    if audio_file:
        # Handle file input
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)
    else:
        # Handle microphone input
        with sr.Microphone() as source:
            print("Say something in Arabic (MSA)...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
    
    try:
        text = recognizer.recognize_google(audio, language='ar-EG')
        return text
    except sr.UnknownValueError:
        return 'Could not understand audio'
    except sr.RequestError as e:
        return f'Error: {e}'

if __name__ == '__main__':
    print(recognize_speech())