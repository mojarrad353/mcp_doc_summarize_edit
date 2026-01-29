from .openai import OpenAIClient
from ..client.mcp_client import MCPClient
from .tools import ToolManager
from typing import List, Dict, Any

class Chat:
    def __init__(self, openai_service: OpenAIClient, clients: dict[str, MCPClient]):
        self.openai_service: OpenAIClient = openai_service
        self.clients: dict[str, MCPClient] = clients
        self.messages: List[Dict[str, Any]] = []

    async def _process_query(self, query: str):
        self.messages.append({"role": "user", "content": query})

    async def run(self, query: str) -> str:
        final_text_response = ""

        await self._process_query(query)

        while True:
            # 1. Get available tools
            tools = await ToolManager.get_all_tools(self.clients)
            
            # 2. Call OpenAI
            response = self.openai_service.chat(
                messages=self.messages,
                tools=tools if tools else None,
            )

            # 3. Add Assistant Response to History (Includes tool_calls if any)
            self.openai_service.add_assistant_message(self.messages, response)

            finish_reason = response.choices[0].finish_reason

            # 4. Check if the model wants to call tools
            if finish_reason == "tool_calls":
                print(f"DEBUG: Tool calls requested...")
                
                # Execute tools
                tool_result_messages = await ToolManager.execute_tool_requests(
                    self.clients, response
                )

                # Add tool results to history
                self.openai_service.add_user_message(
                    self.messages, tool_result_messages
                )
                
                # Loop continues to send tool outputs back to OpenAI
            
            else:
                # Normal text response
                final_text_response = self.openai_service.text_from_message(
                    response
                )
                break

        return final_text_response