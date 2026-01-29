import json
from typing import Optional, List, Any
from mcp.types import CallToolResult, TextContent
from ..client.mcp_client import MCPClient

from openai.types.chat import (
    ChatCompletion, 
    ChatCompletionToolMessageParam,
    ChatCompletionToolParam
)

class ToolManager:
    @classmethod
    async def get_all_tools(cls, clients: dict[str, MCPClient]) -> list[ChatCompletionToolParam]:
        """Gets all tools from the provided clients and formats them for OpenAI."""
        tools: list[ChatCompletionToolParam] = []
        for client in clients.values():
            tool_models = await client.list_tools()
            tools += [
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.inputSchema,  
                    }
                }
                for t in tool_models
            ]
        return tools

    @classmethod
    async def _find_client_with_tool(
        cls, clients: list[MCPClient], tool_name: str
    ) -> Optional[MCPClient]:
        """Finds the first client that has the specified tool."""
        for client in clients:
            tools = await client.list_tools()
            tool = next((t for t in tools if t.name == tool_name), None)
            if tool:
                return client
        return None

    @classmethod
    def _build_tool_result_part(
        cls,
        tool_use_id: str,
        text: str,
    ) -> ChatCompletionToolMessageParam:
        """Builds a tool result message compatible with OpenAI."""
        return {
            "role": "tool",
            "tool_call_id": tool_use_id,
            "content": text,
        }

    @classmethod
    async def execute_tool_requests(
        cls, clients: dict[str, MCPClient], message: ChatCompletion
    ) -> List[ChatCompletionToolMessageParam]:
        """Executes tool calls found in the OpenAI ChatCompletion response."""
        
        choice = message.choices[0]
        if not choice.message.tool_calls:
            return []
            
        tool_calls = choice.message.tool_calls
        tool_result_messages: list[ChatCompletionToolMessageParam] = []

        for tool_call in tool_calls:
            tool_use_id = tool_call.id
            tool_name = tool_call.function.name
            
            try:
                tool_input = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                tool_result_messages.append(
                    cls._build_tool_result_part(
                        tool_use_id, "Error: Invalid JSON arguments provided by model."
                    )
                )
                continue

            client = await cls._find_client_with_tool(
                list(clients.values()), tool_name
            )

            if not client:
                tool_result_messages.append(
                    cls._build_tool_result_part(
                        tool_use_id, f"Error: Could not find tool '{tool_name}'"
                    )
                )
                continue

            try:
                tool_output: CallToolResult | None = await client.call_tool(
                    tool_name, tool_input
                )
                
                content_str = ""
                if tool_output and tool_output.content:
                    # Extract text from MCP content list
                    texts = [
                        item.text for item in tool_output.content 
                        if isinstance(item, TextContent)
                    ]
                    content_str = "\n".join(texts)
                
                if tool_output and tool_output.isError:
                    content_str = f"Tool Execution Error: {content_str}"

                if not content_str:
                    content_str = "Tool executed successfully but returned no content."

                tool_result_messages.append(
                    cls._build_tool_result_part(tool_use_id, content_str)
                )

            except Exception as e:
                error_message = f"Error executing tool '{tool_name}': {str(e)}"
                print(error_message)
                tool_result_messages.append(
                    cls._build_tool_result_part(
                        tool_use_id, error_message
                    )
                )

        return tool_result_messages