import os
import google.generativeai as genai
from google.generativeai.types import generation_types


my_api_key = os.getenv("GEMINI_API_KEY")
model_name = os.getenv("LLM_MODEL_NAME")

def sql_generator(user_query) -> generation_types.GenerateContentResponse:
    """
    This is the test gemini sql generator query
    This will be replace with Agentic Loop
    """
    if my_api_key is None or model_name is None:
        raise ValueError("API Key or Gemini model name is not set in environment variables")

    genai.configure(api_key=my_api_key)
    model = genai.GenerativeModel(model_name)
    prompt = f"""
    ###You are an expert AI assistant who converts provided ""English Question"" to optimized ""SQL Query"".
    ### User Query: {user_query}
    """
    responses = model.generate_content(prompt, stream=True)

    return responses