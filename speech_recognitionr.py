import speech_recognition as sr

def recognize_speech(audio_file=None):
    recognizer = sr.Recognizer()
    if audio_file:
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)
    else:
        with sr.Microphone() as source:
            print("Say something in Arabic (MSA)...")   
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
    try:
        if audio_file:
            text = recognizer.recognize_google(audio, language='ar-EG')
        else:
            text = recognizer.recognize_google(audio, language="ar-SA") 
        return text
    except sr.UnknownValueError:
        if audio_file:
            return 'Could not understand audio'
        else:
            return 'Sorry, could not understand the audio.'
    except sr.RequestError as e:
        if audio_file:
            return f'Error: {e}'
        else:
            return 'Could not request results, check your internet connection.'

if __name__ == '__main__':
    result = recognize_speech()
    print(f'You said: {result}')