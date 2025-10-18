
from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from utils.llm import llm, classifier_llm
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from prompts.system_prompt import classifier_prompt
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import ToolNode,tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from services.amadeus_service import AmadeusService
from services.weather_service import WeatherService

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
    - "Tell me about Lahore,Karachi, Turkye, USA, China or any place" → relevant
    - "find weather of any place to plan a trip" → relevant
    - "PIA available flights today " → relevant
    - "write a Python script or any type of code" → irrelevant
    - "define computer, AI workflow or any question releted to computer" → irrelevant
    - "recipe of foods" → irrelevant
    - "who is Virat Kohli, Imran Khan or any popular personality" → irrelevant
    - "what is the popular news today" → irrelevant

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
    response = llm_with_tools.invoke(message)
    
    # response store in state
    return {'messages': [response]}

# ✅ Define irrelevent node (for non-travel queries)
def irrelevant_node(state:State):
    return {
        "messages": [
            HumanMessage(
                content="Sorry, I can only assist with travel-related queries like flights, hotels,tour planing and destinations."
            )
        ]
    }
    
def check_condition(state: State) -> Literal["chat_node", "irrelevant_node"]:
    
    if state['intent'] == 'relevant':
        return 'chat_node'
    else:
        return 'irrelevant_node'  
       
    
   
    
#tools
def duck_search(query:str)  -> str:
    """Searches websites to answer the user queries using DuckDuckGoSearchRun."""
    duck_tool = DuckDuckGoSearchRun()
    return duck_tool.invoke(query)
    
    
@tool("flight_search")
def flight_search(query: str) -> str:
    """Searches for flights from the user query."""
    try:
        flight_tool = AmadeusService(client_id=os.getenv("AMADEUS_CLIENT_ID"),client_secret=os.getenv("AMADEUS_CLIENT_SECRET"))
        parsed = flight_tool.parse_flight_query(query)
        return flight_tool.flight_search(parsed.origin, parsed.destination, parsed.date)
    except Exception as e:
        return "Try in date format like this YYYY-MM-DD (2025-12-29)."


@tool("weather_info")
def weather_check(city: str | dict) -> str:
    """Get current weather for a city or any place."""
    weather_tool = WeatherService()

    if isinstance(city, dict):
        city = city.get("city") or city.get("location") or list(city.values())[0]

    if not isinstance(city, str):
        return "⚠️ Please provide a valid city name."

    return weather_tool.get_weather(city)


tools = [duck_search,flight_search, weather_check]
llm_with_tools = llm.bind_tools(tools=tools)

tool_node = ToolNode(tools)

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
graph.add_node("tools",tool_node)

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

graph.add_conditional_edges("chat_node", tools_condition)
graph.add_edge("tools", "chat_node")
graph.add_edge("irrelevant_node", END)



chatbot = graph.compile(checkpointer=checkpointer)
# config1 = {"configurable": {'thread_id': thread_id}}
