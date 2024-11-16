from enum import Enum


class AgentStatus(Enum):
    ANALYZING_INTENT = "Analyzing the intent of the query..."
    CATALOGING = "Cataloging data..."
    GENERATING_QUERIES = "Generating queries..."
    EXECUTING_QUERIES = "Executing queries..."
    EXECUTE_REFINED_QUERY = "Executing the refined query..."
    EVALUATING_RESULTS = "Evaluating results..."
    REFINING_QUERY = "Refining the query..."
    TASK_COMPLETED = "Agent has completed the task."
    TASK_FAILED = "Agent has failed to complete the task."
