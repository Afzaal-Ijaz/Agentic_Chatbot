
from typing import Annotated
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
    
# Define classify_query node (that classify user query in travel query or not)
def classify_query(state: State):
    """Classify user intent"""
     # take user query 
    user_message = state["messages"]
    
    messages = [
        SystemMessage(content=classifier_prompt), user_message]
    response = llm.invoke(messages)
    return {"messages": [response]}

# Define chat node (that response to user on travel reletad queries)
def chat_node(state: State):
    # take user query 
    message = state['messages']
    
    # send to llm
    response = llm.invoke(message)
    
    # response store in state
    return {'messages': [response]}

# ✅ Define irrelevent node (for non-travel queries)
def irrelevent_node(state:State):
    return {
        "messages": [
            HumanMessage(
                content="Sorry, I can only assist with travel-related queries like flights, hotels, and destinations."
            )
        ]
    }
    
    
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
graph.add_node('chat_node', chat_node)

# add edges
graph.add_edge(START,'chat_node')
graph.add_edge('chat_node',END)


chatbot = graph.compile(checkpointer=checkpointer)
# config1 = {"configurable": {'thread_id': thread_id}}

# initial_state = {
#      'messages': [HumanMessage(content='define bike in one line')]
# }

# res = chatbot.invoke(initial_state, config=config1)['messages'][-1].content
# print(res)