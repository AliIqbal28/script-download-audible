import speech_recognition as sr
import os
from pydub.utils import make_chunks
from pydub import AudioSegment
from pydub.playback import play
import codecs
import re
import fileinput
list=[]
#Curse words list
# with codecs.open("words_final.txt", "r") as f0:
#     sentences_lines=f0.read().splitlines()
#     for sentences in sentences_lines:
#         list.append(sentences)
# print(list)

# create a speech recognition object
r = sr.Recognizer()

# a function that splits the audio file into chunks
# and applies speech recognition
def get_large_audio_transcription(path):
    """
    Splitting the large audio file into chunks
    and apply speech recognition on each of these chunks
    """
    # open the audio file using pydub
    sound = AudioSegment.from_wav(path)
    chunk_length_ms = 5000 # pydub calculates in millisec
    chunks = make_chunks(sound, chunk_length_ms) #Make chunks of one sec
    folder_name = "audio-chunks"
    # create a directory to store the audio chunks
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    whole_text = ""
    # process each chunk
    for i, audio_chunk in enumerate(chunks, start=1):
        # export audio chunk and save it in
        # the `folder_name` directory.
        chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")
        # recognize the chunk
        with sr.AudioFile(chunk_filename) as source:
            audio_listened = r.record(source)
            # try converting it to text
            try:
                text = r.recognize_google(audio_listened,language="en-US")
                wav_file=AudioSegment.from_file(chunk_filename, format = "wav")
                # Reducing volume by 5
                silent_wav_file = AudioSegment.silent(duration=8000)
                #  Playing silent file
                play(silent_wav_file)
            except sr.UnknownValueError as e:
                print("Error:", str(e))
            else:
                text = f"{text.capitalize()}. "
                print(chunk_filename, ":", text)
                whole_text += text
    # return the text for all chunks detected
    return whole_text

path = "Welcome.wav"
print("\nFull text:", get_large_audio_transcription(path))