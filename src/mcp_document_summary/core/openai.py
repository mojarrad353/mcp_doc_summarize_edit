import os
from openai import OpenAI
from openai.types.chat import ChatCompletion
from ..config import settings

class OpenAIClient:
    def __init__(self, model: str, api_key: str = None):
        self.client = OpenAI(api_key=api_key or settings.openai_api_key)
        self.model = model or settings.openai_model_name


    def add_user_message(self, messages: list, message):
        """Adds a user message or a list of tool results to the history."""
        if isinstance(message, list):
            # Likely a list of tool results
            messages.extend(message)
        else:
            messages.append({
                "role": "user",
                "content": message,
            })

    def add_assistant_message(self, messages: list, response: ChatCompletion):
        """
        Adds the assistant's response to the history. 
        Crucial: Must include 'tool_calls' if they exist.
        """
        message_data = response.choices[0].message
        
        assistant_message = {
            "role": "assistant",
            "content": message_data.content, 
        }

        if message_data.tool_calls:
            assistant_message["tool_calls"] = message_data.tool_calls

        messages.append(assistant_message)

    def text_from_message(self, message: ChatCompletion) -> str:
        """Extracts text content from the OpenAI ChatCompletion object."""
        if message.choices and message.choices[0].message.content:
            return message.choices[0].message.content
        return ""

    def chat(
        self,
        messages,
        system=None,
        temperature=1.0,
        stop_sequences=None,
        tools=None,
    ) -> ChatCompletion:
        
        request_messages = messages.copy()
        
        if system:
            request_messages.insert(0, {"role": "system", "content": system})

        params = {
            "model": self.model,
            "messages": request_messages,
            "temperature": temperature,
        }

        if stop_sequences:
            params["stop"] = stop_sequences

        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"

        response = self.client.chat.completions.create(**params)
        return response