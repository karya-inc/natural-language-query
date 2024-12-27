from text2sql import run_text2sql

def test():
    """
    Test function to demonstrate the usage of the text-to-SQL pipeline.
    Passes a custom question to the `run_text2sql` function and prints the SQL response.
    """
    # Define your custom question
    question = "Write a SQL query to retrieve the full names of workers along with the names of tasks they have worked on and the total credits they have earned for each task. The results should be grouped by worker and task, and ordered by the total credits earned in descending order."

    # Run the text-to-SQL process with the custom question
    response = run_text2sql(question)

    # Print the response
    print("Generated SQL Query:")
    print(response)

if __name__ == "__main__":
    test()