from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()

# LangChain looks for OPEN_AI_KEY automatically
api_key = os.getenv("OPEN_AI_KEY")
gen_api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError(
        "API key not found! Please set OPEN_AI_KEY in your .env file")


# Initialize model
model = ChatOpenAI(model="gpt-4o", api_key=api_key)
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=gen_api_key)



prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content="""You are an AI Cricket Assistant.

    - Only answer questions related to cricket (matches, players, rules, history, records, strategies, etc.).
    - If the user asks something  irrelevant to cricket, reply: "I only answer cricket-related questions."
    - Do not add explanations unless the user specifically asks for details."""),
   
    HumanMessage(content="{question}")
])

chain = prompt | model

response = chain.invoke({"question": "what is ODI in cricket answer one line"})

print(response.content)