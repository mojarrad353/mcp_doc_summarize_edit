import asyncio
import sys
import os
from contextlib import AsyncExitStack

from .client.mcp_client import MCPClient
from .core.openai import OpenAIClient
from .core.cli_chat import CliChat
from .core.cli import CliApp
from .config import settings
from .logger import setup_logger

import argparse

logger = setup_logger(__name__)

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="URL of the SSE server to connect to (e.g. http://127.0.0.1:8000/sse)")
    parser.add_argument("additional_servers", nargs="*", help="Additional server scripts to run")
    args = parser.parse_args()

    openai_service = OpenAIClient(model=settings.openai_model_name, api_key=settings.openai_api_key)
    clients = {}

    async with AsyncExitStack() as stack:
        # 1. Initialize the documentation/main client
        if args.url:
             logger.info(f"Connecting to server at: {args.url}")
             try:
                doc_client = await stack.enter_async_context(
                    MCPClient(url=args.url)
                )
                clients["doc_client"] = doc_client
             except Exception as e:
                logger.error(f"Failed to connect to server at {args.url}: {e}")
                return
        else:
             # Default: Spawn internal server
             default_server_script = "src/mcp_document_summary/server/server.py"
             cmd, cmd_args = (
                ("uv", ["run", "python", "-m", "mcp_document_summary.server.server"])
                if os.getenv("USE_UV", "0") == "1"
                else ("python", ["-m", "mcp_document_summary.server.server"])
             )
             logger.info(f"Spawning default server: {cmd} {cmd_args}")
             try:
                doc_client = await stack.enter_async_context(
                    MCPClient(command=cmd, args=cmd_args)
                )
                clients["doc_client"] = doc_client
             except Exception as e:
                logger.error(f"Failed to spawn default server: {e}")
                return

        # 2. Initialize additional clients from command line args
        for i, server_script in enumerate(args.additional_servers):
            client_id = f"client_{i}_{server_script}"
            logger.info(f"Connecting to additional server: {server_script}")
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