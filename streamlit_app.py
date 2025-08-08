import streamlit as st
import requests
import os
import json

st.set_page_config(page_title="RAG Chatbot", page_icon="🤖", layout="wide")

st.title("📄 RAG Chatbot")
st.caption("A Streamlit chat UI for your FastAPI RAG backend")

# Define backend endpoints
CHAT_URL = "http://127.0.0.1:8000/api/chat/"
UPLOAD_URL = "http://127.0.0.1:8000/api/upload/"

def send_chat_message(prompt: str):
    """Helper function to send a message to the chat backend and display the response."""
    # Note: We don't add the user prompt to the history here because the calling function does it.
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            history_for_api = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            payload = {"messages": history_for_api}
            
            with requests.post(CHAT_URL, json=payload, stream=True) as r:
                r.raise_for_status()
                for chunk in r.iter_content(chunk_size=None):
                    if chunk:
                        decoded_chunk = chunk.decode('utf-8')
                        if decoded_chunk.startswith('data: '):
                            try:
                                data_str = decoded_chunk[6:].strip()
                                if data_str == '[DONE]':
                                    break
                                if data_str:
                                    data = json.loads(data_str)
                                    if data.get('content'):
                                        full_response += data['content']
                                        message_placeholder.markdown(full_response + "▌")
                            except json.JSONDecodeError:
                                pass # Ignore non-json data chunks
            message_placeholder.markdown(full_response)
        except requests.exceptions.RequestException as e:
            full_response = f"Error connecting to the backend: {e}"
            message_placeholder.error(full_response)
        except Exception as e:
            full_response = f"An unexpected error occurred: {e}"
            message_placeholder.error(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Initialize session state variables
if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! Please ask a question about the document you want to analyze."}]
# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Main App Logic ---

# Sidebar for file uploads
with st.sidebar:
    st.header("Upload Documents")
    uploaded_files = st.file_uploader(
        "Upload one or more JSON files", 
        type=['json'], 
        accept_multiple_files=True,
        key="file_uploader"
    )
    if uploaded_files:
        # Create a new list for files that haven't been processed yet
        if 'processed_files' not in st.session_state:
            st.session_state.processed_files = []

        new_files_to_process = [f for f in uploaded_files if f.file_id not in st.session_state.processed_files]

        for uploaded_file in new_files_to_process:
            with st.spinner(f'Uploading and processing {uploaded_file.name}...'):
                try:
                    files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    response = requests.post(UPLOAD_URL, files=files)
                    response.raise_for_status()
                    st.success(f"Successfully processed `{uploaded_file.name}`.")
                    # Add a message to the chat history and mark as processed
                    st.session_state.messages.append({"role": "assistant", "content": f"I have successfully processed `{uploaded_file.name}`. You can now ask questions about it."})
                    st.session_state.processed_files.append(uploaded_file.file_id)
                except requests.exceptions.RequestException as e:
                    st.error(f"Error uploading {uploaded_file.name}: {e}")
        
        # Rerun to display the new messages in the chat
        if new_files_to_process:
            st.rerun()

# Main chat interface
if prompt := st.chat_input("Ask a question about your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    send_chat_message(prompt)
