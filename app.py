import streamlit as st

st.title("SEO Tool Test")
st.write("If you can see this, the server is working perfectly!")

api_key = st.sidebar.text_input("Test API Key Input")
if api_key:
    st.write("Key detected!")
