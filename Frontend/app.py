from flask import Flask, render_template, request, jsonify
import os
import sys
import importlib.util

# Add parent directory (project root) to import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Dynamically import travel_agent.py
agent_path = os.path.join(os.path.dirname(__file__), "..", "agents", "travel_agent.py")
spec = importlib.util.spec_from_file_location("travel_agent", agent_path)
travel_agent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(travel_agent)

# Access chatbot object from travel_agent.py
chatbot = travel_agent.chatbot

app = Flask(__name__, template_folder='templates', static_folder='static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    
    # This is a simplified interaction. You might need to adapt this
    # based on how your travel_agent.py is structured.
    # This example assumes a simple call and response.
    # You may need to manage conversation history/state.
    
    from langchain_core.messages import HumanMessage
    
    CONFIG = {"configurable": {'thread_id': '1'}}
    
    # Get the response from the chatbot
    response = chatbot.invoke(
        {"messages": [HumanMessage(content=user_message)]},
        config=CONFIG,
    )
    # extract AI message
    ai_reply = response["messages"][-1].content

    # Process the generator to get the AI message content
    return jsonify({'response': ai_reply})

if __name__ == '__main__':
    app.run(debug=True)