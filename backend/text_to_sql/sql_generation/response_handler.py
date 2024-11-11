from utils.models import get_response
from sql_generation.prompt_builder import build_sql_prompt, build_feedback_prompt
from utils.logger import setup_logging, disable_logging

# Initialize logging for the module
logger = setup_logging(
    logger_name="sql_generation_response_handler",
    success_file="sql_generation_response_handler_success.log",
    error_file="sql_generation_response_handler_error.log"
)

# Disable logging if not needed
# disable_logging('C:/Users/13mal/Documents/nlq_generator/text2sql/logs/sql_generation_response_handler')

from typing import Any, Dict

def generate_sql_response(
    model: Any, 
    safety_configs: Dict[str, Any], 
    generation_config: Dict[str, Any], 
    enriched_db_schema: str, 
    question: str, 
    query_dialect: str
) -> str:
    """
    Generate SQL response based on the input question.

    Args:
        model (Any): The model instance to generate responses.
        safety_configs (Dict[str, Any]): Configuration for safety checks.
        generation_config (Dict[str, Any]): Configuration for generation parameters.
        enriched_db_schema (str): The enriched schema of the database.
        question (str): The user’s question in natural language.
        query_dialect (str): The SQL dialect to use for generation.

    Returns:
        str: Generated SQL response.
    """
    try:
        logger.info("Building SQL prompt for question.")
        # Build the SQL prompt based on inputs
        prompt = build_sql_prompt(enriched_db_schema, question, query_dialect)
        
        logger.info("Fetching SQL response from the model.")

        # Generate SQL response using the model
        response = get_response(model, prompt, safety_configs, generation_config)
        
        logger.info("SQL response generated successfully.")
        return response
    except Exception as e:
        logger.error(f"Failed to generate SQL response: {e}")
        raise


def correct_sql_response(
    model: Any, 
    safety_configs: Dict[str, Any], 
    generation_config: Dict[str, Any], 
    enriched_db_schema: str, 
    initial_question: str, 
    query_dialect: str, 
    initial_sql_query: str, 
    corrective_feedback: str
) -> str:
    """
    Correct SQL response based on user feedback.

    Args:
        model (Any): The model instance to generate responses.
        safety_configs (Dict[str, Any]): Configuration for safety checks.
        generation_config (Dict[str, Any]): Configuration for generation parameters.
        enriched_db_schema (str): The enriched schema of the database.
        initial_question (str): The initial user question.
        query_dialect (str): The SQL dialect to use for generation.
        initial_sql_query (str): The initial generated SQL query.
        corrective_feedback (str): Feedback provided for correcting the query.

    Returns:
        str: Corrected SQL response based on feedback.
    """
    try:
        logger.info("Building feedback prompt for corrective SQL response.")
        # Build the feedback-based prompt
        prompt = build_feedback_prompt(enriched_db_schema, initial_question, query_dialect, initial_sql_query, corrective_feedback)
        
        logger.info("Fetching corrected SQL response from the model.")

        # Generate corrected SQL response
        response = get_response(model, prompt, safety_configs, generation_config)
        
        logger.info("Corrected SQL response generated successfully.")
        return response
    except Exception as e:
        logger.error(f"Failed to generate corrected SQL response: {e}")
        raise