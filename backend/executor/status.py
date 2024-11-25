from enum import Enum


class AgentStatus(Enum):
    ANALYZING_INTENT = "Analyzing the intent of the query..."
    CATALOGING = "Cataloging data..."
    FIXING = "Fixing problems with the SQL query..."
    GENERATING_QUERIES = "Generating queries..."
    EXECUTING_QUERIES = "Executing queries..."
    EVALUATING_RESULTS = "Evaluating results..."
    REFINING_QUERY = "Refining the query..."
    TASK_COMPLETED = "Agent has completed the task."
    TASK_FAILED = "Agent has failed to complete the task."
