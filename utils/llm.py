from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

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
classifier_llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key=gen_api_key)  # used only for classification