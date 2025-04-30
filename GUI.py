import streamlit as st
import back_end
import streamlit.components.v1 as components

if "response" not in st.session_state:
    st.session_state.response = ""
if "url" not in st.session_state:
    st.session_state.url = ""
if "company" not in st.session_state:
    st.session_state.company = ""

st.markdown("<h1 style='text-align: center; color: white;'>Truth On Demand</h1>", unsafe_allow_html=True)
st.header(" ", divider="violet")

if st.session_state.response == "":
    st.session_state.company = st.text_input(label=" ", placeholder="Name of News Company")
    st.session_state.url = st.text_input(label=" ", placeholder="URL")
    if st.button("Submit"):
        with st.spinner("Loading..."):
            st.session_state.response = "hex"
            st.rerun()
else:
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.response = back_end.stream_brochure(st.session_state.company, st.session_state.url)
        
    with col2:
        if st.session_state.url != "":
            components.iframe(st.session_state.url, width=800, height=600, scrolling=True)
    
    if st.button("Restart"):
        st.session_state.response = ""
        st.session_state.url = ""
        st.session_state.company = ""
        st.rerun()