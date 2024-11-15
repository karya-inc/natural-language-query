from typing import Literal
from pydantic import BaseModel

class QueryType(BaseModel):
    query_type: Literal["QUESTION_ANSWERING", "REPORT_GENERATION"]


class RelevantCatalog(BaseModel):
    requires_multiple_catalogs: bool
    database_name: str