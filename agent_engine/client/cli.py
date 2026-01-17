"""CLI for Agent Engine client using click."""

import asyncio
import logging
import os
import sys

import click
from dotenv import load_dotenv

from client import AgentEngineClient

DEFAULT_AGENT_ID = (
    "projects/282268751691/locations/us-central1/reasoningEngines/6133389220548444160"
)


def setup_logging(verbose: int) -> None:
    """Configure logging based on verbosity level."""
    if verbose >= 2:
        level = logging.DEBUG
    elif verbose == 1:
        level = logging.INFO
    else:
        level = logging.WARNING

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def get_client(ctx: click.Context) -> AgentEngineClient:
    """Get or create the AgentEngineClient from context."""
    if "client" not in ctx.obj:
        ctx.obj["client"] = AgentEngineClient(
            agent_engine_id=ctx.obj["agent_id"],
            project=ctx.obj["project"],
            location=ctx.obj["location"],
        )
    return ctx.obj["client"]


def print_event(event) -> None:
    """Print a streaming event."""
    # Handle dict events (from Agent Engine API)
    if isinstance(event, dict):
        content = event.get("content", {})
        parts = content.get("parts", [])
        for part in parts:
            if isinstance(part, dict) and "text" in part:
                print(part["text"], end="", flush=True)
        return

    # Handle object events (with attributes)
    if hasattr(event, "content"):
        content = event.content
        if hasattr(content, "parts"):
            for part in content.parts:
                if hasattr(part, "text"):
                    print(part.text, end="", flush=True)
        elif isinstance(content, str):
            print(content, end="", flush=True)
    elif isinstance(event, str):
        print(event, end="", flush=True)


@click.group()
@click.option(
    "-a",
    "--agent-id",
    envvar="AGENT_ENGINE_ID",
    default=DEFAULT_AGENT_ID,
    help="Agent Engine resource path.",
)
@click.option(
    "-p",
    "--project",
    envvar="GOOGLE_CLOUD_PROJECT",
    help="GCP project ID.",
)
@click.option(
    "-l",
    "--location",
    default="us-central1",
    help="GCP region.",
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Enable verbose logging (-v for INFO, -vv for DEBUG).",
)
@click.pass_context
def cli(
    ctx: click.Context,
    agent_id: str,
    project: str | None,
    location: str,
    verbose: int,
) -> None:
    """Agent Engine CLI Client.

    Interact with deployed Agent Engine resources via command line.
    """
    load_dotenv()
    setup_logging(verbose)

    ctx.ensure_object(dict)
    ctx.obj["agent_id"] = agent_id
    ctx.obj["project"] = project
    ctx.obj["location"] = location


@cli.command()
@click.argument("message")
@click.option(
    "-u",
    "--user-id",
    required=True,
    help="User ID for the query.",
)
@click.option(
    "-s",
    "--session-id",
    help="Session ID. If not provided, a new session is created.",
)
@click.pass_context
def query(
    ctx: click.Context,
    message: str,
    user_id: str,
    session_id: str | None,
) -> None:
    """Send a query to the agent and stream the response.

    MESSAGE is the text to send to the agent.
    """
    client = get_client(ctx)

    async def run_query():
        async for event in client.query_stream(
            user_id=user_id,
            message=message,
            session_id=session_id,
        ):
            print_event(event)
        print()

    try:
        asyncio.run(run_query())
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.group()
def session() -> None:
    """Manage sessions."""
    pass


