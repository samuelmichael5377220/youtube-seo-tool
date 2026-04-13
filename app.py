import streamlit as st

# Basic Page Setup
st.set_page_config(page_title="SEO Tool", layout="wide")

st.title("YouTube SEO Tool: Online")
st.success("The server is running correctly!")

# Sidebar for the API Key
st.sidebar.header("Settings")
api_key = st.sidebar.text_input("YouTube API Key", type="password")

if api_key:
    st.write("API Key received. You can now proceed to fetch trends.")
else:
    st.info("Please enter your API Key in the sidebar to start.")

# Simple Tab structure to test navigation
tab1, tab2 = st.tabs(["Trends", "About"])
with tab1:
    st.write("Trending data will appear here once the full script is restored.")
with tab2:
    st.write("This tool is configured for @RandomVid-m5x")
