from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

class ModelName(str, Enum):
    GPT4_MINI = "gpt-4o-mini"
    GPT4 = "gpt-4o"

class QueryInput(BaseModel):
    question: str
    sessionId: str | None = Field(default=None)
    model: str = Field(default=ModelName.GPT4_MINI.value)

class QueryResponse(BaseModel):     # Not used when streaming the output
    answer: str
    sessionId: str
    model: str

class DocumentInfo(BaseModel):
    id: int
    filename: str
    uploadTimestamp: datetime

class DeleteFileRequest(BaseModel):
    fileId: int