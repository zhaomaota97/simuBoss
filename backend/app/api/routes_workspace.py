from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_session
from app.db import get_db
from app.models import SessionToken, WorkspaceDocument
from app.schemas.workspace import WorkspaceBundleOut, WorkspaceDocumentIn, WorkspaceDocumentOut

router = APIRouter(prefix="/workspace", tags=["workspace"])

ALLOWED_KINDS = {"simuboss", "assets", "runtime"}


def _validate_kind(kind: str) -> str:
    if kind not in ALLOWED_KINDS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace document not found")
    return kind


@router.get("", response_model=WorkspaceBundleOut)
def list_workspace_documents(
    session: SessionToken = Depends(get_current_session),
    db: Session = Depends(get_db),
):
    documents = (
        db.query(WorkspaceDocument)
        .filter(WorkspaceDocument.user_id == session.user_id)
        .all()
    )
    return WorkspaceBundleOut(documents={item.kind: item.data for item in documents})


@router.get("/{kind}", response_model=WorkspaceDocumentOut)
def get_workspace_document(
    kind: str,
    session: SessionToken = Depends(get_current_session),
    db: Session = Depends(get_db),
):
    kind = _validate_kind(kind)
    document = (
        db.query(WorkspaceDocument)
        .filter(WorkspaceDocument.user_id == session.user_id, WorkspaceDocument.kind == kind)
        .first()
    )
    if not document:
        return WorkspaceDocumentOut(kind=kind, data={})
    return WorkspaceDocumentOut(kind=kind, data=document.data)


@router.put("/{kind}", response_model=WorkspaceDocumentOut)
def save_workspace_document(
    kind: str,
    payload: WorkspaceDocumentIn,
    session: SessionToken = Depends(get_current_session),
    db: Session = Depends(get_db),
):
    kind = _validate_kind(kind)
    document = (
        db.query(WorkspaceDocument)
        .filter(WorkspaceDocument.user_id == session.user_id, WorkspaceDocument.kind == kind)
        .first()
    )
    if not document:
        document = WorkspaceDocument(user_id=session.user_id, kind=kind, data=payload.data)
        db.add(document)
    else:
        document.data = payload.data
    db.commit()
    db.refresh(document)
    return WorkspaceDocumentOut(kind=document.kind, data=document.data)
