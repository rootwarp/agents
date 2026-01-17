from google.adk.agents import Agent
from google.adk.tools import google_search


root_agent = Agent(
    name="hello_world",
    #model="gemini-3-pro-preview",
    model="gemini-2.5-flash",
    description="A friendly chatbot that can search the web for information.",
    instruction=(
        "You are a helpful and friendly assistant. "
        "You can answer questions and search the web for information when needed. "
        "Use the google_search tool to find current information about topics the user asks about. "
        "Be concise, accurate, and helpful in your responses."
    ),
    tools=[google_search],
)
