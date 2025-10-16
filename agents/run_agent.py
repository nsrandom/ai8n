#!/usr/bin/env python3
"""Agent Runner"""

import asyncio
import logging
import os
from dotenv import load_dotenv

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agent import math_agent

# Configuration
APP_NAME = "math_agent"
USER_ID = "asif"

# Load .env file from the parent directory
dotenv_path=f"{os.path.dirname(os.path.abspath(__file__))}/../.env"
print(f"run_agent.py: Loading .env file from: {dotenv_path}")
load_dotenv(dotenv_path=dotenv_path)

# Setup logging
logger = logging.getLogger(__name__)
def setup_logging():
    """Setup consistent logging across all agents"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# Session management utilities
async def create_session(app_name: str, user_id: str = "default_user"):
    """Creates a session with proper async handling"""
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id
    )
    return session_service, session

async def run_math_agent(initial_message: str):
    """Runs the newsletter agent"""
    try:
        # Create session
        session_service, session = await create_session(APP_NAME, USER_ID)

        # Create runner
        runner = Runner(
            agent=math_agent,
            app_name=APP_NAME,
            session_service=session_service
        )

        # Prepare content
        content = types.Content(
            role='user',
            parts=[types.Part(text=initial_message)]
        )

        logger.info("Running the Math agent...")

        # Run the agent to create and send newsletter
        events = runner.run_async(
            user_id=USER_ID,
            session_id=session.id,
            new_message=content
        )

        # Collect response
        async for event in events:
            if event.is_final_response():
                print(f"Agent's final response: {event.content.parts[0].text}")
                return event.content.parts[0].text

        return None

    except Exception as e:
        logger.error(f"❌ Math agent failed: {e}")
        return f"Error running newsletter agent: {str(e)}"

async def main():
    """Main execution function"""
    try:
        logger.info("🚀 Starting the Math Agent...")
        result = await run_math_agent(initial_message="Create and solve a math problem")

        print(result if result else "❌ No results returned")
        logger.info("✅ Math sent successfully!")

    except Exception as e:
        logger.error(f"❌ Main execution failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 