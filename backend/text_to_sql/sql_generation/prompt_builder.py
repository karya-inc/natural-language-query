from typing import Any
from utils.logger import setup_logging, disable_logging

# Setting up logging
logger = setup_logging(
    logger_name="prompt_builder",
    success_file="prompt_builder_success.log",
    error_file="prompt_builder_error.log"
)

# Optionally, disable logging if not needed
# disable_logging('C:/Users/13mal/Documents/nlq_generator/text2sql/logs/main_schema_enrichment')

def build_sql_prompt(enriched_db_schema: Any, question: str, query_dialect: str) -> str:
    """Build the prompt for SQL query generation."""
    try:
        # Constructing the first part of the prompt
        prompt_part1 = """
        ### You are an expert AI assistant who takes context from provided "Database Schema" to convert provided "English Question" to optimized "SQL Query".
        #
        ### Your first task is to understand "English Question" provided below and values of following keys of all columns of all tables from "Context" provided below:
        # "table_name", "Column", "Column_description" and "Primary Key".
        #
        ### "Context" provided below is a "Database Schema" in following JSON format:
        # table_name: {"Column": [string value that refers to the name of the column in the database table], "Type": [string value represents the data type of the column], "Nullable": [boolean value that indicates whether the column can contain NULL values], "Primary Key": [boolean value that specifies whether the column is a primary key in the table], "Column_description": [string value describing use of column and type of value stored in column]}
        #
        ### Your second task is to then provide "Output" corresponding to preceding "English Question".
        # {"SQL Query": "your-sql-query", "Assumptions": "your-assumptions", "Reason of Failure": "your-reason-of-failure"}
        #
        """

        # Constructing the second part of the prompt
        prompt_part2 = f"""
        ### "Context": {enriched_db_schema}
        #
        ### "English Question": {question}
        #
        """

        # Constructing the third part of the prompt
        prompt_part3 = f"""
        ### "Output" should be ONLY JSON. No ``` in beginning or at end and no word "json"
        ### In "Output" JSON response, substitute "your-sql-query" with {query_dialect} Query only with no additional assumptions and explanations, no ``` in beginning or at end and no word "sql".
        ### If you don't know what Microsoft Postgres SQL Server Query to generate corresponding to given "English Question", then do not hallucinate incorrect query and substitute "your-sql-query" with None.
        ### In "Output" JSON response, substitute "your-assumptions" with a short summary of what all things have you assumed while generating "your-sql-query" that needs additional inputs from user. Omit when not applicable and substitute "your-assumptions" with None.
        ### In "Output" JSON response, substitute "your-reason-of-failure" with a short reason of why you are not able to generate "your-sql-query". Omit when not applicable and substitute "your-reason-of-failure" with None.
        #
        """

        # Example cases for reference
        few_shot_examples = """
        ### For example,
        # "English Question" - Fetch the task ID, worker ID, duration, and sentence from the microtask_assignment and microtask tables for specific tasks (IDs: 852, 831, 832, 833, 834, 835, 836) where the status of the assignments is either 'COMPLETED' or 'VERIFIED'. Ensure to extract the duration from the output JSON and the sentence from the input JSON.
        # "Output" JSON response - {SQL Query: SELECT ma.task_id as task_id, ma.worker_id, ma.output->'data'->>'duration' as duration, mt.input->'data'->>'sentence' as sentence from microtask_assignment as ma join microtask as mt on ma.microtask_id = mt.id where ma.task_id in (852, 831, 832, 833, 834, 835, 836) and ma.status in ('COMPLETED','VERIFIED');}
        #
        # "English Question" - Fetch detailed information about workers who have completed verified tasks, including their IDs, names, phone numbers, birth years, task names, questions, and selected options. Filter results based on specific task tags and order by task ID and worker ID.
        # "Output" JSON response - {SQL Query: SELECT w.id AS id, w.profile->'data'->'full_name' AS name, w.phone_number AS phone_number, w.profile->'data'->>'yob' AS birth_year, t.name AS task_name,  regexp_replace(mi.input->'data'->>'question', '<[^>]+>', '', 'g') AS question, mta.output->'data'->'option_selected' as option_selected FROM microtask_assignment mta JOIN worker w ON w.id = mta.worker_id JOIN task t ON mta.task_id = t.id JOIN microtask mi ON mi.id = mta.microtask_id WHERE mta.task_id IN (SELECT id FROM task WHERE itags->>'itags' LIKE '%[\"bmgf\", \"prod\", \"task-2\", \"primer\"%') and mta.status = 'VERIFIED' order by mta.task_id, w.id;}
        """

        # Final concatenation of all prompt parts
        final_prompt = prompt_part1 + prompt_part2 + prompt_part3 + few_shot_examples

        # Log the generated prompt
        logger.info("SQL prompt generated successfully.")
        return final_prompt

    except Exception as e:
        logger.error(f"Error while building SQL prompt: {str(e)}")
        raise


