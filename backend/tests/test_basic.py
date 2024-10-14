import unittest
from dotenv import load_dotenv

load_dotenv()

from executor.core import NLQExecutor
from executor.catalog import Catalog
from executor.tools import GPTAgentTools
from executor.config import AgentConfig


class TestBasic(unittest.TestCase):
    def test_basic(self):
        executor = (
            NLQExecutor()
            .with_tools(GPTAgentTools())
            .with_config(
                AgentConfig(update_callback=lambda x: print(f"state: {x}"))
            )  # SSE would ultimately be here
            .with_catalogs(
                [
                    Catalog(
                        provider="postgres",
                        schema={
                            "staff": {
                                "id": "SERIAL PRIMARY KEY",
                                "email": "VARCHAR(100) UNIQUE NOT NULL",
                                "role": "VARCHAR(50) NOT NULL",
                                "created_at": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP",
                            },
                            "workers": {
                                "id": "SERIAL PRIMARY KEY",
                                "email": "VARCHAR(100) UNIQUE NOT NULL",
                                "created_at": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP",
                            },
                            "projects": {
                                "id": "SERIAL PRIMARY KEY",
                                "name": "VARCHAR(100) NOT NULL",
                                "description": "TEXT",
                                "created_at": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP",
                            },
                            "project_staff": {
                                "project_id": "INTEGER REFERENCES projects(id) ON DELETE CASCADE",
                                "staff_id": "INTEGER REFERENCES staff(id) ON DELETE CASCADE",
                                "PRIMARY KEY": "(project_id, staff_id)",
                            },
                            "datasets": {
                                "id": "SERIAL PRIMARY KEY",
                                "project_id": "INTEGER REFERENCES projects(id) ON DELETE CASCADE",
                                "name": "VARCHAR(100) NOT NULL",
                                "description": "TEXT",
                                "created_at": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP",
                            },
                            "labels": {
                                "id": "SERIAL PRIMARY KEY",
                                "dataset_id": "INTEGER REFERENCES datasets(id) ON DELETE CASCADE",
                                "name": "VARCHAR(100) NOT NULL",
                                "description": "TEXT",
                                "created_at": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP",
                            },
                            "data_entries": {
                                "id": "SERIAL PRIMARY KEY",
                                "dataset_id": "INTEGER REFERENCES datasets(id) ON DELETE CASCADE",
                                "text_content": "TEXT NOT NULL",
                                "created_at": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP",
                            },
                            "annotations": {
                                "id": "SERIAL PRIMARY KEY",
                                "data_entry_id": "INTEGER REFERENCES data_entries(id) ON DELETE CASCADE",
                                "label_id": "INTEGER REFERENCES labels(id) ON DELETE CASCADE",
                                "worker_id": "INTEGER REFERENCES workers(id) ON DELETE CASCADE",
                                "created_at": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP",
                                "UNIQUE": "(data_entry_id, worker_id)",
                            },
                            "app_crashes": {
                                "id": "SERIAL PRIMARY KEY",
                                "worker_id": "INTEGER REFERENCES workers(id) ON DELETE CASCADE",
                                "timestamp": "TIMESTAMP WITH TIME ZONE NOT NULL",
                                "error_message": "TEXT NOT NULL",
                                "stack_trace": "TEXT",
                            },
                        },
                        connection_params={
                            "dbname": "nlqx_test",
                            "user": "nlqx_user",
                            "password": "nlqx_password",
                            "host": "localhost",
                            "port": 5432,
                        },
                    )
                ]
            )
        )

        result = executor.execute(
            "When was the worker account with the most crashes created?"
        )

        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
