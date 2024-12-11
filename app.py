# app.py
import os
from datetime import datetime
import uuid

import requests
import streamlit as st

# Configure page settings
st.set_page_config(
    page_title="ChatDocs",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
API_BASE_URL = "http://localhost:8000"
ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.txt']

def init_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'session_id' not in st.session_state or not st.session_state.session_id:
        st.session_state.session_id = str(uuid.uuid4())  # Always ensure a valid session ID
    if 'documents' not in st.session_state:
        st.session_state.documents = []
    if 'api_key_set' not in st.session_state:
        st.session_state.api_key_set = False

def fetch_documents():
    """Fetch all documents from the API"""
    try:
        response = requests.get(f"{API_BASE_URL}/listDocs")
        if response.ok:
            st.session_state.documents = response.json()
    except Exception as e:
        st.error(f"Failed to fetch documents: {str(e)}")

def delete_document(file_id):
    """Delete a document using the API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/deleteDoc",
            json={"fileId": file_id}
        )
        if response.ok:
            st.success("Document deleted successfully")
            fetch_documents()
        else:
            st.error("Failed to delete document")
    except Exception as e:
        st.error(f"Error deleting document: {str(e)}")

def upload_document(files):
    """Upload one or more documents using the API"""
    if not files:
        return
    
    # Convert to list if single file
    if not isinstance(files, list):
        files = [files]
    
    for file in files:
        # Check file extension
        file_extension = os.path.splitext(file.name)[1].lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            st.error(f"Unsupported file type for {file.name}. Allowed types are: {', '.join(ALLOWED_EXTENSIONS)}")
            continue

        try:
            files_data = {"file": (file.name, file, "application/octet-stream")}
            response = requests.post(f"{API_BASE_URL}/uploadDoc", files=files_data)
            
            if response.ok:
                st.success(f"File {file.name} uploaded successfully")
            else:
                st.error(f"Failed to upload {file.name}")
        except Exception as e:
            st.error(f"Error uploading {file.name}: {str(e)}")
    
    fetch_documents()

def send_message(message, model):
    """Send a message to the chat API and stream the response"""
    try:
        # Ensure session_id exists before sending
        if not st.session_state.session_id:
            st.session_state.session_id = str(uuid.uuid4())
            
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            # Show thinking animation
            with message_placeholder:
                with st.status("🤔 Thinking...", expanded=False) as status:
                    st.write("Searching through documents...")
                    
                    # Make streaming request with existing session ID
                    with requests.post(
                        f"{API_BASE_URL}/chat",
                        json={
                            "question": message,
                            "sessionId": st.session_state.session_id, 
                            "model": model
                        },
                        stream=True
                    ) as response:
                        
                        if response.ok:
                            # Clear the thinking status
                            status.update(label="Found relevant information!", state="complete", expanded=False)
                            
                            # Stream the response
                            full_response = ""
                            for chunk in response.iter_content(decode_unicode=True):
                                if chunk:
                                    full_response += chunk
                                    message_placeholder.markdown(full_response + "▌")
                            
                            # Show final response without cursor
                            message_placeholder.markdown(full_response)
                            return full_response
                        else:
                            status.update(label="Error occurred", state="error")
                            st.error("Failed to get response from the assistant")
                            return None
                
    except Exception as e:
        st.error(f"Error sending message: {str(e)}")
        return None

def clear_all_documents():
    """Clear all documents from the system"""
    try:
        response = requests.post(f"{API_BASE_URL}/clearAllDocs")
        if response.ok:
            st.success("All documents cleared successfully")
            fetch_documents()  # Refresh the document list
        else:
            st.error("Failed to clear documents")
    except Exception as e:
        st.error(f"Error clearing documents: {str(e)}")

def set_api_key(api_key):
    """Set the OpenAI API key"""
    try:
        response = requests.post(f"{API_BASE_URL}/setApiKey", params={"api_key": api_key})
        if response.ok:
            st.session_state.api_key_set = True
            return True
        return False
    except Exception as e:
        st.error(f"Error setting API key: {str(e)}")
        return False

def main():
    # Initialize session state
    init_session_state()
    
    # Create top layout with just title
    st.title("ChatDocs")
    
    # Create sidebar
    with st.sidebar:
        st.header("Current Session")
        st.caption(f"ID: {st.session_state.session_id[:8]}...")
        if st.button("➕ New Session", type="secondary", help="Start a new chat session"):
            st.session_state.messages = []
            st.session_state.session_id = str(uuid.uuid4())
            st.rerun()
        st.divider()

        # API Key input at the very top
        st.header("OpenAI API")
        api_key = st.text_input("Enter your OpenAI API key", type="password")
        if api_key and not st.session_state.api_key_set:
            if set_api_key(api_key):
                st.success("API key set successfully!")
            else:
                st.error("Failed to set API key")        

        # Model selection
        model = st.selectbox(
            "Choose Model",
            ["gpt-4o-mini", "gpt-4o"],
            index=0
        )
        
        st.divider()
        
        st.header("Manage Docs")
        
        # Upload section
        uploaded_files = st.file_uploader(
            "Select Documents",
            type=['pdf', 'docx', 'txt'],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            if st.button("Upload Docs", type="primary"):
                upload_document(uploaded_files)
        
        # Documents section
        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("Loaded Docs -")
        
        with col2:    
            if st.button("🔄 Refresh List", key="refresh_docs"):
                fetch_documents()
        
        # Display documents
        for doc in st.session_state.documents:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.text(doc['filename'])
                st.caption(f"{datetime.fromisoformat(doc['uploadTimestamp']).strftime('%Y-%m-%d %H:%M')}")
            with col2:
                if st.button("🗑️", key=f"del_{doc['id']}"):
                    delete_document(doc['id'])
        
        st.divider()
        

        if st.button("🗑️ Delete all docs", key="remove_docs", type="primary"):
            if st.session_state.documents:
                if st.warning("Remove all documents?"):
                    clear_all_documents()
            else:
                st.info("No documents to remove")

    # Only show chat interface if API key is set
    if not st.session_state.api_key_set:
        st.warning("Please enter your OpenAI API key in the sidebar to continue.")
        return

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Get and display streaming response
        response = send_message(prompt, model)
        if response:
            st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()