# Agent Engine

Deploy and manage Google ADK agents on Vertex AI Agent Engine.

## Prerequisites

- Python 3.12+
- GCP project with Vertex AI API enabled
- Service account with appropriate permissions
- GCS bucket for staging

## Setup

1. Install dependencies:

```bash
uv sync
source .venv/bin/activate
```

2. Copy `.env.sample` to `.env` and configure:

```bash
cp .env.sample .env
```

3. Edit `.env` with your GCP configuration:

```bash
# GCP Configuration
HELLO_WORLD_PROJECT=your-gcp-project-id
HELLO_WORLD_LOCATION=us-central1
HELLO_WORLD_STAGING_BUCKET=gs://your-staging-bucket

# Agent Engine Resource ID (set after first deployment)
HELLO_WORLD_AGENT_ENGINE_ID=

# Agent Metadata
HELLO_WORLD_DISPLAY_NAME=hello_world
HELLO_WORLD_DESCRIPTION=Hello World Agent

# Runtime Environment Variables
HELLO_WORLD_LOG_LEVEL=INFO
HELLO_WORLD_GOOGLE_GENAI_USE_VERTEXAI=TRUE
HELLO_WORLD_GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY=TRUE
HELLO_WORLD_OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=TRUE
```

## Usage

### Deploy a New Agent

Deploy a new agent engine to Vertex AI:

```bash
python deploy_cli.py deploy
```

Preview deployment without executing:

```bash
python deploy_cli.py deploy --dry-run
```

After successful deployment, copy the resource name and update `HELLO_WORLD_AGENT_ENGINE_ID` in `.env`.

### Update an Existing Agent

Update an existing agent engine with new code:

```bash
python deploy_cli.py update
```

Update with custom instance scaling:

```bash
python deploy_cli.py update --min-instances 1 --max-instances 4
```

Preview update without executing:

```bash
python deploy_cli.py update --dry-run
```

### CLI Help

```bash
# Show all commands
python deploy_cli.py --help

# Show deploy options
python deploy_cli.py deploy --help

# Show update options
python deploy_cli.py update --help
```

## Project Structure

```
agent_engine/
├── deploy_cli.py      # CLI for deploy/update operations
├── .env               # Environment configuration (not committed)
├── .env.sample        # Environment template
├── hello_world/       # Agent implementation
│   ├── __init__.py
│   └── agent.py       # Agent definition (root_agent)
└── README.md
```
