from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.inbox import InboxItem
from app.services.storage import LocalStorage
from app.services.extraction import DocumentExtractionService
from app.schemas.inbox import InboxItemResponse
import logging

router = APIRouter()
storage = LocalStorage()
extraction_service = DocumentExtractionService()

logger = logging.getLogger(__name__)

@router.post("/upload", response_model=InboxItemResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload a file and create an inbox item for processing"""
    try:
        # Save file to storage
        file_path = await storage.save_file(file)
        
        # Create database entry
        inbox_item = InboxItem(
            original_filename=file.filename,
            file_path=file_path,
            status="processing"
        )
        
        db.add(inbox_item)
        await db.commit()
        await db.refresh(inbox_item)
        
        # Add background task for document processing
        background_tasks.add_task(
            process_inbox_item,
            inbox_item.id,
            file_path
        )
        
        return InboxItemResponse.from_orm(inbox_item)
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

async def process_inbox_item(item_id: str, file_path: str):
    """Background task to process uploaded document"""
    try:
        logger.info(f"Starting processing for item {item_id}")
        
        # Extract and analyze document
        analysis_result = await extraction_service.process_document(file_path)
        
        # Update database with results
        from app.core.database import async_session
        async with async_session() as session:
            inbox_item = await session.get(InboxItem, item_id)
            if inbox_item:
                inbox_item.ai_payload = analysis_result
                inbox_item.status = "review"
                await session.commit()
                logger.info(f"Successfully processed item {item_id}")
            else:
                logger.error(f"Inbox item {item_id} not found")
                
    except Exception as e:
        logger.error(f"Processing failed for item {item_id}: {str(e)}")
        # Update status to error in database
        try:
            from app.core.database import async_session
            async with async_session() as session:
                inbox_item = await session.get(InboxItem, item_id)
                if inbox_item:
                    inbox_item.status = "error"
                    inbox_item.ai_payload = {"error": str(e)}
                    await session.commit()
        except Exception as db_error:
            logger.error(f"Failed to update error status for item {item_id}: {str(db_error)}")