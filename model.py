from typing import List
from pydantic import BaseModel


class ResponseModel(BaseModel):
    """
    #### Response model for the endpoint
    """
    documentID: str = None
    imagePath: str = None
    boxes: List[str] = []
    confidences: List[str] = []
    error: str = None
