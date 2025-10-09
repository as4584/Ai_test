# Streamlit OpenAI Integration Guide

This guide explains how to set up and run our Streamlit application that integrates with OpenAI.

## Prerequisites

- Python 3.10 or higher
- Virtual environment (venv)
- OpenAI API key

## Setup

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd IS218model
   ```

2. **Environment Setup**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```

3. **Install Dependencies**
   ```bash
   pip install streamlit openai
   ```

4. **Set Up Environment Variables**
   Create a `.env` file in the root directory (make sure to add it to .gitignore):
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

## Running the Application

1. **Start the Streamlit App**
   ```bash
   streamlit run src/main.py
   ```

2. **Access the Application**
   - The app will automatically open in your default web browser
   - If it doesn't, you can access it at `http://localhost:8501`

## Features

- Simple web interface for interacting with OpenAI's GPT model
- Real-time responses from the AI
- Clean and intuitive user interface

## Project Structure

```
IS218model/
├── .venv/                  # Virtual environment
├── src/
│   └── main.py            # Main Streamlit application
├── STREAMLIT_GUIDE.md     # This guide
└── requirements.txt       # Project dependencies
```

## Troubleshooting

1. **API Key Issues**
   - Make sure your OpenAI API key is correctly set in the `.env` file
   - Verify the environment variable is being loaded correctly

2. **Streamlit Connection Issues**
   - Check if the port 8501 is available
   - Ensure you're running the command from the correct directory

## Development

To modify the application:
1. Edit `src/main.py` to add new features or modify existing ones
2. Streamlit will automatically reload when you save changes
3. Use `st.write()` for debug output during development