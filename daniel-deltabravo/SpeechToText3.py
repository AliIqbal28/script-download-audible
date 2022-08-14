import speech_recognition as sr

# import soundfile
# data, samplerate = soundfile.read('out.wav')
# soundfile.write('new.wav', data, samplerate, subtype='PCM_16')

r = sr.Recognizer()
harvard = sr.AudioFile('chunk0.wav')
with harvard as source:
    audio = r.record(source)
# print(r.recognize_google(audio))
with open('out.txt', 'w') as f:
    print('Filename:', r.recognize_google(audio), file=f)