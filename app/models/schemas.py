from pydantic import BaseModel
from typing import Optional


class IncomingMessage(BaseModel):
    sender: str
    message_type: str
    text: Optional[str] = None
    media_url: Optional[str] = None