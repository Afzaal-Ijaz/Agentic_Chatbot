
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage,HumanMessage
# from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode,tools_condition
# from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from dotenv import load_dotenv
import os
import requests
import random
os.environ["GRPC_VERBOSITY"] = "NONE"
os.environ["GLOG_minloglevel"] = "3"

load_dotenv()

# LangChain looks for OPEN_AI_KEY automatically
api_key = os.getenv("OPEN_AI_KEY")
gen_api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError(
        "API key not found! Please set OPEN_AI_KEY in your .env file")


# Initialize model
model = ChatOpenAI(model="gpt-4o-mini", api_key=api_key)
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=gen_api_key)

#define State
class State(TypedDict):
    
    messages: Annotated[list[BaseMessage], add_messages]


def chat_node(state: State):
    # take user query 
    message = state['messages']
    
    # send to llm
    response = llm.invoke(message)
    
    # response store in state
    return {'messages': [response]}
    
    
# duck_tool = DuckDuckGoSearchRun()


# agent = create_react_agent(
#     model="llm",
#     tools=[get_flights],
#     prompt="You are a helpful travel agent assistant"
# )

# # Run the agent
# agent.invoke(
#     {"messages": [{"role": "user", "content": "what is the computer in one line"}]}
# )

# print(State[messages])


graph = StateGraph(State)

#add nodes
graph.add_node('chat_node', chat_node)

# add edges
graph.add_edge(START,'chat_node')
graph.add_edge('chat_node',END)

checkpointer = MemorySaver()


chatbot = graph.compile(checkpointer=checkpointer)
config1 = {"configurable": {'thread_id': '1'}}

if __name__ == "__main__":
    initial_state = {
        'messages': [HumanMessage(content='define mobile in one line')]
    }

    res = chatbot.invoke(initial_state, config=config1)['messages'][-1].content
    print(res)
