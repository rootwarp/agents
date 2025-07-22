from google.adk.agents import Agent


research_clarifier_agent = Agent(
    name="research_clarifier_agent",
    model="gemini-2.5-pro",
    description=(
        "Analyze the user's query and clarify the research question."
    ),
    instruction=(
        "Analyze the user's query and ask questions to clarify the research question."
    ),
)
