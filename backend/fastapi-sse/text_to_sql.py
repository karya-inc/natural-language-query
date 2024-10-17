from dotenv import load_dotenv
import os
import google.generativeai as genai
import grpc


load_dotenv()
my_api_key = os.getenv("GEMINI_API_KEY")
model_name=os.getenv("LLM_MODEL_NAME")

if not my_api_key:
    raise ValueError("API key not found. Make sure your .env file contains GEMINI_API_KEY.")
print("API Key loaded successfully!")

genai.configure(api_key=my_api_key)
model = genai.GenerativeModel(model_name) # "gemini-1.5-pro" or "gemini-1.5-flash"

def sql_generator(user_query):
    prompt = f"""
    ###You are an expert AI assistant who converts provided ""English Question"" to optimized ""SQL Query"".
    ### User Query: {user_query}
    """

    responses = model.generate_content(prompt, stream=True)

    return responses


if __name__ == "__main__":
    test_query = "What is the total sales for last month?"
    responses = sql_generator(test_query)
    print(responses)