@session.command("create")
@click.option(
    "-u",
    "--user-id",
    required=True,
    help="User ID for the session.",
)
@click.pass_context
def session_create(ctx: click.Context, user_id: str) -> None:
    """Create a new session for a user."""
    client = get_client(ctx)

    async def run():
        result = await client.create_session(user_id=user_id)
        click.echo(f"Session created: {result}")

    try:
        asyncio.run(run())
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@session.command("list")
@click.option(
    "-u",
    "--user-id",
    required=True,
    help="User ID to list sessions for.",
)
@click.pass_context
def session_list(ctx: click.Context, user_id: str) -> None:
    """List all sessions for a user."""
    client = get_client(ctx)

    async def run():
        sessions = await client.list_sessions(user_id=user_id)
        if not sessions:
            click.echo("No sessions found.")
            return
        click.echo(f"Sessions for user '{user_id}':")
        for s in sessions:
            click.echo(f"  - {s}")

    try:
        asyncio.run(run())
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@session.command("get")
@click.option(
    "-u",
    "--user-id",
    required=True,
    help="User ID.",
)
@click.option(
    "-s",
    "--session-id",
    required=True,
    help="Session ID to retrieve.",
)
@click.pass_context
def session_get(ctx: click.Context, user_id: str, session_id: str) -> None:
    """Get details of a specific session."""
    client = get_client(ctx)

    async def run():
        result = await client.get_session(user_id=user_id, session_id=session_id)
        click.echo(f"Session: {result}")

    try:
        asyncio.run(run())
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@session.command("delete")
@click.option(
    "-u",
    "--user-id",
    required=True,
    help="User ID.",
)
@click.option(
    "-s",
    "--session-id",
    required=True,
    help="Session ID to delete.",
)
@click.confirmation_option(prompt="Are you sure you want to delete this session?")
@click.pass_context
def session_delete(ctx: click.Context, user_id: str, session_id: str) -> None:
    """Delete a session."""
    client = get_client(ctx)

    async def run():
        await client.delete_session(user_id=user_id, session_id=session_id)
        click.echo(f"Session '{session_id}' deleted.")

    try:
        asyncio.run(run())
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "-u",
    "--user-id",
    required=True,
    help="User ID for the session.",
)
@click.option(
    "-s",
    "--session-id",
    help="Session ID to resume. If not provided, a new session is created.",
)
@click.pass_context
def repl(ctx: click.Context, user_id: str, session_id: str | None) -> None:
    """Start an interactive REPL session with the agent."""
    client = get_client(ctx)
    current_session_id = session_id

    async def create_new_session():
        nonlocal current_session_id
        result = await client.create_session(user_id=user_id)
        current_session_id = result.get("id") if isinstance(result, dict) else str(result)
        return current_session_id

    async def process_query(message: str):
        async for event in client.query_stream(
            user_id=user_id,
            message=message,
            session_id=current_session_id,
        ):
            print_event(event)
        print()

    def print_help():
        click.echo("""
Commands:
  /help     - Show this help message
  /session  - Show current session info
  /new      - Start a new session
  /exit     - Exit the REPL (also: /quit, Ctrl+D)

Type any other text to chat with the agent.
""")

    def print_session_info():
        click.echo(f"\nSession Info:")
        click.echo(f"  User ID:    {user_id}")
        click.echo(f"  Session ID: {current_session_id}")
        click.echo(f"  Agent:      {ctx.obj['agent_id']}\n")

    async def run_repl():
        nonlocal current_session_id

        # Create session if not provided
        if not current_session_id:
            click.echo("Creating new session...")
            await create_new_session()

        click.echo("\n" + "=" * 50)
        click.echo("Agent Engine Interactive REPL")
        click.echo("=" * 50)
        click.echo(f"User: {user_id}")
        click.echo(f"Session: {current_session_id}")
        click.echo("Type /help for commands, /exit to quit")
        click.echo("=" * 50 + "\n")

        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.startswith("/"):
                    cmd = user_input.lower()
                    if cmd in ("/exit", "/quit"):
                        click.echo("Goodbye!")
                        break
                    elif cmd == "/help":
                        print_help()
                    elif cmd == "/session":
                        print_session_info()
                    elif cmd == "/new":
                        click.echo("Creating new session...")
                        await create_new_session()
                        click.echo(f"New session: {current_session_id}\n")
                    else:
                        click.echo(f"Unknown command: {user_input}")
                    continue

                # Send query to agent
                click.echo("\nAgent: ", nl=False)
                await process_query(user_input)
                click.echo()

            except EOFError:
                click.echo("\nGoodbye!")
                break
            except KeyboardInterrupt:
                click.echo("\n(Use /exit to quit)")

    try:
        asyncio.run(run_repl())
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def main() -> None:
    """Entry point."""
    cli()


if __name__ == "__main__":
    main()
