# app.py

import streamlit as st
import os
import requests
import sqlite3
import json
import datetime
import random
import time
import nltk
from textblob import TextBlob
from typing import List, Dict

# Download necessary NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('vader_lexicon', quiet=True)

# PAGE CONFIG
st.set_page_config(
    page_title="AI Job Search Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# BASIC SESSION STATE
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# SIMPLE CHATBOT LOGIC
def get_response(user_input):
    user_input = user_input.lower()
    if "job" in user_input:
        return "🔍 Sure! What job role and location are you looking for?"
    elif "resume" in user_input:
        return "📄 I can help with resume tips! Upload your resume if you'd like a review."
    elif "interview" in user_input:
        return "🎤 Interview prep is important. I can give you some common questions and tips!"
    elif "salary" in user_input:
        return "💰 Negotiating salary? I can offer tips on what to say and what to ask."
    else:
        return "🤖 I'm here to help you with job search, resume advice, interviews, or salary info!"

# MAIN TITLE
st.title("🤖 AI Job Search Assistant")
st.markdown("Ask me anything about jobs, resumes, interviews, or salaries!")

# CHAT UI
with st.form("chat_form"):
    user_input = st.text_input("💬 Your Message", placeholder="e.g. Help me find data analyst jobs in Mumbai")
    submitted = st.form_submit_button("Send")
    if submitted and user_input:
        response = get_response(user_input)
        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("Assistant", response))

# DISPLAY CHAT HISTORY
for sender, msg in st.session_state.chat_history:
    with st.chat_message(sender):
        st.markdown(msg)
