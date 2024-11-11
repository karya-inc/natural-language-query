import json
import os
from typing import Dict, Any
from utils.logger import setup_logging, disable_logging
import shutil

# Initialize logger
logger = setup_logging(
    logger_name="file_io",
    success_file="file_io_success.log",
    error_file="file_io_error.log"
)

# # Disable logging if not needed
# disable_logging('file_io')


def load_json(path: str) -> Dict[str, Any]:
    """
    Load JSON data from a file.

    Args:
        path (str): The path to the JSON file.

    Returns:
        Dict[str, Any]: The loaded JSON data as a dictionary.
    """
    try:
        with open(path, 'r') as file:
            logger.info(f"Successfully loaded JSON from {path}")
            return json.load(file)
    except FileNotFoundError:
        # Handle the case where the file is not found
        logger.error(f"File not found: {path}")
        raise FileNotFoundError(f"The file at {path} was not found.")
    except json.JSONDecodeError:
        # Handle invalid JSON format
        logger.error(f"Invalid JSON format in file: {path}")
        raise ValueError(f"The file at {path} is not a valid JSON file.")
    except Exception as e:
        # Catch any other exceptions
        logger.error(f"Error loading the file at {path}: {e}")
        raise RuntimeError(f"An error occurred while loading the file at {path}: {e}")


def check_intermediate_folder(folder_path: str) -> None:
    """
    Check if the intermediate folder exists and is empty.

    Args:
        folder_path (str): The path to the intermediate folder.

    Returns:
        None
    """

    # Create the folder if it doesn't exist
    if not os.path.exists(folder_path):
        logger.info(f"Folder {folder_path} does not exist. Creating it...")
        os.makedirs(folder_path)
        logger.info(f"Created folder: {folder_path}")
    # If exists then empty it
    else:
        logger.info(f"Folder {folder_path} already exists. Emptying it...")
        # Remove all contents of the folder
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # Remove file or symbolic link
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Remove directory and all its contents
            except Exception as e:
                logger.error(f"Failed to delete {file_path}. Reason: {e}")
        logger.info(f"Emptied folder: {folder_path}")


def save_json(data: Dict[str, Any],
    folder_path: str,
    file_path: str) -> None:
    """
    Save data to a JSON file.

    Args:
        data (Dict[str, Any]): The data to save.
        path (str): The path where the JSON file will be saved.

    Returns:
        None
    """
    try:
        file_full_path = os.path.join(folder_path, file_path)
        with open(file_full_path, 'w') as file:
            json.dump(data, file, indent=4)
            logger.info(f"Successfully saved intermediate JSON file to {file_full_path}")
    except IOError as e:
        # Handle file I/O errors (e.g., permission issues)
        logger.error(f"Error saving intermediate JSON file at {file_full_path}: {e}")


def combine_json_files(intermediate_processed_files_path: str,
enriched_schema_path: str    
) -> None:
    """
    Combine all JSON files from a folder into a single JSON file.

    Args:
        intermediate_processed_files_path (str): The folder containing the JSON files to combine.
        enriched_schema_path (str): The path where the combined JSON will be saved.

    Returns:
        None
    """
    # Initialize the combined data
    combined_data = {}

    # Get all .json files in the folder
    json_files = [f for f in os.listdir(intermediate_processed_files_path) if f.endswith('.json')]

    # Combine the contents of all JSON files
    for json_file in json_files:
        file_path = os.path.join(intermediate_processed_files_path, json_file)
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                combined_data.update(data)
                logger.info(f"Successfully read data from {file_path}")
        except json.JSONDecodeError:
            # Handle invalid JSON file format
            logger.warning(f"Skipping invalid JSON file: {file_path}")
        except Exception as e:
            # Handle other exceptions during file reading
            logger.error(f"Error reading {file_path}: {e}")

    # Save the combined data to the output file
    try:
        save_json(combined_data, f"{intermediate_processed_files_path}/", enriched_schema_path)
    except Exception as e:
        # Handle errors during saving the combined data
        logger.error(f"Error saving combined JSON to {enriched_schema_path}: {e}")