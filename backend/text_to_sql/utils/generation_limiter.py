import logging
from functools import wraps
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def limit_calls_per_minute(max_calls=4, interval=60):
    """
    Decorator to limit the rate of function calls to Gemini to a maximum specified number within a time interval.
    
    Args:
        max_calls (int): Maximum number of calls allowed per interval.
        interval (int): Time interval in seconds within which the call limit applies.
        
    Returns:
        func: Wrapped function with rate-limiting behavior.
    """
    def decorator(func):
        
        last_reset_time = [time.time()]
        call_count = [0]

        @wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()

            # Reset call count if the interval has passed
            if current_time - last_reset_time[0] >= interval:
                call_count[0] = 0
                last_reset_time[0] = current_time

            if call_count[0] < max_calls:
                call_count[0] += 1
                return func(*args, **kwargs)
            else:
                # Calculate remaining wait time before next allowed call
                wait_time = interval - (current_time - last_reset_time[0])
                logger.info("Rate limit reached. Waiting %.2f seconds before retrying.", wait_time)
                time.sleep(max(0, wait_time))

                # Reset after waiting
                call_count[0] = 1
                last_reset_time[0] = time.time()
                return func(*args, **kwargs)

        return wrapper
    return decorator


@limit_calls_per_minute(max_calls=4, interval=60)
def generate_content_with_limit(model, prompt, generation_config, safety_settings):
    """
    Generates content via Gemini with rate limiting applied.

    Args:
        model: The model instance used for content generation.
        prompt (str): The input text to generate content from.
        generation_config: Configuration settings for generation.
        safety_settings: Safety settings for content generation.
        
    Returns:
        Generated content based on the model and prompt provided.
    """
    return model.generate_content(
        prompt,
        generation_config=generation_config,
        safety_settings=safety_settings
    )