from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.routes.auth import get_current_user
from app.models.document import Document
from app.models.expert import Expert
from app.schemas.document import DocumentCreate, DocumentRead
from app.services.vector_store import add_documents_to_expert

router = APIRouter()

@router.post("/upload", response_model=DocumentRead)
def upload_document(document_create: DocumentCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    expert = db.get(Expert, document_create.expert_id)
    if not expert:
        raise HTTPException(status_code=404, detail="Expert not found")
    if expert.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Can only upload documents to your own profile")
    
    doc = Document(
        expert_id=document_create.expert_id,
        file_url=None,
        file_type=document_create.file_type,
        text=document_create.text,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    add_documents_to_expert(document_create.expert_id, [{"text": document_create.text, "file_type": document_create.file_type}])
    return doc

@router.post("/upload-file", response_model=DocumentRead)
async def upload_file(
    expert_id: int = Form(...),
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    expert = db.get(Expert, expert_id)
    if not expert:
        raise HTTPException(status_code=404, detail="Expert not found")
    if expert.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Can only upload documents to your own profile")
    
    content = await file.read()
    text = content.decode('utf-8', errors='ignore')
    
    doc = Document(
        expert_id=expert_id,
        file_url=file.filename,
        file_type=file.content_type or "file",
        text=text,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    add_documents_to_expert(expert_id, [{"text": text, "file_type": file.content_type or "file"}])
    return doc

@router.get("/list/{expert_id}", response_model=list[DocumentRead])
def list_documents(expert_id: int, db: Session = Depends(get_db)):
    return db.query(Document).filter(Document.expert_id == expert_id).all()

@router.delete("/delete/{document_id}")
def delete_document(document_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    expert = db.get(Expert, doc.expert_id)
    if expert.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Can only delete your own documents")
    
    db.delete(doc)
    db.commit()
    return {"status": "deleted"}
