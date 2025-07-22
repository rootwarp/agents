import os

from google.adk.agents import Agent, SequentialAgent
from research_agent.sub_agents.research_clarifier_agent import research_clarifier_agent
from research_agent.sub_agents.research_proceed_agent import research_proceed_agent



root_agent = Agent(
    name="research_agent_orchestrator",
    model="gemini-2.5-pro",
    description=(
        "A research agent orchestrator that can delegate tasks to other agents"
    ),
    instruction=(
        "You are a research agent that can search the web for information."
    ),
    sub_agents=[
        research_clarifier_agent,
        research_proceed_agent,
    ],
)
