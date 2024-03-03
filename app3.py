import streamlit as st
import openai
import pandas as pd
from io import BytesIO
from audio_recorder_streamlit import audio_recorder
import os

# Set your OpenAI API key
os.environ["OPENAI_API_KEY"] = "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"
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
        transcript_response = client.audio.translations.create(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        )
    # Extracting text from the response
    return transcript_response

def save_to_excel(question, answer, filename="responses.xlsx"):
    df = pd.DataFrame({'Question': [question], 'Answer': [answer]})
    if not os.path.isfile(filename):
        df.to_excel(filename, index=False)
    else:
        df.to_excel(filename, index=False, mode='a', header=False)

questions = [
    "What is your favorite color?",
    "How do you spend your free time?"
]

st.title("Q&A Session with ChatGPT")

if 'current_question_index' not in st.session_state:
    st.session_state['current_question_index'] = 0
    st.session_state['waiting_for_answer'] = False

# Initialize 'question' variable to avoid NameError
question = ""

if st.session_state['current_question_index'] < len(questions):
    if not st.session_state['waiting_for_answer']:
        question = questions[st.session_state['current_question_index']]
        st.write("Question:")
        st.write(question)

        # Convert question to speech and play it
        tts_audio = text_to_speech(question)
        st.audio(tts_audio, format="audio/mp3")
        st.session_state['waiting_for_answer'] = True

    # Record user's answer
    audio_bytes = audio_recorder()

    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")

        # Save and transcribe the audio response
        audio_file_path = 'user_response.wav'
        with open(audio_file_path, 'wb') as f:
            f.write(audio_bytes)

        answer_text = transcribe_audio(audio_file_path)
        st.write(f"Your response: {answer_text}")

        # Save the Q&A pair to an Excel file
        save_to_excel(question, answer_text)

        # Button to go to the next question
        if st.button("Next Question"):
            st.session_state['current_question_index'] += 1
            st.session_state['waiting_for_answer'] = False
else:
    st.write("All questions have been answered.")
