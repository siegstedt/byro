from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.matters import Matter
from app.models.documents import Document
from app.models.inbox import InboxItem
from app.schemas.matters import MatterCreate, MatterResponse

router = APIRouter()

@router.post("/", response_model=MatterResponse)
async def create_matter(
    matter_data: MatterCreate,
    inbox_item_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Create a new matter and archive the inbox item as a document"""
    # Get the inbox item
    inbox_item = await db.get(InboxItem, inbox_item_id)
    if not inbox_item:
        raise HTTPException(status_code=404, detail="Inbox item not found")

    # Create the matter
    matter = Matter(
        title=matter_data.title,
        category=matter_data.category,
        attributes=matter_data.attributes
    )
    db.add(matter)
    await db.commit()
    await db.refresh(matter)

    # Create document from inbox item
    document = Document(
        matter_id=matter.id,
        title=inbox_item.original_filename,
        content_text=str(inbox_item.ai_payload) if inbox_item.ai_payload else None
    )
    db.add(document)

    # Archive the inbox item
    inbox_item.status = "done"

    await db.commit()

    return MatterResponse.from_orm(matter)

@router.post("/{matter_id}/documents")
async def attach_document_to_matter(
    matter_id: str,
    inbox_item_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Attach an inbox item as a document to an existing matter"""
    # Get the matter
    matter = await db.get(Matter, matter_id)
    if not matter:
        raise HTTPException(status_code=404, detail="Matter not found")

    # Get the inbox item
    inbox_item = await db.get(InboxItem, inbox_item_id)
    if not inbox_item:
        raise HTTPException(status_code=404, detail="Inbox item not found")

    # Create document
    document = Document(
        matter_id=matter.id,
        title=inbox_item.original_filename,
        content_text=str(inbox_item.ai_payload) if inbox_item.ai_payload else None
    )
    db.add(document)

    # Archive the inbox item
    inbox_item.status = "done"

    await db.commit()

    return {"message": "Document attached successfully"}

@router.get("/", response_model=list[MatterResponse])
async def get_matters(db: AsyncSession = Depends(get_db)):
    """Get all matters"""
    result = await db.execute(
        select(Matter).order_by(Matter.created_at.desc())
    )
    matters = result.scalars().all()
    return [MatterResponse.from_orm(matter) for matter in matters]