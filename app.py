import streamlit as st
import openai
import pandas as pd
import os
from io import BytesIO
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
import os
os.environ["OPENAI_API_KEY"]="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"
# Initialize OpenAI client
client = openai.OpenAI()

def text_to_speech(text):
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )
    audio_data = BytesIO(response.content)
    return audio_data


def transcribe_audio(audio_file_path):
    with open(audio_file_path, "rb") as audio_file:
        transcript = client.audio.translations.create(
            model="whisper-1",
            file=audio_file
        )
    return transcript['text']


def save_to_excel(question, answer, filename="responses.xlsx"):
    df = pd.DataFrame({'Question': [question], 'Answer': [answer]})
    if not os.path.isfile(filename):
        df.to_excel(filename, index=False)
    else:
        df.to_excel(filename, index=False, mode='a', header=False)


# List of questions
questions = [
    "What is your favorite color?",
    "How do you spend your free time?",
    # Add more questions as needed
]

# Streamlit app
st.title("Q&A Session with ChatGPT")

# Iterate over the questions
for question in questions:
    st.write(question)

    # Convert question to speech and play it
    tts_audio = text_to_speech(question)
    st.audio(tts_audio, format="audio/mp3")

    audio_bytes = audio_recorder()

    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")

        # Save the audio response to a file
        audio_file_path = 'user_response.wav'
        with open(audio_file_path, 'wb') as f:
            f.write(audio_bytes.getbuffer())

        # Transcribe the audio response
        answer_text = transcribe_audio(audio_file_path)
        st.write(f"Your response: {answer_text}")

        # Save the Q&A pair to an Excel file
        save_to_excel(question, answer_text)

st.write("All questions have been answered.")
