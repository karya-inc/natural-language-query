from datetime import date, datetime
from decimal import Decimal
import pandas as pd
from typing import Any, Optional, Sequence
from pandas.io.parquet import json
from sqlalchemy import UUID
from sqlalchemy.engine import Row


def convert_rows_to_serializable(rows: Sequence[Row[Any]]) -> list[dict[str, Any]]:
    df = pd.DataFrame(rows)

    for column in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[column]):
            try:
                df[column] = df[column].astype(str)
            except Exception as e:
                print(f"Error converting column {column} to isoformat: {e}")

        # Convert Decimal to float
        if pd.api.types.is_float_dtype(df[column]):
            try:
                df[column] = df[column].astype(float)
            except Exception as e:
                print(f"Error converting column {column} to float: {e}")

    return df.to_dict(orient="records")


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    if isinstance(obj, (bytes, bytearray)):
        return obj.decode("utf-8")

    if isinstance(
        obj,
        (
            Decimal,
            UUID,
        ),
    ):
        return str(obj)

    raise TypeError("Type %s not serializable" % type(obj))


def convert_rows_to_json(rows: Sequence[Row[Any]]) -> Optional[str]:
    """
    Convert a list of rows generated from a database query into a json string
    """

    records = convert_rows_to_serializable(rows)
    return json.dumps(records, default=json_serial)