def build_feedback_prompt(enriched_db_schema: Any, initial_question: str, query_dialect: str, initial_sql_query: str, corrective_feedback: str) -> str:
    """Build the prompt for SQL correction based on feedback."""
    try:
        # Constructing the first part of the feedback prompt
        prompt_part1 = """
        ### You are an expert AI assistant who corrects the "Initial SQL Query" based on "Corrective Feedback" and "Database Schema".
        #
        ### Your first task is to understand "Corrective Feedback" provided below:
        #
        """    

        # Constructing the second part with corrective feedback
        prompt_part2 = f"""
        ### "Corrective Feedback": {corrective_feedback}
        """

        # Constructing the third part to understand the database schema
        prompt_part3 = """
        ### Your second task is to understand values of following keys: "table_name", "Column", "Column_description" and "Primary Key" corresponding to all columns of all tables from "Context" provided below:
        #
        ### "Context" provided below is a "Database Schema" in following JSON format:
        # table_name: {"Column": [string value that refers to the name of the column in the database table], "Type": [string value represents the data type of the column], "Nullable": [boolean value that indicates whether the column can contain NULL values], "Primary Key": [boolean value that specifies whether the column is a primary key in the table], "Column_description": [string value describing use of column and type of value stored in column]}
        #
        """

        # Constructing the fourth part with enriched database schema
        prompt_part4 = f"""
        ### "Context": {enriched_db_schema}
        #
        """

        # Constructing the fifth part for providing the corrected SQL query
        prompt_part5 = """
        ### Your third task is to then provide "Output" corresponding to below "Initial User Question" by correcting the below "Initial User Question" based on above "Corrective Feedback" within context of above "Database Schema".
        # "Format for Output": {"Corrected SQL Query": "your-sql-query", "Assumptions": "your-assumptions", "Reason of Failure": "your-reason-of-failure"}
        #
        """

        # Constructing the sixth part with the initial user question and query
        prompt_part6 = f"""
        ### "Initial User Question": {initial_question}
        #
        ### "Initial SQL Query": {initial_sql_query}
        #
        """

        # Constructing the seventh part for JSON output format
        prompt_part7 = f"""
        ### "Output" should be ONLY JSON. No ``` in beginning or at end and no word "json"
        ### In "Output" JSON response, substitute "your-sql-query" with {query_dialect} Query only with no additional assumptions and explanations, no ``` in beginning or at end and no word "sql".
        ### If you don't know what Microsoft Postgres SQL Server Query to generate corresponding to given "English Question", then do not hallucinate incorrect query and substitute "your-sql-query" with None.
        ### In "Output" JSON response, substitute "your-assumptions" with a short summary of what all things have you assumed while generating "your-sql-query" that needs additional inputs from user. Omit when not applicable and substitute "your-assumptions" with None.
        ### In "Output" JSON response, substitute "your-reason-of-failure" with a short reason of why you are not able to generate "your-sql-query". Omit when not applicable and substitute "your-reason-of-failure" with None.
        """

        final_prompt = prompt_part1 + prompt_part2 + prompt_part3 + prompt_part4 + prompt_part5 + prompt_part6 + prompt_part7

        return final_prompt

    except Exception as e:
        logger.error(f"Error while building feedback SQL prompt: {str(e)}")
        raise

