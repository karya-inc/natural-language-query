import sqlite3
from datetime import date, datetime, time


def get_sqlite_type(value):
    if isinstance(value, int):
        return "INTEGER"
    elif isinstance(value, float):
        return "REAL"
    elif isinstance(value, str):
        return "TEXT"
    elif isinstance(value, list):
        return "BLOB"
    elif isinstance(value, (date, datetime)):
        return "TEXT"  # Store date/datetime as ISO 8601 strings (e.g., "YYYY-MM-DD HH:MM:SS")
    elif isinstance(value, time):
        return "TEXT"  # Store time as TEXT (e.g., "HH:MM:SS")
    else:
        return "TEXT"  # Default to TEXT for unsupported types


def dict_to_create_table(table_name, data_dict):
    columns = []
    for key, value in data_dict.items():
        sqlite_type = get_sqlite_type(value)
        columns.append(f"{key} {sqlite_type}")
    columns_def = ", ".join(columns)
    create_table_stmt = f"CREATE TABLE {table_name} ({columns_def});"
    return create_table_stmt


class EphemeralStorage:
    def __init__(self, connection, cursor):
        self.connection = connection
        self.cursor = cursor


class EphemeralTools:
    def get_ephemeral_storage(self):
        if not self.connection:
            self.connection = sqlite3.connect(":memory:")
            self.cursor = self.connection.cursor()

        return EphemeralStorage(self.connection, self.cursor)
