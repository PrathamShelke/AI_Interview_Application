import streamlit as st
import openai
import pandas as pd
import os
from audio_recorder_streamlit import audio_recorder
from openpyxl import load_workbook

# Set your OpenAI API key
os.environ["OPENAI_API_KEY"] = "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"
client = openai.OpenAI()

def text_to_speech(text):
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )
    return response.content

def transcribe_audio(audio_file_path):
    with open(audio_file_path, "rb") as audio_file:
        transcript_response = client.audio.translations.create(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        )
    return transcript_response['data'][0]['text']

def save_to_excel(question, answer, filename="responses.xlsx"):
    if not os.path.isfile(filename):
        df = pd.DataFrame({'Question': [question], 'Answer': [answer]})
        df.to_excel(filename, index=False)
    else:
        df = pd.read_excel(filename)
        new_row = {'Question': question, 'Answer': answer}
        df = df.append(new_row, ignore_index=True)
        df.to_excel(filename, index=False)

questions = ["What is your favorite color?", "How do you spend your free time?"]

st.title("Q&A Session with ChatGPT")

if 'current_question_index' not in st.session_state:
    st.session_state['current_question_index'] = 0

while st.session_state['current_question_index'] < len(questions):
    question = questions[st.session_state['current_question_index']]
    st.write("Question:")
    st.write(question)

    tts_audio = text_to_speech(question)
    st.audio(tts_audio, format="audio/mp3")

    audio_bytes = audio_recorder()

    if audio_bytes and st.button("Submit Response"):
        audio_file_path = f'user_response_{st.session_state["current_question_index"]}.wav'
        with open(audio_file_path, 'wb') as f:
            f.write(audio_bytes.getbuffer())

        answer_text = transcribe_audio(audio_file_path)
        st.write(f"Your response: {answer_text}")

        save_to_excel(question, answer_text)
        st.session_state['current_question_index'] += 1

if st.session_state['current_question_index'] >= len(questions):
    st.write("All questions have been answered.")
