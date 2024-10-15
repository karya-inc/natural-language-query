from dotenv import load_dotenv
import os
import google.generativeai as genai


load_dotenv()
my_api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=my_api_key)
model = genai.GenerativeModel("gemini-1.5-flash") # gemini-1.5-pro

def sql_generator(user_query):
    model=genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction="You are an expert AI assistant who converts provided ""English Question"" to optimized ""SQL Query""")

    prompt = f"""
    ###You are an expert AI assistant who converts provided ""English Question"" to optimized ""SQL Query"".
    ### User Query: {user_query}
    """

    responses = model.generate_content(prompt, stream=True)

    return responses


if __name__ == "__main__":
    test_query = "What is the total sales for last month?"
    response = sql_generator(test_query)

