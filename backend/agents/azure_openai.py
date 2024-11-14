import os
import json
from typing import List
from executor.catalog import Catalog
from executor.query import Query
from executor.result import Result
from executor.state import AgentState
from executor.tools import AgentTools
from openai import AzureOpenAI, OpenAI

client = AzureOpenAI(
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT", ""),
)
analyze_catalogs_schema = {
    "name": "analyze_catalogs",
    "description": "Analyze the catalogs and return the subset of catalogs that this query could be querying",
    "parameters": {
        "type": "object",
        "properties": {
            "providers": {
                "type": "array",
                "description": "The list of providers to analyze (e.g. ['postgres', 'mongodb'])",
                "items": {"type": "string"},
            },
        },
        "required": ["providers"],
    },
}


class GPTAgentTools(AgentTools):

    def analyze_catalogs(self, nlq: str, catalogs: List[Catalog]) -> List[Catalog]:
        message_content = f"Analyze the following natural language query and return the subset of catalogs that this query could be querying:\n\nNLQ: {nlq}\n\nCatalogs: {catalogs}"

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": message_content,
                }
            ],
            functions=[analyze_catalogs_schema],
            function_call="auto",
            model="gpt-4o",
        )

        response = json.loads(
            chat_completion.choices[0].message.function_call.arguments
        )

        filtered_catalogs = []
        for catalog in catalogs:
            if catalog.provider in response["providers"]:
                filtered_catalogs.append(catalog)

        return filtered_catalogs

    def generate_queries(self, nlq: str, catalogs: List[Catalog]) -> List[Query]:
        queries = []

        for catalog in catalogs:
            if catalog.provider == "postgres":
                provider = "SQL"
            else:
                raise ValueError(f"Unsupported provider: {catalog.provider}")
            message_content = f"Convert the following natural language query to {provider} for the given catalog. Only return the SQL and nothing else (not even markdown or code blocks):\n\nNLQ: {nlq}\n\nCatalog: {catalog}"

            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": message_content,
                    }
                ],
                model="gpt-4o",
            )

            response = chat_completion.choices[0].message.content
            if response.startswith("```sql"):
                response = response[6:].strip()
            elif response.startswith("```"):
                response = response[3:].strip()

            if response.endswith("```"):
                response = response[:-3].strip()

            print(f"response({catalog.provider}): {response}")
            queries.append(Query(nlq=nlq, sql=response, catalog=catalog))

        return queries
