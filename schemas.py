from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        description="User research topic or prompt."
    )


class ChatResponse(BaseModel):
    response: str = Field(
        ...,
        description="Final markdown research report."
    )


class StreamEvent(BaseModel):
    type: str = Field(..., description="Type of event emitted during execution.")
    message: Optional[str] = Field(None, description="Human readable event message.")
    tool: Optional[str] = Field(None, description="Executed tool identifier.")
    step: Optional[int] = Field(None, description="Current agent iteration step.")
    plan: Optional[str] = Field(None, description="Full strategic research plan.")
    report: Optional[str] = Field(None, description="Generated final markdown report.")
    details: Optional[Dict[str, Any]] = Field(None, description="Execution metadata.")