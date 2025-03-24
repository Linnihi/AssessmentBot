import streamlit as st
import openai
from docx import Document
import PyPDF2
from dotenv import load_dotenv
import json5
from datetime import datetime

# Load environment variables
load_dotenv()

# customized avatar
# user_avatar = "./customize/avatars/user.png"
# assistant_avatar = "./customize/avatars/assistant.jpeg"

def load_config(config_file):
    """Load configuration from a JSON5 file."""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json5.load(f)
        return config
    except Exception as e:
        st.error(f"Error loading configuration file: {str(e)}")
        return None

def save_config(config, filename):
    """Save configuration to a JSON5 file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json5.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Error saving configuration file: {str(e)}")
        return False

# Load default configuration
DEFAULT_CONFIG = load_config('customize/default_config.json5')
if not DEFAULT_CONFIG:
    st.error("Failed to load default configuration. Please check the configuration file.")
    st.stop()

# Initialize session state for configuration
if "config" not in st.session_state:
    st.session_state.config = DEFAULT_CONFIG.copy()
    openai.api_key = st.session_state.config["api_key"]

# Main chat interface
st.title(st.session_state.config["title"])

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add initial message from the bot
    st.session_state.messages.append({"role": "assistant", "content": st.session_state.config["initial_conversation"]})

# Initialize session state for knowledge base
if "knowledge_base" not in st.session_state:
    st.session_state.knowledge_base = ""

# Initialize session state for API key source
if "api_key_source" not in st.session_state:
    st.session_state.api_key_source = None  # Can be 'config' or 'manual'

# Initialize session state for selected model
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "gpt-3.5-turbo"


def extract_text_from_docx(file):
    doc = Document(file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text


def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text


def export_conversation():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"conversation_{timestamp}.txt"

    conversation_text = "Mental Health Assessment Conversation\n"
    conversation_text += "=" * 50 + "\n\n"

    for message in st.session_state.messages:
        role = "Assistant" if message["role"] == "assistant" else "Client"
        conversation_text += f"{role}:\n{message['content']}\n\n"

    return conversation_text, filename


# Sidebar
with st.sidebar:
    st.title("Settings")

    # Configuration upload
    st.markdown("### Configuration")
    config_file = st.file_uploader(
        "Upload Configuration File (JSON5)",
        type=["json5", "json"],
        help="Upload a JSON5 file containing custom prompts and settings. If no file is uploaded, default configuration will be used."
    )
    
    if config_file:
        try:
            config_content = config_file.getvalue().decode('utf-8')
            new_config = json5.loads(config_content)
            # Validate required fields
            required_fields = ["title", "system_role", "initial_conversation", "context_template"]
            if all(field in new_config for field in required_fields):
                st.session_state.config = new_config
                st.success("Configuration loaded successfully!")
                # Update title if changed
                st.title(st.session_state.config["title"])
                # Set API key if provided in config
                if "api_key" in new_config and new_config["api_key"]:
                    openai.api_key = new_config["api_key"]
            else:
                st.error("Configuration file is missing required fields.")
        except Exception as e:
            st.error(f"Error loading configuration file: {str(e)}")

    # Download current configuration
    with open('customize/default_config.json5', 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Download the modified template with current values
    st.download_button(
        label="Download Configuration",
        data=template_content,
        file_name="current_config.json5",
        mime="application/json",
        key="config_download"
    )

    # API Key input (only if not provided in config)
    if not st.session_state.config.get("api_key"):
        api_key = st.text_input("OpenAI API Key", type="password")
        if api_key:
            openai.api_key = api_key
            st.session_state.config["api_key"] = api_key
            st.session_state.api_key_source = "manual"

        st.markdown("""
        ⚠️ **WE DO NOT STORE YOUR OPENAI KEY.**
        
        Just paste your OpenAI API key here and we'll use it to power the chatbot.
        [Get your OpenAI API key](https://platform.openai.com/api-keys)
        """)
    else:
        st.info("API key is loaded from configuration file.")
        st.session_state.api_key_source = "config"

    # Model selection
    st.session_state.selected_model = st.selectbox(
        "Select Model",
        ["gpt-3.5-turbo", "gpt-4o", "gpt-4o-mini", "gpt-4", "gpt-4-turbo"],
        index=0
    )

    # Multiple file upload
    st.markdown("### Document Upload")

    # Initialize session state for uploaded files if not exists
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []

    uploaded_files = st.file_uploader(
        "Upload any relevant documents to provide context for the response.",
        type=["pdf", "docx"],
        accept_multiple_files=True
    )

    # Check if files were removed
    if len(uploaded_files) < len(st.session_state.uploaded_files):
        st.session_state.knowledge_base = ""
        st.session_state.uploaded_files = []
        if uploaded_files:
            st.info("Documents were removed. Please re-upload your documents.")
        else:
            st.info("All documents were removed.")

    # Update knowledge base if files are uploaded
    if uploaded_files:
        combined_text = ""
        for uploaded_file in uploaded_files:
            if uploaded_file.type == "application/pdf":
                text = extract_text_from_pdf(uploaded_file)
            else:
                text = extract_text_from_docx(uploaded_file)
            combined_text += f"\n--- Content from {uploaded_file.name} ---\n{text}\n"
        st.session_state.knowledge_base = combined_text
        st.session_state.uploaded_files = uploaded_files
        st.success(f"Processed {len(uploaded_files)} document(s) successfully!")

# Add export button in the top right
col1, col2, col3 = st.columns([1, 5, 1])
with col1:
    if st.button("Restart", type="primary"):
        # Reset messages to initial state
        st.session_state.messages = []
        st.session_state.messages.append({"role": "assistant", "content": st.session_state.config["initial_conversation"]})
        st.rerun()

with col3:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"conversation_{timestamp}.txt"

    conversation_text = "Mental Health Assessment Conversation\n"
    conversation_text += "=" * 50 + "\n\n"

    for message in st.session_state.messages:
        role = "Assistant" if message["role"] == "assistant" else "User"
        conversation_text += f"{role}:\n{message['content']}\n\n"

    st.download_button(
        label="Export",
        data=conversation_text,
        file_name=filename,
        mime="text/plain"
    )

# Display chat messages with avatars
if 'user_avatar' in locals():
    avatar_user = user_avatar
else:
    avatar_user = None

if 'assistant_avatar' in locals():
    avatar_assistant = assistant_avatar
else:
    avatar_assistant = None

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=avatar_assistant if message["role"] == "assistant" else avatar_user):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your response here..."):
    # Check if we have a valid API key
    if not openai.api_key:
        st.error("Please provide an OpenAI API key in the sidebar.")
        st.stop()

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=avatar_user):
        st.markdown(prompt)

    # Prepare context with knowledge base if available
    context = ""
    if st.session_state.knowledge_base:
        context = st.session_state.config["context_template"].format(
            knowledge_base=st.session_state.knowledge_base,
            user_input=prompt
        )
    else:
        context = prompt

    # Get AI response
    try:
        # Create messages list with system role and chat history
        messages = [{"role": "system", "content": st.session_state.config["system_role"]}]
        # Add all messages except the last user message (which we'll add with context)
        messages.extend(st.session_state.messages[:-1])
        # Add the current user message with context
        messages.append({"role": "user", "content": context})

        response = openai.chat.completions.create(
            model=st.session_state.selected_model,
            messages=messages
        )

        # Add assistant response to chat history
        assistant_message = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": assistant_message})

        with st.chat_message("assistant", avatar=avatar_assistant):
            st.markdown(assistant_message)

    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.info("Please check your OpenAI API key and try again.")
