from typing import List, Tuple
from mcp.types import Prompt, PromptMessage, EmbeddedResource
# Updated Import for OpenAI Types
from openai.types.chat import ChatCompletionMessageParam

from openai.types.chat import ChatCompletionMessageParam

from .chat import Chat
from .openai import OpenAIClient
from ..client.mcp_client import MCPClient


class CliChat(Chat):
    def __init__(
        self,
        doc_client: MCPClient,
        clients: dict[str, MCPClient],
        openai_service: OpenAIClient,
    ):
        super().__init__(clients=clients, openai_service=openai_service)
        self.doc_client: MCPClient = doc_client

    async def list_prompts(self) -> list[Prompt]:
        return await self.doc_client.list_prompts()

    async def list_docs_ids(self) -> list[str]:
        return await self.doc_client.read_resource("docs://documents")

    async def get_doc_content(self, doc_id: str) -> str:
        return await self.doc_client.read_resource(f"docs://documents/{doc_id}")

    async def get_prompt(
        self, command: str, doc_id: str
    ) -> list[PromptMessage]:
        return await self.doc_client.get_prompt(command, {"doc_id": doc_id})

    async def _extract_resources(self, query: str) -> str:
        mentions = [word[1:] for word in query.split() if word.startswith("@")]

        doc_ids = await self.list_docs_ids()
        mentioned_docs: list[Tuple[str, str]] = []

        for doc_id in doc_ids:
            if doc_id in mentions:
                content = await self.get_doc_content(doc_id)
                mentioned_docs.append((doc_id, content))

        return "".join(
            f'\n<document id="{doc_id}">\n{content}\n</document>\n'
            for doc_id, content in mentioned_docs
        )

    async def _process_command(self, query: str) -> bool:
        if not query.startswith("/"):
            return False

        words = query.split()
        command = words[0].replace("/", "")

        # Safety check for command arguments
        if len(words) < 2:
            return False

        messages = await self.doc_client.get_prompt(
            command, {"doc_id": words[1]}
        )

        self.messages += convert_prompt_messages_to_message_params(messages)
        return True

    async def _process_query(self, query: str):
        if await self._process_command(query):
            return

        added_resources = await self._extract_resources(query)

        prompt = f"""
        The user has a question:
        <query>
        {query}
        </query>

        The following context may be useful in answering their question:
        <context>
        {added_resources}
        </context>

        Note the user's query might contain references to documents like "@report.docx". The "@" is only
        included as a way of mentioning the doc. The actual name of the document would be "report.docx".
        If the document content is included in this prompt, you don't need to use an additional tool to read the document.
        Answer the user's question directly and concisely. Start with the exact information they need. 
        Don't refer to or mention the provided context in any way - just use it to inform your answer.
        """

        self.messages.append({"role": "user", "content": prompt})


def convert_prompt_message_to_message_param(
    prompt_message: "PromptMessage",
) -> ChatCompletionMessageParam:
    """
    Converts an MCP PromptMessage to an OpenAI ChatCompletionMessageParam.
    """
    role = "user" if prompt_message.role == "user" else "assistant"
    content = prompt_message.content

    # 1. Text Content
    if hasattr(content, "text"):
         return {"role": role, "content": content.text}
    
    # 2. Dictionary Content
    if isinstance(content, dict):
        if content.get("type") == "text":
             return {"role": role, "content": content.get("text", "")}

    # 3. List Content (Complex)
    if isinstance(content, list):
        # Flatten to string for simplicity with OpenAI unless using vision model explicitly
        # Otherwise, we need to map to [{"type": "text", "text": ...}, ...]
        text_parts = []
        for item in content:
            if hasattr(item, "text"):
                text_parts.append(item.text)
            elif isinstance(item, dict) and item.get("type") == "text":
                text_parts.append(item.get("text", ""))
            elif isinstance(item, EmbeddedResource):
                 text_parts.append(f"[Resource: {item.resource.uri}]")
        
        return {"role": role, "content": "\n".join(text_parts)}

    return {"role": role, "content": str(content)}


def convert_prompt_messages_to_message_params(
    prompt_messages: List[PromptMessage],
) -> List[ChatCompletionMessageParam]:
    return [
        convert_prompt_message_to_message_param(msg) for msg in prompt_messages
    ]