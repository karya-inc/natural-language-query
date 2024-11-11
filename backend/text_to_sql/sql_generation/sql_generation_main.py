import json
import os
from typing import Any
from dotenv import load_dotenv

from sql_generation.response_handler import generate_sql_response, correct_sql_response
from utils.config import QUERY_DIALECT, SAFETY_CONFIGS, GENERATION_CONFIG
from utils.logger import setup_logging, disable_logging

# Logger setup
logger = setup_logging(
    logger_name="main_sql_generation",
    success_file="main_sql_generation_success.log",
    error_file="main_sql_generation_error.log"
)

# # Disable logging if not needed
# disable_logging('main_sql_generation')

# Load environment variables
load_dotenv()
ENRICHED_SCHEMA_PATH = os.getenv("ENRICHED_SCHEMA_PATH")


def run_sql_generation(model: Any, 
question: str
) -> str:
    """
    Generate SQL response and handle corrective feedback to refine the SQL.

    Args:
        model (Any): The language model used for generating SQL responses.
        question (str): The user's question in natural language.

    Returns:
        str: The SQL response generated by the model.
    """
    try:
        # Load enriched database schema
        logger.info("Loading enriched database schema.")
        with open(ENRICHED_SCHEMA_PATH, "r") as json_file:
            enriched_db_schema = json.load(json_file)
        logger.info("Successfully loaded enriched database schema.")

        # Generate initial SQL response
        logger.info("Generating initial SQL response.")
        initial_sql_query = generate_sql_response(
            model, SAFETY_CONFIGS, GENERATION_CONFIG, enriched_db_schema, question, QUERY_DIALECT
        )
        logger.info(f"Generated SQL Response: {initial_sql_query}")


        # # ToDo: discuss if need of corrective feedback
        # # Prepare for corrective feedback
        # initial_question = question
        # corrective_feedback = "Please include the total credits earned by each worker."
        # logger.info("Applying corrective feedback to SQL response.")
        
        # # Generate corrected SQL response
        # corrected_sql_query = correct_sql_response(
        #     model, SAFETY_CONFIGS, GENERATION_CONFIG, enriched_db_schema,
        #     initial_question, QUERY_DIALECT, initial_sql_query, corrective_feedback
        # )
        # logger.info(f"Corrected SQL Response: {corrected_sql_query}")

        return initial_sql_query

    except FileNotFoundError as e:
        logger.error("Enriched schema file not found. Please check the ENRICHED_SCHEMA_PATH.", exc_info=True)
        raise e

    except json.JSONDecodeError as e:
        logger.error("Failed to parse enriched schema file. Ensure it is in valid JSON format.", exc_info=True)
        raise e

    except Exception as e:
        logger.error("An unexpected error occurred during SQL generation.", exc_info=True)
        raise e