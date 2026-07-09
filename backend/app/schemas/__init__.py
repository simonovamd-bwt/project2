from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class Credentials(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    # bcrypt only hashes the first 72 bytes, so reject longer passwords up front
    # rather than silently truncating them.
    password: str = Field(min_length=6, max_length=72)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str


class DocumentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    document_type: str = Field(default="Mutual NDA", max_length=128)
    form_values: dict = Field(default_factory=dict)
    markdown: str = Field(min_length=1)


class DocumentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    document_type: str
    created_at: datetime


class DocumentOut(DocumentSummary):
    form_values: dict
    markdown: str


class ChatRequest(BaseModel):
    """The answers collected so far. The frontend re-sends the full map each
    turn (stateless), and the mock service replies with the next question."""

    answers: dict[str, str] = Field(default_factory=dict)


class ChatResponse(BaseModel):
    """A single structured turn: chat text + extracted fields + live preview.

    Mirrors the shape a real non-streaming structured-output model would
    return, so no code changes when a live LLM eventually replaces the mock.
    """

    reply: str
    next_field: str | None
    complete: bool
    fields: dict[str, str]
    document_type: str
    title: str
    markdown: str
    total_questions: int
    answered: int
