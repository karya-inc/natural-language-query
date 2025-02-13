import os
from openai import AsyncOpenAI, AsyncAzureOpenAI
from openai.types.chat import ChatCompletionMessageParam
from executor.tools import AgentTools
from utils.logger import get_logger
from dotenv import load_dotenv
from typing import override

load_dotenv()

logger = get_logger("[Azure AI Agent]")


class AzureAIAgentTools(AgentTools):
    az_ai_client: AsyncOpenAI

    def __init__(self) -> None:
        self.az_ai_client = AsyncAzureOpenAI(
            api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT", ""),
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
        )

    @override
    async def invoke_llm[
        T
    ](
        self,
        response_type: type[T],
        messages: list[ChatCompletionMessageParam],
        temperature=0.0,
    ) -> T:

        response = await self.az_ai_client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=messages,
            response_format=response_type,
            temperature=temperature,
        )
        parsed_content = response.choices[0].message.parsed

        logger.info(f"Generated Response: {response.choices[0].message.content}")

        if parsed_content:
            return parsed_content

        raise Exception("LLM response is empty")
