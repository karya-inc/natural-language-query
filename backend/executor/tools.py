from typing import List, Any

from .catalog import Catalog
from .query import Query
from .result import Result
from .state import AgentState


class AgentTools:
    def analyze_catalogs(self, nlq: str, catalogs: List[Catalog]) -> List[Catalog]:
        raise NotImplementedError

    def generate_queries(self, nlq: str, catalogs: List[Catalog]) -> List[Query]:
        raise NotImplementedError

    def execute_queries(self, queries: List[Query]) -> List[Result]:
        raise NotImplementedError

    def store_intermediate_results(self, results: List[Result]) -> Catalog:
        raise NotImplementedError

    def generate_aggregate_query(
        self, results: List[Result], intermediate_catalog: Catalog
    ) -> Query:
        raise NotImplementedError

    def is_result_sufficient(self, results: List[Result], nlq: str) -> bool:
        raise NotImplementedError

    def format_result(self, results: List[Result]) -> Any:
        raise NotImplementedError

    def refine_query(self, state: AgentState) -> AgentState:
        raise NotImplementedError


import os
import json
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
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
            provider = (
                "SQL"
                if catalog.provider == "postgres"
                else "MongoDB (so use MongoDB Aggregation Pipeline)"
            )
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
            print(f"response({catalog.provider}): {response}")
            queries.append(Query(nlq=nlq, sql=response, catalog=catalog))

        return queries
