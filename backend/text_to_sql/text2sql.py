from dotenv import load_dotenv
import os

from schema_enricher.schema_enricher_main import run_schema_enrichment
from sql_generation.sql_generation_main import run_sql_generation
from utils.models import initialize_model
from utils.logger import setup_logging, disable_logging

# Set up logging
logger = setup_logging(
    logger_name="run_text2sql",
    success_file="run_text2sql_success.log",
    error_file="run_text2sql_error.log"
)

# Load environment variables from the .env file
load_dotenv()

# Fetch API key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def run_text2sql(question: str) -> str:
    """
    Main function to run the text-to-SQL pipeline:
    - Initializes the Gemini model using an API key from the environment.
    - Enriches the database schema with descriptions.
    - Generates an SQL query for the provided question.

    Args:
        question (str): The question for which an SQL query needs to be generated.

    Returns:
        str: The generated SQL query for the provided question.
    """
    try:
        # Initialize model with API key
        if not GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY is not set in the environment.")
            return "Error: API key not found."
        
        model = initialize_model(GEMINI_API_KEY)
        logger.info("Model initialized successfully.")


        # Enrich schema with model
        try:
            logger.info("Starting schema enrichment.")
            run_schema_enrichment(model)
            logger.info("Schema enrichment completed successfully.")
        except Exception as e:
            logger.error(f"Schema enrichment failed: {e}")
            return "Error during schema enrichment."


        # Generate SQL query for the passed question
        try:
            logger.info("Starting SQL generation.")
            corrected_response = run_sql_generation(model, question)
            logger.info("SQL generation completed successfully.")
        except Exception as e:
            logger.error(f"SQL generation failed: {e}")
            return "Error during SQL generation."

        return corrected_response

    except Exception as e:
        logger.error(f"Text-to-SQL pipeline encountered an error: {e}")
        return "Error in Text-to-SQL pipeline."