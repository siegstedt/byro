import pytest
from io import BytesIO
from unittest.mock import patch, AsyncMock
from app.models.inbox import InboxItem
from app.models.matters import Matter
from app.models.documents import Document

@pytest.mark.asyncio
async def test_full_processing_workflow(client, db_session):
    """Test complete workflow: upload → processing → review → commit to matter"""
    # Step 1: Upload file
    file_content = b"Sample contract content for testing"
    files = {"file": ("contract.pdf", BytesIO(file_content), "application/pdf")}

    response = await client.post("/inbox/upload", files=files)
    assert response.status_code == 200
    upload_data = response.json()
    inbox_item_id = upload_data["id"]

    # Verify item created with processing status
    item = await db_session.get(InboxItem, inbox_item_id)
    assert item.status == "processing"

    # Step 2: Simulate background processing (mock AI extraction)
    with patch('app.services.extraction.DocumentExtractionService.analyze_with_llm') as mock_analyze:
        mock_analyze.return_value = {
            "title": "Sample Contract",
            "category": "contract",
            "document_date": "2024-01-15",
            "parties": ["Party A", "Party B"],
            "amount": 50000.0
        }

        # Trigger processing (in real app this would be background task)
        from app.services.extraction import DocumentExtractionService
        service = DocumentExtractionService()

        # Mock file path exists
        item.file_path = "byro_data/uploads/test.pdf"
        await db_session.commit()

        # Process the item
        from app.api.endpoints.inbox import process_inbox_item
        await process_inbox_item(str(item.id), item.file_path)

        # Refresh item
        await db_session.refresh(item)
        assert item.status == "review"
        assert item.ai_payload is not None
        assert item.ai_payload["title"] == "Sample Contract"

    # Step 3: Get inbox item for review
    response = await client.get(f"/inbox/{inbox_item_id}")
    assert response.status_code == 200
    review_data = response.json()
    assert review_data["status"] == "review"
    assert "ai_payload" in review_data

    # Step 4: Commit to matter
    matter_data = {
        "title": "Sample Contract Matter",
        "category": "contract",
        "attributes": {
            "document_date": "2024-01-15",
            "parties": ["Party A", "Party B"],
            "amount": 50000.0
        },
        "inbox_item_id": inbox_item_id
    }

    response = await client.post("/matters", json=matter_data)
    assert response.status_code == 200
    matter_response = response.json()

    # Verify matter created
    matter = await db_session.get(Matter, matter_response["id"])
    assert matter.title == "Sample Contract Matter"
    assert matter.category == "contract"

    # Verify document attached
    documents = await db_session.execute(
        f"SELECT * FROM documents WHERE matter_id = '{matter.id}'"
    )
    docs = documents.fetchall()
    assert len(docs) == 1

    # Verify inbox item status updated
    await db_session.refresh(item)
    assert item.status == "committed"

@pytest.mark.asyncio
async def test_processing_error_handling(client, db_session):
    """Test error handling in processing workflow"""
    # Upload file
    files = {"file": ("error.pdf", BytesIO(b"content"), "application/pdf")}
    response = await client.post("/inbox/upload", files=files)
    assert response.status_code == 200
    upload_data = response.json()
    inbox_item_id = upload_data["id"]

    # Simulate processing error
    with patch('app.services.extraction.DocumentExtractionService.analyze_with_llm') as mock_analyze:
        mock_analyze.side_effect = Exception("AI processing failed")

        from app.services.extraction import DocumentExtractionService
        service = DocumentExtractionService()

        item = await db_session.get(InboxItem, inbox_item_id)
        item.file_path = "byro_data/uploads/error.pdf"
        await db_session.commit()

        # Process should handle error gracefully
        from app.api.endpoints.inbox import process_inbox_item
        await process_inbox_item(str(item.id), item.file_path)

        # Refresh and check status
        await db_session.refresh(item)
        assert item.status == "error"
        assert item.error_message is not None

@pytest.mark.asyncio
async def test_attach_existing_document_to_matter(client, db_session):
    """Test attaching already processed document to existing matter"""
    # Create existing matter
    matter = Matter(title="Existing Matter", category="contract")
    db_session.add(matter)
    await db_session.commit()
    await db_session.refresh(matter)

    # Create processed inbox item
    inbox_item = InboxItem(
        original_filename="existing.pdf",
        file_path="byro_data/uploads/existing.pdf",
        status="review",
        ai_payload={"title": "Existing Document", "category": "contract"}
    )
    db_session.add(inbox_item)
    await db_session.commit()
    await db_session.refresh(inbox_item)

    # Attach to existing matter
    response = await client.post(
        f"/matters/{matter.id}/documents",
        json={"inbox_item_id": str(inbox_item.id)}
    )
    assert response.status_code == 200

    # Verify document attached
    documents = await db_session.execute(
        f"SELECT * FROM documents WHERE matter_id = '{matter.id}'"
    )
    docs = documents.fetchall()
    assert len(docs) == 1

    # Verify inbox item committed
    await db_session.refresh(inbox_item)
    assert inbox_item.status == "committed"