import os
from typing import Optional
from dotenv import load_dotenv

from utils.logger import setup_logging, disable_logging
from schema_enricher.enrich_schema import enrich_schema_of_all_tables
from schema_enricher.db_utils import get_table_names
from schema_enricher.file_io import load_json, combine_json_files, check_intermediate_folder

# Load environment variables
load_dotenv()

# Access environment variables
SCHEMA_PATH = os.getenv("SCHEMA_PATH")
INTERMEDIATE_ENRICHED_PER_TABLE_SCHEMA_FOLDER = os.getenv("INTERMEDIATE_ENRICHED_PER_TABLE_SCHEMA_FOLDER")
ENRICHED_SCHEMA_PATH = os.getenv("ENRICHED_SCHEMA_PATH")

# Initialize logger
logger = setup_logging(
    logger_name="main_schema_enrichment",
    success_file="main_schema_enrichment_success.log",
    error_file="main_schema_enrichment_error.log"
)

# # Disable logging if not needed
# disable_logging('C:/Users/13mal/Documents/nlq_generator/text2sql/logs/main_schema_enrichment')


def user_triggered_enrichment() -> bool:
    """
    Prompt the user to confirm if they want to enrich the schema.

    Returns:
        bool: True if the user inputs 'yes', otherwise False.
    """
    return input("Schema changed? Enter 'yes' to enrich the newly updated schema: ").lower() == 'yes'


def run_schema_enrichment(model: Optional[object] = None
) -> None:
    """
    Run the schema enrichment process if a schema change is detected or triggered by the user.

    Args:
        model (Optional[object]): Model to use for schema enrichment.
    """
    try:
        # if user_triggered_enrichment():
        if user_triggered_enrichment():
            logger.info("Schema change detected or user requested enrichment.")
            
            table_names = get_table_names()
            logger.info("Fetched table names successfully.")
            
            try:
                # Ensure the intermediate folder exists, and if already exists then empty it
                check_intermediate_folder(INTERMEDIATE_ENRICHED_PER_TABLE_SCHEMA_FOLDER)
                # Enrich the schema
                enrich_schema_of_all_tables(model, SCHEMA_PATH, table_names, INTERMEDIATE_ENRICHED_PER_TABLE_SCHEMA_FOLDER)
                logger.info("Schema enrichment completed successfully.")
            except Exception as e:
                logger.error(f"An error occurred during schema enrichment step: {e}")
            
            # Combine all the intermediate JSON files of per table schema
            combine_json_files(INTERMEDIATE_ENRICHED_PER_TABLE_SCHEMA_FOLDER, ENRICHED_SCHEMA_PATH)
            logger.info("Combined JSON files successfully to a single final schema.")
    
    except Exception as e:
        logger.error(f"An error occurred while running run_schema_enrichment fn: {e}")

if __name__ == "__main__":
    run_schema_enrichment()