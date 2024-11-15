import os
from openai import AzureOpenAI, OpenAI
from openai.types.chat import ChatCompletionMessageParam
from executor.tools import AgentTools
from utils.logger import get_logger
from dotenv import load_dotenv
from typing import override

load_dotenv()

logger = get_logger("[Azure AI Agent]")


class AzureAIAgentTools(AgentTools):
    az_ai_client: OpenAI

    def __init__(self) -> None:
        self.az_ai_client = AzureOpenAI(
            api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT", ""),
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
        )

        self.gemini_ai_client = OpenAI(
            api_key=os.environ.get("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )

    @override
    def invoke_llm[
        T
    ](self, response_type: type[T], messages: list[ChatCompletionMessageParam]) -> T:

        response = self.az_ai_client.beta.chat.completions.parse(
            model="gpt-4o", messages=messages, response_format=response_type
        )
        parsed_content = response.choices[0].message.parsed

        if parsed_content:
            return parsed_content

        raise Exception("LLM response is empty")
