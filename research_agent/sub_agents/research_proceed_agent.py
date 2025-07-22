import os

from google.adk.agents import Agent, SequentialAgent
from google.adk.tools import google_search


research_plan_agent = Agent(
    name="research_plan_agent",
    model="gemini-2.5-pro",
    description=(
        "Research process planner."
    ),
    instruction=(
        "Analyze the user's query and responses from the research clarifier agent and plan the research process."
        "Think ultra hard and come up with a plan that is as detailed as possible."
    ),
)


search_ref_agent = Agent(
    name="search_ref_agent",
    model="gemini-2.5-pro",
    description=(
        "Search references agent."
    ),
    instruction=(
        "Search references as many as possible for research."
        "You can use the web search tool to search the web for information."
        "After searching, you should return the references in a list of strings."
    ),
    tools=[google_search],
)

extract_info_agent = Agent(
    name="extract_info_agent",
    model="gemini-2.5-pro",
    description="Extract relevant information from the references.",
    instruction=(
        "Think ultra hard to collect information from the searched references."
        "Then, extract key informations to write a report."
    ),
)

synthesize_agent = Agent(
    name="synthesize_agent",
    model="gemini-2.5-pro",
    description="Information synthesizer.",
    instruction=(
        "Think ultra hard to synthesize the collected information into a coherent report."
        "Plan the report structure."
    ),
)

write_report_agent = Agent(
    name="write_report_agent",
    model="gemini-2.5-pro",
    description="Draft report writer.",
    instruction=(
        "Think ultra hard to write the draft version of the report in markdown format."
        "Use simple and clear sentences."
    ),
)

review_agent = Agent(
    name="review_agent",
    model="gemini-2.5-pro",
    description="Report reviewer.",
    instruction=(
        "Think hard to review the report and make sure it is accurate and complete."
        "Response with the review feedback."
    ),
)


def write_report(filename: str, report: str):
    """
    Write the report to the file.
    Args:
        filename: The filename to write the report to.
        report: The report to write.
    """

    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)



final_agent = Agent(
    name="final_agent",
    model="gemini-2.5-pro",
    description="Final report writer.",
    instruction=(
        "Think hard to create a final report with the review feedback applied."
        "The final report should contain references at the end of the report."
        "Generate appropriate filename for the report and save it to the file."
    ),
    tools=[write_report],
)


research_proceed_agent = SequentialAgent(
    name="research_proceed_agent",
    description=(
        "Research proceeder."
    ),
    sub_agents=[
        research_plan_agent,
        search_ref_agent,
        extract_info_agent,
        synthesize_agent,
        write_report_agent,
        review_agent,
        final_agent,
    ],
)
