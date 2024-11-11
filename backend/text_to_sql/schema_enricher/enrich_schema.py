from tqdm import tqdm
from typing import Dict, List

from schema_enricher.db_utils import get_column_random_data
from schema_enricher.llm_column_descriptor import generate_column_description
from schema_enricher.file_io import load_json, save_json
from utils.logger import setup_logging, disable_logging
from utils.config import SAFETY_CONFIGS, GENERATION_CONFIG


# Initialize logger
logger = setup_logging(
    logger_name="schema_enrichment",
    success_file="schema_enrichment_success.log",
    error_file="schema_enrichment_error.log"
)

# # Disable logging if not needed
# disable_logging('schema_enrichment')


# Function to enrich schema of a single table
def enrich_schema_of_table(
    path_to_db_schema: str, 
    model: object, 
    safety_configs: dict, 
    generation_config: dict, 
    table_name: str
) -> Dict[str, List[Dict[str, str]]]:
    """
    Enrich the schema of a table by adding descriptions to columns.

    Args:
        path_to_db_schema (str): Path to the database schema JSON file.
        model (object): The model used to generate column descriptions.
        safety_configs (dict): Safety configurations for description generation.
        generation_config (dict): Configuration for the generation process.
        table_name (str): The name of the table whose schema is to be enriched.

    Returns:
        Dict[str, List[Dict[str, str]]]: The enriched schema with descriptions added to columns.
    """
    try:
        # Load the schema from the given JSON file
        schema = load_json(path_to_db_schema)

        # Filter the table details to include only the current table name
        schema = {table_name: schema[table_name]}
        
        # Enrich the columns of the current table
        for table_name_from_loaded_schema, columns_of_eachtable in schema.items():
                for eachcolumn_of_eachtable in columns_of_eachtable:
                    name_of_columns_of_eachtable = eachcolumn_of_eachtable["column_name"]

                    # Using SQL query fetch particular number of rows in random order of a particular column of a particular table
                    random_data_of_column_of_table = get_column_random_data(table_name, name_of_columns_of_eachtable)

                    # Generate column description from fivedata of a column of a particular table
                    column_description = generate_column_description(model, safety_configs, generation_config, table_name, name_of_columns_of_eachtable, random_data_of_column_of_table)

                    # Add "column description" to previous details of each column of each table
                    eachcolumn_of_eachtable["column_description"] = column_description

        return schema
    except Exception as e:
        logger.error(f"Error enriching schema for table {table_name}: {e}")
        raise


# Function to enrich schemas for all tables and save them
def enrich_schema_of_all_tables(
    model: object,
    path_to_db_schema: str, 
    table_names: List[str], 
    folder_path_to_save_intermediate_files: str
) -> None:
    """
    Enrich schemas for all tables and save them into intermediate files.

    Args:
        model (object): The model used to generate column descriptions.
        path_to_db_schema (str): Path to the database schema JSON file.
        table_names (List[str]): List of table names whose schemas are to be enriched.
        folder_path_to_save_intermediate_files (str): Folder path to save intermediate enriched schema files.
    """
    # Load necessary configs from the config module
    safety_configs, generation_config = SAFETY_CONFIGS, GENERATION_CONFIG

    # Process each table, but only first two tables
    for i, table_name in enumerate(tqdm(table_names, desc="Processing tables")):
        # if i >= 2:
        #     break  # Exit loop after two iterations

        try:
            logger.info(f"Processing table {table_name}")
            enriched_schema_per_table = enrich_schema_of_table(
                path_to_db_schema, 
                model, 
                safety_configs, 
                generation_config, 
                table_name
            )
            
            # Save the enriched schema into a separate file for each table
            save_json(enriched_schema_per_table, f"{folder_path_to_save_intermediate_files}/", f"{table_name}_schema.json")
            logger.info(f"Saved {table_name} schema to {folder_path_to_save_intermediate_files}/{table_name}_schema.json")

        except Exception as e:
            logger.error(f"Failed to process table {table_name}: {e}")
            continue