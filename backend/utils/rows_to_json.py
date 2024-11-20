import pandas as pd
from typing import Any, Optional, Sequence
from sqlalchemy.engine import Row


def convert_rows_to_json(rows: Sequence[Row[Any]]) -> Optional[str]:
    """
    Convert a list of rows generated from a database query into a json string
    """

    df = pd.DataFrame(rows)
    return df.to_json(orient="records")
