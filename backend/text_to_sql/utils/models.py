from typing import Dict
from utils.generation_limiter import generate_content_with_limit
import google.generativeai as genai
from utils.logger import setup_logging

# Setup logger
logger = setup_logging(
    logger_name="main_schema_enrichment",
    success_file="main_schema_enrichment_success.log",
    error_file="main_schema_enrichment_error.log"
)

def initialize_model(api_key: str) -> genai.GenerativeModel:
    """Initialize the Gemini model using the provided API key.
    
    Args:
        api_key (str): The API key to configure the model.

    Returns:
        genai.GenerativeModel: The initialized model.
    """
    try:
        # Configure the model using the provided API key
        genai.configure(api_key=api_key)

        # # Get a list of all Gemini models that we have access to via this API KEy
        # for model in genai.list_models():
        #   if 'generateContent' in model.supported_generation_methods:
        #     print(model.name)
        
        # Initialize and return the specific Gemini model
        initialized_model = genai.GenerativeModel("gemini-1.5-flash")
        logger.info(f"Model 'gemini-1.5-flash' initialized successfully.")
        return initialized_model

    except Exception as e:
        logger.error(f"Error initializing the model: {e}")
        raise RuntimeError(f"Failed to initialize model: {e}") from e


def get_response(
    model: genai.GenerativeModel,
    prompt: str,
    safety_configs: Dict,
    generation_config: Dict
) -> str:
    """Get a response from the model given a prompt and configurations.
    
    Args:
        model (genai.GenerativeModel): The initialized generative model.
        prompt (str): The input prompt to generate content for.
        safety_configs (Dict): The safety configurations for content generation.
        generation_config (Dict): The configurations for controlling the content generation.

    Returns:
        str: The generated content from the model, or an empty string in case of failure.
    """
    try:
        # Generate content using the provided model and configurations
        responses = generate_content_with_limit(
            model,
            prompt,
            generation_config=generation_config,
            safety_settings=safety_configs
        )
        logger.info("Content generated successfully.")
        return responses.text

    except Exception as e:
        # Log the error and return an empty string if content generation fails
        logger.error(f"Error generating content: {e}")
        return ""