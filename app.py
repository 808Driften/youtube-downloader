import streamlit as st
from yt_dlp import YoutubeDL
import os
import re
from PIL import Image
import requests
from io import BytesIO

# Configure page
st.set_page_config(
    page_title="YouTube Downloader 2025",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
def load_css():
    st.markdown("""
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f0f2f6;
            color: #333;
        }
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        h1 {
            color: #ff0000;
            text-align: center;
            margin-bottom: 2rem;
        }
        .stTextInput > div > div > input {
            border-radius: 20px;
        }
        .stButton > button {
            background-color: #ff0000;
            color: white;
            border-radius: 20px;
            padding: 0.5rem 2rem;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            background-color: #cc0000;
            transform: scale(1.05);
        }
        .stAlert {
            border-radius: 10px;
            margin-top: 1rem;
        }
        .thumbnail {
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
    </style>
    """, unsafe_allow_html=True)

load_css()

# Main app
st.title("YouTube Downloader 2025")

def sanitize_filename(filename):
    """Remove invalid characters from filename"""
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def get_video_info(url):
    """Fetch video info and thumbnail"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        return info_dict

def download_video(url, download_type, quality=None):
    try:
        ydl_opts = {
            'outtmpl': os.path.join(os.path.expanduser("~"), "Downloads", "%(title)s.%(ext)s"),
            'quiet': True,
            'no_warnings': True,
            'format': 'best' if download_type == "Video" else 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }] if download_type == "Audio" else [],
        }

        if quality and download_type == "Video":
            ydl_opts['format'] = f'bestvideo[height<={quality}]+bestaudio/best'

        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            title = info_dict.get('title', 'video')
            filename = sanitize_filename(title) + (".mp4" if download_type == "Video" else ".mp3")
            download_path = os.path.join(os.path.expanduser("~"), "Downloads", filename)

            with st.spinner(f"Downloading {filename}..."):
                ydl.download([url])

        return True, filename, download_path

    except Exception as e:
        return False, str(e), None

# URL input
url = st.text_input("Enter YouTube URL", placeholder="https://www.youtube.com/watch?v=...")

if url:
    try:
        # Fetch video info
        info_dict = get_video_info(url)
        title = info_dict.get('title', 'video')
        thumbnail_url = info_dict.get('thumbnail', '')

        # Display video info
        col1, col2 = st.columns([1, 2])

        with col1:
            if thumbnail_url:
                response = requests.get(thumbnail_url)
                img = Image.open(BytesIO(response.content))
                st.image(img, caption=title, use_column_width=True, output_format="PNG", clamp=True)

        with col2:
            st.subheader(title)
            st.write(f"👤 Channel: {info_dict.get('uploader', 'Unknown')}")
            st.write(f"👀 Views: {info_dict.get('view_count', 0):,}")
            st.write(f"⏱️ Length: {info_dict.get('duration', 0) // 60}:{info_dict.get('duration', 0) % 60:02d}")

        # Download options
        download_type = st.radio("Select download type:", ("Video", "Audio"))

        if download_type == "Video":
            resolutions = ["1080p", "720p", "480p", "360p", "240p", "144p"]
            selected_resolution = st.selectbox("Select resolution:", resolutions)
            quality = int(selected_resolution[:-1])  # Extract resolution number
        else:
            selected_resolution = None
            quality = None

        if st.button("Download", key="download_button"):
            success, message, path = download_video(url, download_type, quality)

            if success:
                st.success(f"✅ Downloaded successfully to: {path}")
                st.balloons()
            else:
                st.error(f"❌ Error: {message}")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.error("Please try again or check if the video is available.")