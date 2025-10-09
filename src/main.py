import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Minimal model list for selection
AVAILABLE_MODELS = [
    "gpt-4o-mini",
    "gpt-4o",
    "gpt-4",
    "gpt-3.5-turbo",
]

st.set_page_config(page_title="Basic Chat", page_icon="💬")

# Initialize OpenAI client factory function (will be called per-request)
def make_client():
    # Try Streamlit secrets first, then environment variables
    api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not found in Streamlit secrets or environment variables")
    return OpenAI(api_key=api_key)

# Session state initialization
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

if "system_message" not in st.session_state:
    st.session_state.system_message = "You are a helpful assistant."

if "show_config" not in st.session_state:
    st.session_state.show_config = False

if "input_counter" not in st.session_state:
    st.session_state.input_counter = 0

# Configuration screen
if st.session_state.show_config:
    st.title("Configuration")
    
    # System message configuration
    new_system_message = st.text_area(
        "System Message",
        value=st.session_state.system_message,
        height=100,
        help="This message controls how the AI behaves. It's sent as the first message in every conversation."
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save & Return"):
            st.session_state.system_message = new_system_message
            # Update the first message in the conversation
            st.session_state.messages[0] = {"role": "system", "content": new_system_message}
            st.session_state.show_config = False
            st.rerun()
    
    with col2:
        if st.button("Cancel"):
            st.session_state.show_config = False
            st.rerun()
    
    st.stop()

# Main chat interface
st.title("Minimal OpenAI Chat")

with st.sidebar:
    st.header("Settings")
    model = st.selectbox("Model", AVAILABLE_MODELS, index=AVAILABLE_MODELS.index("gpt-4o-mini") if "gpt-4o-mini" in AVAILABLE_MODELS else 0)
    
    if st.button("⚙️ Configure"):
        st.session_state.show_config = True
        st.rerun()
    
    # Check API key from both sources
    api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if api_key:
        st.success("API key configured")
    else:
        st.error("API key not found. Add OPENAI_API_KEY to Streamlit secrets or environment variables.")

# Chat display
st.subheader("Conversation")
for msg in st.session_state.messages:
    if msg["role"] == "system":
        # hide system messages from display
        continue
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**Assistant:** {msg['content']}")

# Input area - use a unique key that changes when we want to clear
user_input = st.text_input(
    "Message", 
    key=f"user_input_{st.session_state.input_counter}"
)

col1, col2 = st.columns([1, 4])
with col1:
    send = st.button("Send")
with col2:
    clear = st.button("Clear Chat")

if clear:
    st.session_state.messages = [{"role": "system", "content": st.session_state.system_message}]
    st.session_state.input_counter += 1  # This will create a new input widget
    st.rerun()

if send and user_input:
    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    try:
        client = make_client()
        with st.spinner("Waiting for assistant..."):
            response = client.chat.completions.create(
                model=model,
                messages=st.session_state.messages
            )
        assistant_text = response.choices[0].message.content
    except Exception as e:
        assistant_text = f"[Error] {e}"

    # Append assistant response
    st.session_state.messages.append({"role": "assistant", "content": assistant_text})

    # Clear input by incrementing counter (creates new widget)
    st.session_state.input_counter += 1

    # Rerun so the conversation display updates
    st.rerun()
