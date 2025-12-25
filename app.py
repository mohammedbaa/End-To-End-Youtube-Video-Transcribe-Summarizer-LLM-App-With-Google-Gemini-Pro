import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import os
from urllib.parse import urlparse, parse_qs

from youtube_transcript_api import YouTubeTranscriptApi

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

prompt = """You are a YouTube Video Summarizer. You will take the transcript text
and summarize the entire video in important bullet points within 250 words.
Please provide the summary of this text:
"""


# ----------- FIXED YouTube ID Extraction -----------
def extract_video_id(url):
    try:
        parsed = urlparse(url)

        # format: https://www.youtube.com/watch?v=ID
        if parsed.query:
            return parse_qs(parsed.query).get("v", [None])[0]

        # format: https://youtu.be/ID
        if parsed.path:
            return parsed.path.lstrip("/")

    except:
        return None


# ----------- FIXED Transcript Extraction -----------
def extract_transcript_details(youtube_video_url):
    try:
        video_id = extract_video_id(youtube_video_url)

        if not video_id:
            st.error("❌ Could not extract video ID from URL.")
            return None

        # Correct usage
        ytt = YouTubeTranscriptApi()
        transcript_obj = ytt.fetch(video_id)  # fetch returns FetchedTranscript object
        transcript_raw = transcript_obj.to_raw_data()

        transcript = " ".join([t["text"] for t in transcript_raw])
        return transcript

    except Exception as e:
        st.error(f"❌ Transcript Error: {e}")
        return None


# ----------- Gemini Summary -----------
def generate_gemini_content(transcript_text, prompt):
    try:
        model = genai.GenerativeModel("gemini-2.5-pro")
        response = model.generate_content(prompt + transcript_text)
        return response.text
    except Exception as e:
        st.error(f"❌ Gemini Error: {e}")
        return None


# ----------- Streamlit UI -----------
st.title("YouTube Transcript → Detailed Notes")

youtube_link = st.text_input("Enter the YouTube Video Link:")

if youtube_link:
    vid = extract_video_id(youtube_link)
    if vid:
        st.image(f"http://img.youtube.com/vi/{vid}/0.jpg", use_container_width=True)
    else:
        st.error("❌ Invalid YouTube URL")


if st.button("Get Detailed Notes"):
    transcript = extract_transcript_details(youtube_link)

    if transcript:
        summary = generate_gemini_content(transcript, prompt)

        if summary:
            st.markdown("## 📘 Detailed Notes:")
            st.write(summary)


