"""Mock AI chat endpoint for guided document drafting (issue #2).

No LLM is called. The endpoint delegates to ``app.services.chat``, which
deterministically decides the next question (or completion) from the answers
collected so far and rebuilds the live preview. Public by design (freemium):
anyone can draft via chat; saving the result is what requires auth
(``POST /api/documents``).
"""

from fastapi import APIRouter

from app.schemas import ChatRequest, ChatResponse
from app.services import chat as chat_service

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat_turn(payload: ChatRequest) -> ChatResponse:
    turn = chat_service.advance(payload.answers)
    return ChatResponse(
        reply=turn.reply,
        next_field=turn.next_field,
        complete=turn.complete,
        fields=turn.fields,
        document_type=turn.document_type,
        title=turn.title,
        markdown=turn.markdown,
        total_questions=turn.total_questions,
        answered=turn.answered,
    )
