from sqlalchemy import create_engine, inspect, text
from urllib.parse import quote_plus
from dotenv import load_dotenv
import os
from typing import List, Optional
from utils.logger import setup_logging, disable_logging

# Initialize logger
logger = setup_logging(
    logger_name="database",
    success_file="database_success.log",
    error_file="database_error.log"
)

# # Disable logging if not needed
disable_logging('database')

# Load environment variables from .env file
load_dotenv()

# Access environment variable for connection string to PostgreSQL database
PASSWORD: str = quote_plus(os.getenv("PASSWORD"))
DBNAME: str = os.getenv("DBNAME")
HOSTNAME: str = os.getenv("HOSTNAME")
USER: str = os.getenv("USER")
CONN_STRING: str = f"postgresql+pg8000://{USER}:{PASSWORD}@{HOSTNAME}/{DBNAME}"


def get_table_names() -> List[str]:
    """
    Fetches all table names from the PostgreSQL database.

    Returns:
        List[str]: List of table names present in the database.

    Raises:
        Exception: If unable to connect to the database or fetch table names.
    """
    try:
        # Create an engine to connect to the PostgreSQL database
        engine = create_engine(CONN_STRING)
        inspector = inspect(engine)
        table_names = inspector.get_table_names()  # Retrieve table names
        logger.info("Successfully fetched table names.")
        return table_names
    except Exception as e:
        # Log error if unable to fetch table names
        logger.error(f"Error fetching table names: {e}")
        raise Exception(f"Error fetching table names: {e}")


def get_column_random_data(table_name: str, column_name: str) -> Optional[List[str]]:
    """
    Fetches random data from a specified column in a specified table.

    Args:
        table_name (str): Name of the table from which to fetch data.
        column_name (str): Name of the column from which to fetch data.

    Returns:
        List[str]: A list of random values from the specified column.

    Raises:
        Exception: If unable to execute the query or retrieve data.
    """
    try:
        # SQL query to fetch random data from the specified column
        query = f'SELECT "{column_name}" FROM {table_name} ORDER BY RANDOM() LIMIT 9'
        
        # Create an engine to connect to the PostgreSQL database
        engine = create_engine(CONN_STRING)
        
        with engine.connect() as connection:
            result = connection.execute(text(query))  # Execute query
            random_data = [row[0] for row in result]  # Extract column data
            logger.info(f"Successfully fetched random data from {column_name} in {table_name}.")
            return random_data
    except Exception as e:
        # Log error if unable to fetch random data
        logger.error(f"Error fetching random data from {table_name} column {column_name}: {e}")
        raise Exception(f"Error fetching random data from {table_name} column {column_name}: {e}")
