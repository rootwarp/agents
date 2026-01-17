# =============================================================================
# deploy_cli.py - Agent Engine CLI
# =============================================================================
import os

import click
import vertexai
from dotenv import load_dotenv
from vertexai import agent_engines

# Load environment variables from .env file
load_dotenv()

# Configuration
PROJECT_ID = os.getenv("HELLO_WORLD_PROJECT")
LOCATION = os.getenv("HELLO_WORLD_LOCATION")
STAGING_BUCKET = os.getenv("HELLO_WORLD_STAGING_BUCKET")
AGENT_ENGINE_ID = os.getenv("HELLO_WORLD_AGENT_ENGINE_ID")
DISPLAY_NAME = os.getenv("HELLO_WORLD_DISPLAY_NAME")
DESCRIPTION = os.getenv("HELLO_WORLD_DESCRIPTION")

# Requirements for the agent
REQUIREMENTS = [
    "google-adk",
    "google-cloud-aiplatform[agent_engines,adk]>=1.112.0",
    "cloudpickle>=3.0",
]


def get_env_vars():
    """Get environment variables for the deployed agent."""
    return {
        "LOG_LEVEL": os.getenv("HELLO_WORLD_LOG_LEVEL"),
        "GOOGLE_GENAI_USE_VERTEXAI": os.getenv(
            "HELLO_WORLD_GOOGLE_GENAI_USE_VERTEXAI"
        ),
        "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY": os.getenv(
            "HELLO_WORLD_GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY"
        ),
        "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": os.getenv(
            "HELLO_WORLD_OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"
        ),
    }


def load_agent():
    """Lazy load the agent to avoid import at module level."""
    from hello_world.agent import root_agent
    return root_agent


def validate_config():
    """Validate required configuration is set."""
    missing = []
    if not PROJECT_ID:
        missing.append("HELLO_WORLD_PROJECT")
    if not LOCATION:
        missing.append("HELLO_WORLD_LOCATION")
    if not STAGING_BUCKET:
        missing.append("HELLO_WORLD_STAGING_BUCKET")
    if not DISPLAY_NAME:
        missing.append("HELLO_WORLD_DISPLAY_NAME")
    if not DESCRIPTION:
        missing.append("HELLO_WORLD_DESCRIPTION")

    if missing:
        raise click.ClickException(
            f"Missing required environment variables: {', '.join(missing)}"
        )


def init_vertexai():
    """Initialize Vertex AI SDK."""
    vertexai.init(
        project=PROJECT_ID,
        location=LOCATION,
        staging_bucket=STAGING_BUCKET,
    )


@click.group()
def cli():
    """Agent Engine CLI for deploying and updating agents."""
    pass


@cli.command()
@click.option(
    "--dry-run",
    is_flag=True,
    help="Preview deployment without executing.",
)
def deploy(dry_run):
    """Deploy a new agent engine."""
    validate_config()

    if dry_run:
        click.echo("Dry run mode - deployment preview:")
        click.echo(f"  Project: {PROJECT_ID}")
        click.echo(f"  Location: {LOCATION}")
        click.echo(f"  Display name: {DISPLAY_NAME}")
        click.echo(f"  Description: {DESCRIPTION}")
        click.echo(f"  Requirements: {REQUIREMENTS}")
        click.echo(f"  Env vars: {list(get_env_vars().keys())}")
        return

    init_vertexai()
    root_agent = load_agent()

    click.echo("Deploying agent...")

    try:
        agent_engine = agent_engines.AgentEngine.create(
            agent_engine=root_agent,
            display_name=DISPLAY_NAME,
            description=DESCRIPTION,
            requirements=REQUIREMENTS,
            env_vars=get_env_vars(),
        )
    except Exception as e:
        raise click.ClickException(f"Deployment failed: {e}")

    click.echo("Agent deployed successfully!")
    click.echo(f"Resource name: {agent_engine.resource_name}")


@cli.command()
@click.option(
    "--min-instances",
    default=0,
    help="Minimum number of instances.",
)
@click.option(
    "--max-instances",
    default=2,
    help="Maximum number of instances.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Preview update without executing.",
)
def update(min_instances, max_instances, dry_run):
    """Update an existing agent engine."""
    validate_config()

    if not AGENT_ENGINE_ID:
        raise click.ClickException(
            "HELLO_WORLD_AGENT_ENGINE_ID not set in .env file. "
            "Run 'deploy' first to create a new agent engine."
        )

    if dry_run:
        click.echo("Dry run mode - update preview:")
        click.echo(f"  Agent Engine ID: {AGENT_ENGINE_ID}")
        click.echo(f"  Display name: {DISPLAY_NAME}")
        click.echo(f"  Description: {DESCRIPTION}")
        click.echo(f"  Min instances: {min_instances}")
        click.echo(f"  Max instances: {max_instances}")
        click.echo(f"  Requirements: {REQUIREMENTS}")
        click.echo(f"  Env vars: {list(get_env_vars().keys())}")
        return

    init_vertexai()
    root_agent = load_agent()

    click.echo(f"Updating agent: {AGENT_ENGINE_ID}")

    try:
        agent_engine = agent_engines.AgentEngine(AGENT_ENGINE_ID)
        agent_engine.update(
            agent_engine=root_agent,
            display_name=DISPLAY_NAME,
            description=DESCRIPTION,
            requirements=REQUIREMENTS,
            min_instances=min_instances,
            max_instances=max_instances,
            env_vars=get_env_vars(),
        )
    except Exception as e:
        raise click.ClickException(f"Update failed: {e}")

    click.echo("Agent updated successfully!")
    click.echo(f"Resource name: {agent_engine.resource_name}")


if __name__ == "__main__":
    cli()
