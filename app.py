import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re
from collections import Counter

# ====================== CONFIG ======================
st.set_page_config(page_title="Pro YouTube SEO", layout="wide")

# Expanded stop words for cleaner SEO results
STOP_WORDS = {"the", "and", "a", "an", "to", "of", "in", "for", "on", "with", "at", "by", "from", "as", "is", "are", "was", "be", "this", "that", "these", "those", "it", "i", "you", "your", "we", "our", "me", "my", "video", "videos", "youtube", "subscribe", "http", "https", "channel"}

# Default channel handle
DEFAULT_HANDLE = "@RandomVid-m5x"

# Initialize session state
if 'global_keywords' not in st.session_state: st.session_state.global_keywords = []
if 'global_hashtags' not in st.session_state: st.session_state.global_hashtags = []
if 'channel_videos' not in st.session_state: st.session_state.channel_videos = []

def clean_text(text):
    return re.sub(r'[^a-zA-Z0-9\s#]', '', str(text).lower())

def extract_keywords(text, max_words=25):
    text = clean_text(text)
    words = [w for w in text.split() if w not in STOP_WORDS and len(w) > 3]
    return Counter(words).most_common(max_words)

def extract_hashtags(text):
    return re.findall(r'#\w+', str(text).lower())

# Sidebar
st.sidebar.header("Settings")
api_key = st.sidebar.text_input("YouTube Data API Key", type="password")
target_regions = st.sidebar.multiselect("Target Regions", ["US", "GB", "CA", "AU", "IN", "NG", "DE"], default=["US", "GB"])

if not api_key:
    st.sidebar.warning("Please enter your API Key to unlock the tool.")
    st.stop()

youtube = build("youtube", "v3", developerKey=api_key)

st.title("Global YouTube SEO Optimizer")
st.markdown("Bridge the gap between your content and Global Trending Topics.")

tab1, tab2, tab3 = st.tabs(["Global Trending", "Channel Analysis", "SEO Suggestions"])

# --- TAB 1: GLOBAL TRENDING ---
with tab1:
    st.header("What the World is Watching")
    if st.button("Fetch Global Trends", type="primary"):
        with st.spinner("Analyzing global markets..."):
            all_text = ""
            all_hashtags = []
            for reg in target_regions:
                try:
                    res = youtube.videos().list(part="snippet", chart="mostPopular", regionCode=reg, maxResults=20).execute()
                    for item in res.get("items", []):
                        all_text += f"{item['snippet']['title']} {item['snippet'].get('description', '')} "
                        all_hashtags.extend(extract_hashtags(item['snippet'].get('description', '')))
                except: continue
            
            st.session_state.global_keywords = extract_keywords(all_text, 30)
            st.session_state.global_hashtags = Counter(all_hashtags).most_common(20)
            st.success("Trends Updated")

    if st.session_state.global_keywords:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Trending Keywords")
            for word, count in st.session_state.global_keywords[:15]:
                st.write(f"- {word}")
        with c2:
            st.subheader("Trending Hashtags")
            for tag, count in st.session_state.global_hashtags[:15]:
                st.write(f"- {tag}")

# --- TAB 2: CHANNEL ANALYSIS ---
with tab2:
    st.header(f"Data for {DEFAULT_HANDLE}")
    if st.button("Scan My Channel"):
        try:
            param = {"forHandle": DEFAULT_HANDLE}
            ch_resp = youtube.channels().list(part="contentDetails,snippet", **param).execute()
            
            if ch_resp.get("items"):
                channel = ch_resp["items"][0]
                upload_id = channel["contentDetails"]["relatedPlaylists"]["uploads"]
                
                v_list = youtube.playlistItems().list(part="contentDetails", playlistId=upload_id, maxResults=5).execute()
                video_ids = [v["contentDetails"]["videoId"] for v in v_list["items"]]
                
                full_v = youtube.videos().list(part="snippet,statistics", id=",".join(video_ids)).execute()
                st.session_state.channel_videos = full_v["items"]
                st.success(f"Scanned {len(st.session_state.channel_videos)} videos from {channel['snippet']['title']}")
            else:
                st.error("Channel not found.")
        except Exception as e:
            st.error(f"Error: {e}")

    if st.session_state.channel_videos:
        for v in st.session_state.channel_videos:
            st.text(f"Loaded: {v['snippet']['title']}")

# --- TAB 3: OPTIMIZATION ---
with tab3:
    st.header("Personalized SEO Strategy")
    if not st.session_state.channel_videos or not st.session_state.global_keywords:
        st.info("Please fetch 'Global Trends' (Tab 1) and 'Scan Channel' (Tab 2) first.")
    else:
        trending_set = {word for word, count in st.session_state.global_keywords}
        
        for v in st.session_state.channel_videos:
            with st.expander(f"Optimize: {v['snippet']['title']}"):
                title = v['snippet']['title']
                desc = v['snippet']['description']
                tags = v['snippet'].get('tags', [])
                
                score = 0
                if 50 <= len(title) <= 70: score += 40
                if len(desc) > 250: score += 30
                if len(tags) > 10: score += 30
                
                st.metric("SEO Health Score", f"{score}/100")
                
                my_words = set([w[0] for w in extract_keywords(title + desc)])
                matches = my_words.intersection(trending_set)
                
                if matches:
                    st.success(f"Trending keywords found in your metadata: {', '.join(matches)}")
                else:
                    st.warning("No global trending keywords found in your current metadata.")
                
                st.subheader("Copy these into your tags or description:")
                suggested = [w for w, c in st.session_state.global_keywords[:10]]
                st.code(", ".join(suggested))

st.divider()
st.caption("Developed for Daily Global SEO | Refresh Trends every 24 hours")