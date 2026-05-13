from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct")

response = llm.invoke("What is the tallest building in the world?")
print(response.content)

llm = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct")

messages = [
  SystemMessage(content="You are a math tutor who provides answers with a bit of sarcasm."),
  HumanMessage(content="What is the square of 2?"),
]

response = llm.invoke(messages)
print(response.content)