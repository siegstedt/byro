import pytest
from app.models.matters import Matter
from app.models.documents import Document
from app.models.inbox import InboxItem

@pytest.mark.asyncio
async def test_get_matters_empty(client):
    """Test GET /matters returns empty list"""
    response = await client.get("/matters")
    assert response.status_code == 200
    data = response.json()
    assert data == []

@pytest.mark.asyncio
async def test_create_matter(client, db_session):
    """Test POST /matters creates new matter"""
    # Create test inbox item
    inbox_item = InboxItem(
        original_filename="test.pdf",
        file_path="test/path.pdf",
        status="review",
        ai_payload={"title": "Test Contract", "category": "contract"}
    )
    db_session.add(inbox_item)
    await db_session.commit()
    await db_session.refresh(inbox_item)

    matter_data = {
        "title": "Test Matter",
        "category": "contract",
        "attributes": {"date": "2025-01-01"},
        "inbox_item_id": str(inbox_item.id)
    }

    response = await client.post("/matters", json=matter_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Matter"
    assert data["category"] == "contract"

    # Check database
    matter = await db_session.get(Matter, data["id"])
    assert matter is not None
    assert matter.title == "Test Matter"

    # Check document created
    document = await db_session.execute(
        f"SELECT * FROM documents WHERE matter_id = '{data['id']}'"
    )
    docs = document.fetchall()
    assert len(docs) == 1

@pytest.mark.asyncio
async def test_attach_document_to_matter(client, db_session):
    """Test POST /matters/{id}/documents attaches document"""
    # Create test matter
    matter = Matter(title="Test Matter", category="contract")
    db_session.add(matter)
    await db_session.commit()
    await db_session.refresh(matter)

    # Create test inbox item
    inbox_item = InboxItem(
        original_filename="test.pdf",
        file_path="test/path.pdf",
        status="review"
    )
    db_session.add(inbox_item)
    await db_session.commit()
    await db_session.refresh(inbox_item)

    response = await client.post(
        f"/matters/{matter.id}/documents",
        json={"inbox_item_id": str(inbox_item.id)}
    )
    assert response.status_code == 200

    # Check document created
    document = await db_session.execute(
        f"SELECT * FROM documents WHERE matter_id = '{matter.id}'"
    )
    docs = document.fetchall()
    assert len(docs) == 1