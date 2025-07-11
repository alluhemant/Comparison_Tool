from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4


class ComparisonResult(BaseModel):
    id: UUID = Field(default_factory=uuid4)  # Auto-generate UUID if not provided
    tibco_response: str
    python_response: str
    differences: str
    metrics: dict
    created_at: datetime = Field(default_factory=datetime.now)  # Auto-set current time
