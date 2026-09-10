from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.routes.auth import get_current_user
from app.models.document import Document
from app.models.expert import Expert
from app.schemas.document import DocumentCreate, DocumentRead
from app.services.vector_store import add_documents_to_expert, query_expert_documents
from app.services.llm_service import llm_service

router = APIRouter()


class DocumentSearchRequest(BaseModel):
    query: str
    top_k: int = 5


class DocumentRAGRequest(BaseModel):
    query: str
    expert_id: int | None = None


@router.post("/upload", response_model=DocumentRead)
def upload_document(document_create: DocumentCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    expert = db.get(Expert, document_create.expert_id)
    if not expert:
        raise HTTPException(status_code=404, detail="Expert not found")
    if expert.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Can only upload documents to your own profile")

    doc = Document(
        expert_id=document_create.expert_id,
        file_url=None,
        file_type=document_create.file_type,
        text=document_create.text,
        title=document_create.title or "Document Note",
        description=document_create.description,
        category=document_create.category or "portfolio",
        status="approved" if expert.is_verified else "pending",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    add_documents_to_expert(document_create.expert_id, [{"text": document_create.text, "file_type": document_create.file_type}])
    return doc


@router.post("/upload-file", response_model=DocumentRead)
async def upload_file(
    expert_id: int = Form(...),
    title: str = Form(None),
    category: str = Form(None),
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    expert = db.get(Expert, expert_id)
    if not expert:
        raise HTTPException(status_code=404, detail="Expert not found")
    if expert.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Can only upload documents to your own profile")

    # File validation
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    text = content.decode('utf-8', errors='ignore')

    doc = Document(
        expert_id=expert_id,
        file_url=file.filename,
        file_type=file.content_type or "file",
        text=text,
        title=title or file.filename,
        category=category or "portfolio",
        status="approved" if expert.is_verified else "pending",
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
    if expert.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Can only delete your own documents")

    db.delete(doc)
    db.commit()
    return {"status": "deleted", "document_id": document_id}


@router.post("/search")
def search_documents(request: DocumentSearchRequest, db: Session = Depends(get_db)):
    """
    Performs semantic vector search across all indexed expert documents using FAISS.
    """
    if not request.query.strip():
        return {"query": request.query, "results": []}

    matches = query_expert_documents(request.query, top_k=request.top_k)
    enriched_results = []
    for match in matches:
        metadata = match.get("metadata", {})
        expert_id = metadata.get("expert_id")
        expert = db.get(Expert, expert_id) if expert_id else None
        enriched_results.append({
            "text": metadata.get("text", "")[:400],
            "score": round(match.get("score", 0.0), 3),
            "expert_id": expert_id,
            "expert_name": expert.user.name if expert and expert.user else "Expert",
            "expert_title": expert.title if expert else None,
            "file_type": metadata.get("file_type", "document"),
        })

    return {
        "query": request.query,
        "total_results": len(enriched_results),
        "results": enriched_results,
    }


@router.post("/rag-chat")
def rag_chat(request: DocumentRAGRequest, db: Session = Depends(get_db)):
    """
    Document-Grounded RAG (Retrieval-Augmented Generation):
    Retrieves semantic excerpts from indexed expert documents and generates a response
    directly grounded in those source materials with transparent attribution.
    """
    matches = query_expert_documents(request.query, top_k=3)
    if not matches:
        return {
            "query": request.query,
            "grounded": False,
            "answer": "No relevant indexed documents were found matching your inquiry. Consider chatting with the general AI agent or browsing our expert directory.",
            "sources": [],
        }

    context_passages = []
    sources = []
    for idx, match in enumerate(matches):
        metadata = match.get("metadata", {})
        expert_id = metadata.get("expert_id")
        expert = db.get(Expert, expert_id) if expert_id else None
        excerpt = metadata.get("text", "")
        context_passages.append(f"[Document {idx+1}] (From {expert.title if expert else 'Expert'}):\n{excerpt}")
        sources.append({
            "expert_id": expert_id,
            "expert_title": expert.title if expert else "Expert",
            "excerpt": excerpt[:200] + "...",
        })

    combined_context = "\n\n".join(context_passages)

    prompt = f"""You are a specialized Document-Grounded AI Research Agent.
Answer the user's question using ONLY the provided verified document excerpts below.
If the documents do not provide enough information, state what is known from the text and note any limitations ethically.

Retrieved Document Excerpts:
{combined_context}

User Question:
"{request.query}"

Provide a clear, direct, and structured answer citing the specific documents where appropriate."""

    answer = llm_service.generate_text(prompt)
    if not answer or len(answer.strip()) < 30:
        answer = (
            f"**Document-Grounded Findings**:\n\n"
            f"Based on the retrieved expert documents for *\"{request.query}\"*:\n\n"
            + "\n".join([f"• {s['expert_title']}: {s['excerpt']}" for s in sources])
            + "\n\n*Note: This insight is synthesized directly from verified portfolio and strategy documents indexed in our vector store.*"
        )

    return {
        "query": request.query,
        "grounded": True,
        "answer": answer,
        "sources": sources,
    }
