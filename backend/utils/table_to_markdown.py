from executor.models import QueryResults


def get_table_markdown(data: QueryResults) -> str:
    """
    Convert the query results to a markdown table
    """
    if not data:
        return "No data found"

    # Get the column names
    columns = data[0].keys()

    # Create the markdown table
    header_markdown = "| " + " | ".join(columns) + " |\n"
    header_markdown += "| " + " | ".join(["---"] * len(columns)) + " |\n"

    row_markdown = ""
    for row in data:
        cells = [str(row[column]) for column in columns]
        row_markdown += "| " + " | ".join(cells) + " |\n"

    markdown = header_markdown + row_markdown
    return markdown
