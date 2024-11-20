import pandas as pd
from typing import Any, Optional, Sequence
from pandas.io.parquet import json
from sqlalchemy.engine import Row


def convert_rows_to_serializable(rows: Sequence[Row[Any]]) -> list[dict[str, Any]]:
    df = pd.DataFrame(rows)

    for column in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[column]):
            try:
                df[column] = df[column].astype(str)
            except Exception as e:
                print(f"Error converting column {column} to isoformat: {e}")

    return df.to_dict(orient="records")


def convert_rows_to_json(rows: Sequence[Row[Any]]) -> Optional[str]:
    """
    Convert a list of rows generated from a database query into a json string
    """

    records = convert_rows_to_serializable(rows)
    return json.dumps(records)
