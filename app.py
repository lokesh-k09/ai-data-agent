import streamlit as st
import pandas as pd
import os
import time
from agent import run_agent

st.set_page_config(page_title="AI Data Agent", page_icon="🤖", layout="wide")
st.title("🤖 Agentic AI Data Analyst")

with st.sidebar:
    st.header("📁 Data Control")
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    
    if uploaded_file:
        file_name = uploaded_file.name
        with open(file_name, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state.current_file = file_name
        st.success(f"Loaded: {file_name}")
        st.dataframe(pd.read_csv(file_name).head(3))
    
    st.divider()
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        if "current_file" in st.session_state:
            del st.session_state.current_file
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "image" in msg and os.path.exists(msg["image"]):
            st.image(msg["image"])

if prompt := st.chat_input("What would you like to analyze?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Agent is reasoning and executing..."):
            active_file = st.session_state.get("current_file")
            result = run_agent(prompt, filename=active_file)
            
            if result:
                st.markdown(result)
                msg_entry = {"role": "assistant", "content": result}
                
                if os.path.exists("output_plot.png"):
                    unique_name = f"plot_{int(time.time())}.png"
                    os.rename("output_plot.png", unique_name)
                    st.image(unique_name)
                    msg_entry["image"] = unique_name
                
                st.session_state.messages.append(msg_entry)
            else:
                st.error("Terminal execution error. Check your API key or data source.")