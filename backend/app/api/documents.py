"""Document-history endpoints: list, create, and fetch saved documents."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from app.api.deps import current_user
from app.db.session import get_db
from app.models import Document, User
from app.schemas import DocumentCreate, DocumentOut, DocumentSummary

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.get("", response_model=list[DocumentSummary])
def list_documents(
    user: User = Depends(current_user), db: DbSession = Depends(get_db)
) -> list[Document]:
    stmt = (
        select(Document)
        .where(Document.user_id == user.id)
        .order_by(Document.created_at.desc())
    )
    return list(db.scalars(stmt))


@router.post("", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
def create_document(
    payload: DocumentCreate,
    user: User = Depends(current_user),
    db: DbSession = Depends(get_db),
) -> Document:
    doc = Document(
        user_id=user.id,
        title=payload.title.strip(),
        document_type=payload.document_type,
        form_values=payload.form_values,
        markdown=payload.markdown,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.get("/{doc_id}", response_model=DocumentOut)
def get_document(
    doc_id: int,
    user: User = Depends(current_user),
    db: DbSession = Depends(get_db),
) -> Document:
    doc = db.get(Document, doc_id)
    if doc is None or doc.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")
    return doc
