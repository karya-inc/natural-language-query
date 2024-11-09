from enum import Enum


class AgentStatus(Enum):
    CATALOGING = "Agent is cataloging data..."
    GENERATING_QUERIES = "Agent is generating queries..."
    EXECUTING_QUERIES = "Agent is executing queries..."
    PROCESSING_RESULTS = "Agent is processing intermediate results..."
    EVALUATING_RESULTS = "Agent is evaluating results..."
    REFINING_QUERY = "Agent is refining the query..."
    TASK_COMPLETED = "Agent has completed the task."
