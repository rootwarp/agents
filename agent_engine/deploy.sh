#!/bin/bash

. .env

adk deploy agent_engine hello_world \
    --project ${HELLO_WORLD_PROJECT} \
    --region us-central1 \
    --agent_engine_id ${HELLO_WORLD_AGENT_ENGINE_ID}

