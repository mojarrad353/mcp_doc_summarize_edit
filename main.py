import asyncio
import sys
import os
from dotenv import load_dotenv
from contextlib import AsyncExitStack

from mcp_client import MCPClient
from core.openai import OpenAIClient
from core.cli_chat import CliChat
from core.cli import CliApp

load_dotenv()

# OpenAI Config
openai_model = os.getenv("OPENAI_MODEL_NAME", "gpt-4o")
openai_api_key = os.getenv("OPENAI_API_KEY", "")

assert openai_model, "Error: OPENAI_MODEL_NAME cannot be empty. Update .env"
assert openai_api_key, "Error: OPENAI_API_KEY cannot be empty. Update .env"

async def main():
    openai_service = OpenAIClient(model=openai_model, api_key=openai_api_key)

    server_scripts = sys.argv[1:]
    clients = {}

    command, args = (
        ("uv", ["run", "mcp_server.py"])
        if os.getenv("USE_UV", "0") == "1"
        else ("python", ["mcp_server.py"])
    )

    async with AsyncExitStack() as stack:
        # 1. Initialize the documentation/main client
        doc_client = await stack.enter_async_context(
            MCPClient(command=command, args=args)
        )
        clients["doc_client"] = doc_client

        # 2. Initialize additional clients from command line args
        for i, server_script in enumerate(server_scripts):
            client_id = f"client_{i}_{server_script}"
            client = await stack.enter_async_context(
                MCPClient(command="uv", args=["run", server_script])
            )
            clients[client_id] = client

        # 3. Initialize Chat Logic
        chat = CliChat(
            doc_client=doc_client,
            clients=clients,
            openai_service=openai_service,
        )

        # 4. Initialize UI
        cli = CliApp(chat)
        await cli.initialize()
        await cli.run()

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())