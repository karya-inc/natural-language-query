from typing import Optional, Any

from utils.models import get_response
from utils.logger import setup_logging, disable_logging

# Initialize logger
logger = setup_logging(
    logger_name="column_description",
    success_file="column_description_success.log",
    error_file="column_description_error.log"
)

# # Disable logging if not needed
# disable_logging('column_description')


def generate_column_description(
    model: Any,  
    safety_configs: Optional[dict], 
    generation_config: dict,  
    table_name: str, 
    name_of_columns_of_eachtable: str, 
    random_data_of_column_of_table: list 
) -> str:
    """
    Generates a short description of a column based on its name and the values in the column.

    Args:
        model (Any): The model used to generate content (can be an AI model or similar).
        safety_configs (Optional[dict]): Optional safety configurations for content generation.
        generation_config (dict): Configuration settings for the content generation process.
        table_name (str): The name of the table containing the column.s
        name_of_columns_of_eachtable (str): The name of the column being described.
        random_data_of_column_of_table (list): A list of data items in the column to assist in description generation.

    Returns:
        str: A generated description of the column or a fallback message if no description is generated.
    """

    col_description = None

    prompt = f"""
    You are an AI assistant who is expert in analysing data items of a list to produce a short description about the column.
    \n
    Given the name of column: {name_of_columns_of_eachtable}
    \n
    Given, values of data items in this column: {random_data_of_column_of_table}
    \n
    Your task is to generate a short yet descriptive description about this particular column by understanding the context using name of this column, and values of data items in this column.
    Include column name within ` ` symbols in the generated description as it is.
    \n
    For example,\nExample 1 - Given name of column: 'started_at' and value of data items in column: '[2023-05-12 08:30:00, 2023-06-15 14:45:00, 2023-07-01 09:00:00, 2023-08-10 11:20:00, 2023-09-22 16:10:00]',
    the description about this column will be something like 'The column `started_at` contains timestamps indicating when an event began. The values are in date-time format, representing the starting date and time for various records.'
    \nExample 2 - Given name of column: 'avatar_id' and value of data items in column: '[A101, A102, A103, A104, A105]',
    the description about this column will be something like 'The column `avatar_id` stores unique identifiers for avatars which are workers on ground. These IDs are used to differentiate between different avatars in the system, allowing each avatar to be uniquely referenced',
    """
    try:
        # Call the function to generate column description using the provided model
        responses = get_response(model, prompt, safety_configs, generation_config)

        # Return the generated description if available
        if responses:
            logger.info(f"Table: {table_name}, Column: {name_of_columns_of_eachtable}, Generated col description: {responses}.") 
        else:
            logger.info("No column desription generated from LLM available")
        return col_description

    except Exception as e:
        # Handle any exceptions that may occur during content generation
        logger.error(f"Error generating column description: {e}")
        return "An error occurred while generating the column description."
