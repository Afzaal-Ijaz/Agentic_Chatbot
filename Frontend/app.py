
import os
import sys
import importlib.util
import streamlit as st 
from langchain_core.messages import HumanMessage
from agents.travel_agent import chatbot


#  Add parent directory (project root) to import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

#  Dynamically import travel_agent.py no matter how Streamlit runs
agent_path = os.path.join(os.path.dirname(__file__), "..", "agents", "travel_agent.py")
spec = importlib.util.spec_from_file_location("travel_agent", agent_path)
travel_agent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(travel_agent)

#  Access chatbot object from travel_agent.py
chatbot = travel_agent.chatbot

# ---------------- Streamlit UI ----------------
user_input = st.chat_input('Type here')

# Session state setup
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []
    

# thread_id = '1'
CONFIG = {"configurable": {'thread_id': '1'}}

# Load conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

if user_input:
    # Add user message
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    # # Call chatbot (object from travel_agent.py)
    # ai_message = response['messages'][-1].content

    with st.chat_message('assistant'):
        ai_message = st.write_stream(
            message_chunk.content for message_chunk,metadata in  chatbot.stream(
             {'messages': [HumanMessage(content= user_input)]},
            config=CONFIG,
            stream_mode='messages'
            ) 
        )
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})