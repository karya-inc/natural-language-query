from fastapi import FastAPI
import logging

# Set up logging configuration
log_format = '%(asctime)s - %(levelname)s - %(message)s'

# Create two handlers: one for console output and one for file output
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(log_format))
console_handler.setLevel(logging.INFO)

# Create file handlers for success and error logs
success_handler = logging.FileHandler('success.log')
success_handler.setFormatter(logging.Formatter(log_format))
success_handler.setLevel(logging.INFO)

error_handler = logging.FileHandler('error.log')
error_handler.setFormatter(logging.Formatter(log_format))
error_handler.setLevel(logging.ERROR)

# Create a logger and add the handlers
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(console_handler)
logger.addHandler(success_handler)
logger.addHandler(error_handler)

# Create the FastAPI app
app = FastAPI()

@app.get("/chat")
async def stream_sql_query_responses(query: str):
    logger.info(f"Received query: {query}")
    return {"message": "This is a placeholder response."}