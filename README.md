# AssessmentBot

A Streamlit-based mental health assessment chatbot that uses OpenAI's API to provide preliminary mental health evaluations. The chatbot can incorporate knowledge from uploaded documents to provide more contextual responses.

## Features

- Interactive chat interface with context-aware prompts
- Support for multiple PDF and DOCX document uploads
- Secure API key handling (no storage)
- Persistent chat history during session
- Context-aware responses based on uploaded documents
- Export conversation history
- Multiple GPT model options
- Culturally sensitive and ethical mental health assessment

## Requirements

- Python 3.12.0
- OpenAI API key
- Required packages (see requirements.txt)

## Setup

1. Install the required packages:
```bash
pip install -r requirements.txt
```

2. Get your OpenAI API key from [OpenAI's website](https://platform.openai.com/api-keys)

## Running the Application

1. Start the Streamlit app:
```bash
streamlit run app.py
```

2. Open your web browser and navigate to the URL shown in the terminal (typically http://localhost:8501)

3. Enter your OpenAI API key in the sidebar
   - Note: Your API key is not stored and is only used for the current session
   - You can get an API key from [OpenAI's website](https://platform.openai.com/api-keys)

4. (Optional) Upload relevant documents (PDF or DOCX) to provide context for the assessment

5. Start the conversation with the AI assistant

## Usage

- The sidebar contains settings for your API key, model selection, and document upload
- The main area shows the chat interface
- Type your response in the chat input at the bottom
- The chatbot will respond based on the uploaded documents (if any) and the conversation history
- Use the "Export" button to download the conversation history

## Model Options

The application supports multiple GPT models:
- gpt-3.5-turbo
- gpt-4o
- gpt-4o-mini
- gpt-4
- gpt-4-turbo

## Important Notes

- This is not a substitute for professional mental health services
- The chatbot provides preliminary assessments only
- No medical advice or treatment is provided
- The conversation history can be exported for record-keeping
- Your OpenAI API key is not stored and is only used for the current session

## Security

- API keys are not stored and are only used for the current session
- All conversations are local to your browser
- Document uploads are processed locally and not stored 
