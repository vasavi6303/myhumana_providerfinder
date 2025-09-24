from pydantic import BaseModel
from typing import Optional

class SearchRequest(BaseModel):
    query: str
    location: Optional[str] = None
    specialty: Optional[str] = None
