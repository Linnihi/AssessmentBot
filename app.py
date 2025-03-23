import streamlit as st
import openai
from docx import Document
import PyPDF2
from dotenv import load_dotenv
from customize.prompts import TITLE, SYSTEM_ROLE, INITIAL_CONVERSATION, CONTEXT_TEMPLATE
from datetime import datetime

# Load environment variables
load_dotenv()

# customized avatar
# user_avatar = "./customize/avatars/user.png"
# assistant_avatar = "./customize/avatars/assistant.jpeg"

# Main chat interface
st.title(TITLE)

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add initial message from the bot
    st.session_state.messages.append({"role": "assistant", "content": INITIAL_CONVERSATION})

# Initialize session state for knowledge base
if "knowledge_base" not in st.session_state:
    st.session_state.knowledge_base = ""

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

    api_key = st.text_input("OpenAI API Key", type="password")
    if api_key:
        openai.api_key = api_key

    st.markdown("""
    ⚠️ **WE DO NOT STORE YOUR OPENAI KEY.**
    
    Just paste your OpenAI API key here and we'll use it to power the chatbot.
    [Get your OpenAI API key](https://platform.openai.com/api-keys)
    """)

    # Model selection
    st.session_state.selected_model = st.selectbox(
        "Select Model",
        ["gpt-3.5-turbo", "gpt-4o", "gpt-4o-mini", "gpt-4", "gpt-4-turbo"],
        index=0
    )

    # Multiple file upload
    st.markdown("### Document Upload")

    uploaded_files = st.file_uploader(
        "Upload any relevant documents to provide context for the response.",
        type=["pdf", "docx"],
        accept_multiple_files=True
    )

    if uploaded_files:
        combined_text = ""
        for uploaded_file in uploaded_files:
            if uploaded_file.type == "application/pdf":
                text = extract_text_from_pdf(uploaded_file)
            else:
                text = extract_text_from_docx(uploaded_file)
            combined_text += f"\n--- Content from {uploaded_file.name} ---\n{text}\n"
        st.session_state.knowledge_base = combined_text
        st.success(f"Processed {len(uploaded_files)} document(s) successfully!")

# Add export button in the top right
col1, col2 = st.columns([6, 1])
with col2:
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
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=avatar_user):
        st.markdown(prompt)

    # Prepare context with knowledge base if available
    context = ""
    if st.session_state.knowledge_base:
        context = CONTEXT_TEMPLATE.format(knowledge_base=st.session_state.knowledge_base, user_input=prompt)
    else:
        context = prompt

    # Get AI response
    try:
        # Create messages list with full chat history
        messages = [{"role": "system", "content": SYSTEM_ROLE}]
        messages.extend(st.session_state.messages)
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
