"""Core client wrapper for Agent Engine."""

from typing import AsyncIterator
import logging

import vertexai

logger = logging.getLogger(__name__)


class AgentEngineClient:
    """Client for interacting with Agent Engine."""

    def __init__(
        self,
        agent_engine_id: str,
        project: str | None = None,
        location: str = "us-central1",
    ):
        """Initialize the Agent Engine client.

        Args:
            agent_engine_id: Full resource path or ID of the Agent Engine.
            project: GCP project ID. If None, uses default from environment.
            location: GCP region. Defaults to us-central1.
        """
        self.agent_engine_id = agent_engine_id
        self.project = project
        self.location = location

        logger.info("Initializing AgentEngineClient...")
        logger.debug("  agent_engine_id: %s", agent_engine_id)
        logger.debug("  project: %s", project)
        logger.debug("  location: %s", location)

        logger.debug("Creating vertexai.Client...")
        self._client = vertexai.Client(project=project, location=location)
        logger.debug("vertexai.Client created successfully")

        logger.debug("Fetching agent engine resource...")
        self._agent = self._client.agent_engines.get(name=agent_engine_id)
        logger.info("AgentEngineClient initialized successfully")

    async def query_stream(
        self,
        user_id: str,
        message: str,
        session_id: str | None = None,
    ) -> AsyncIterator[dict]:
        """Send a query and stream the response asynchronously.

        Args:
            user_id: User identifier.
            message: The query message.
            session_id: Optional session identifier. If None, creates a new session.

        Yields:
            Response events as they arrive.
        """
        logger.info("Starting streaming query...")
        logger.debug("  user_id: %s", user_id)
        logger.debug("  session_id: %s", session_id)
        logger.debug("  message: %s", message[:100] if len(message) > 100 else message)

        kwargs = {"user_id": user_id, "message": message}
        if session_id:
            kwargs["session_id"] = session_id

        logger.debug("Calling async_stream_query with kwargs: %s", kwargs)
        event_count = 0
        async for event in self._agent.async_stream_query(**kwargs):
            event_count += 1
            logger.debug("Received event #%d: %s", event_count, type(event).__name__)
            logger.debug("  Event content: %s", event)
            yield event

        logger.info("Streaming query completed. Total events: %d", event_count)

    async def create_session(self, user_id: str) -> dict:
        """Create a new session for a user.

        Args:
            user_id: User identifier (up to 128 characters).

        Returns:
            The created session object.
        """
        logger.info("Creating session...")
        logger.debug("  user_id: %s", user_id)

        session = await self._agent.async_create_session(user_id=user_id)

        logger.info("Session created successfully")
        logger.debug("  Session: %s", session)
        return session

    async def list_sessions(self, user_id: str) -> list:
        """List all sessions for a user.

        Args:
            user_id: User identifier.

        Returns:
            List of sessions.
        """
        logger.info("Listing sessions...")
        logger.debug("  user_id: %s", user_id)

        response = await self._agent.async_list_sessions(user_id=user_id)
        sessions = list(response.sessions) if hasattr(response, "sessions") else []

        logger.info("Found %d sessions", len(sessions))
        logger.debug("  Sessions: %s", sessions)
        return sessions

    async def get_session(self, user_id: str, session_id: str) -> dict:
        """Get a specific session.

        Args:
            user_id: User identifier.
            session_id: Session identifier.

        Returns:
            The session object.
        """
        logger.info("Getting session...")
        logger.debug("  user_id: %s", user_id)
        logger.debug("  session_id: %s", session_id)

        session = await self._agent.async_get_session(
            user_id=user_id, session_id=session_id
        )

        logger.info("Session retrieved successfully")
        logger.debug("  Session: %s", session)
        return session

    async def delete_session(self, user_id: str, session_id: str) -> None:
        """Delete a session.

        Args:
            user_id: User identifier.
            session_id: Session identifier.
        """
        logger.info("Deleting session...")
        logger.debug("  user_id: %s", user_id)
        logger.debug("  session_id: %s", session_id)

        await self._agent.async_delete_session(
            user_id=user_id, session_id=session_id
        )

        logger.info("Session deleted successfully")
