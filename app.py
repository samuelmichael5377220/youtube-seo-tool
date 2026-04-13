import streamlit as st

# 1. IMMEDIATE ERROR CATCHING
try:
    from googleapiclient.discovery import build
    import re
    from collections import Counter
except ImportError as e:
    st.error(f"Missing library: {e}. Please check your requirements.txt")
    st.stop()

# ====================== CONFIG ======================
st.set_page_config(page_title="Pro YouTube SEO", layout="wide")

STOP_WORDS = {"the", "and", "a", "an", "to", "of", "in", "for", "on", "with", "at", "by", "from", "as", "is", "are", "was", "be", "this", "that", "these", "those", "it", "i", "you", "your", "we", "our", "me", "my", "video", "videos", "youtube", "subscribe", "http", "https", "channel"}
DEFAULT_HANDLE = "@RandomVid-m5x"

# Initialize session state
if 'global_keywords' not in st.session_state: st.session_state.global_keywords = []
if 'channel_videos' not in st.session_state: st.session_state.channel_videos = []

# Helper Functions
def clean_text(text):
    return re.sub(r'[^a-zA-Z0-9\s#]', '', str(text).lower())

def extract_keywords(text, max_words=25):
    text = clean_text(text)
    words = [w for w in text.split() if w not in STOP_WORDS and len(w) > 3]
    return Counter(words).most_common(max_words)

# ====================== UI BINDING ======================
st.title("Global YouTube SEO Optimizer")

# Sidebar
st.sidebar.header("Settings")
api_key = st.sidebar.text_input("YouTube Data API Key", type="password")
target_regions = st.sidebar.multiselect("Target Regions", ["US", "GB", "CA", "AU", "IN", "NG"], default=["US", "GB"])

if not api_key:
    st.info("Enter your API Key in the sidebar to begin.")
    st.stop()

# Create API Client
try:
    youtube = build("youtube", "v3", developerKey=api_key)
except Exception as e:
    st.error(f"API Connection Error: {e}")
    st.stop()

tab1, tab2 = st.tabs(["Global Trending", "Channel & SEO"])

with tab1:
    st.header("What the World is Watching")
    if st.button("Fetch Global Trends", type="primary"):
        all_text = ""
        for reg in target_regions:
            try:
                res = youtube.videos().list(part="snippet", chart="mostPopular", regionCode=reg, maxResults=15).execute()
                for item in res.get("items", []):
                    all_text += f"{item['snippet']['title']} {item['snippet'].get('description', '')} "
            except: continue
        st.session_state.global_keywords = extract_keywords(all_text, 25)
        st.success("Trends Updated")

    if st.session_state.global_keywords:
        for word, count in st.session_state.global_keywords:
            st.write(f"- {word}")

with tab2:
    st.header(f"Strategy for {DEFAULT_HANDLE}")
    if st.button("Analyze My Latest Videos"):
        try:
            ch_resp = youtube.channels().list(part="contentDetails", forHandle=DEFAULT_HANDLE).execute()
            if ch_resp.get("items"):
                upload_id = ch_resp["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
                v_list = youtube.playlistItems().list(part="snippet,contentDetails", playlistId=upload_id, maxResults=3).execute()
                v_ids = [v["contentDetails"]["videoId"] for v in v_list["items"]]
                st.session_state.channel_videos = youtube.videos().list(part="snippet,statistics", id=",".join(v_ids)).execute().get("items", [])
                st.success("Videos Loaded")
            else: st.error("Channel not found.")
        except Exception as e: st.error(f"Error: {e}")

    if st.session_state.channel_videos:
        for v in st.session_state.channel_videos:
            st.subheader(v['snippet']['title'])
            st.write("Suggested Keywords to add:")
            suggested = [w[0] for w in st.session_state.global_keywords[:8]]
            st.code(", ".join(suggested))
