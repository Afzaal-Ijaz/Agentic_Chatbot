
from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from utils.llm import llm, classifier_llm
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from prompts.system_prompt import classifier_prompt
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import ToolNode,tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
import os
import requests
import sqlite3

os.environ["GRPC_VERBOSITY"] = "NONE"
os.environ["GLOG_minloglevel"] = "3"


#define State
class State(TypedDict):
    
    messages: Annotated[list[BaseMessage], add_messages]
    intent : str
    
# Define classify_query node (that classify user query in travel query or not)
def classify_node(state: State)->Literal["relevent", "irrelevent"]:
    user_message = state["messages"]

    classifier_prompt = f"""
    You are a strict classifier that decides whether a user query is related to travel.

    Return only one word:
    - "relevant" — if the query is about flights, hotels, trip planning, destinations, travel recommendations, weather for trips, etc.
    - "irrelevant" → if the query is about anything else like computers, AI, coding, sports, health, or general questions.


    Examples:
    - "book me a flight to Dubai" → relevant
    - "best hotels in London" → relevant
    - "weather in Paris for next week" → relevant
    - "how to plan a vacation" → relevant
    - "explain AI workflow" → irrelevant
    - "write a Python script" → irrelevant
    - "define computer" → irrelevant
    - "explain AI workflow" → irrelevant
    - "write a Python script" → irrelevant
    - "who is Virat Kohli" → irrelevant
    - "what is machine learning" → irrelevant

    User query: {user_message}

    Answer with only one label: relevant or irrelevant.
    """


    prompt = [
    SystemMessage(content="You are a strict classifier for travel-related queries."),
    HumanMessage(content=classifier_prompt)
    ]

    # invoke model
    response = classifier_llm.invoke(prompt)
    intent = response.content.lower().strip()
    
    return {'intent': intent}


# Define chat node (that response to user on travel reletad queries)
def chat_node(state: State):
    # take user query 
    message = state['messages']
    
    # send to llm
    response = llm.invoke(message)
    
    # response store in state
    return {'messages': [response]}

# ✅ Define irrelevent node (for non-travel queries)
def irrelevant_node(state:State):
    return {
        "messages": [
            HumanMessage(
                content="Sorry, I can only assist with travel-related queries like flights, hotels, and destinations."
            )
        ]
    }
    
def check_condition(state: State) -> Literal["chat_node", "irrelevant_node"]:
    
    if state['intent'] == 'relevant':
        return 'chat_node'
    else:
        return 'irrelevant_node'  
       
    
   
    

duck_tool = DuckDuckGoSearchRun()
# print(duck.invoke("current weather in Lahore in Celcius degree"))


# agent = create_react_agent(
#     model="llm",
#     tools=[duck_tool],
#     prompt="You are a helpful travel agent assistant"
# )

# # Run the agent
# agent.invoke(
#     {"messages": [{"role": "user", "content": "what is the computer in one line"}]}
# )

# print(State[messages])

# Path to your existing database folder
db_path = os.path.join(os.path.dirname(__file__), "..", "database", "chat.db")
conn = sqlite3.connect(database=db_path ,check_same_thread=False)

checkpointer = SqliteSaver(conn=conn)
# thread_id = '1'

graph = StateGraph(State)

#add nodes
graph.add_node("classifier_node", classify_node)
graph.add_node("chat_node", chat_node)
graph.add_node("irrelevant_node", irrelevant_node)

#add edges
graph.add_edge(START, "classifier_node")

graph.add_conditional_edges(
    "classifier_node",
    check_condition,
    {
        "chat_node": "chat_node",
        "irrelevant_node": "irrelevant_node"
    }
)

graph.add_edge("chat_node", END)
graph.add_edge("irrelevant_node", END)



chatbot = graph.compile(checkpointer=checkpointer)
# config1 = {"configurable": {'thread_id': thread_id}}
