import speech_recognition as sr

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something in Arabic (MSA)...")   
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio, language="ar-SA") 
        return text
    except sr.UnknownValueError:
        return 'Sorry, could not understand the audio.'
    except sr.RequestError:
        return 'Could not request results, check your internet connection.'

if __name__ == '__main__':
    result = recognize_speech()
    print(f'You said: {result}')