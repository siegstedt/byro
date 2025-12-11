import pytest
from io import BytesIO
from app.models.inbox import InboxItem

@pytest.mark.asyncio
async def test_get_inbox_empty(client):
    """Test GET /inbox returns empty list when no items"""
    response = await client.get("/inbox")
    assert response.status_code == 200
    data = response.json()
    assert data == []

@pytest.mark.asyncio
async def test_get_inbox_item(client, db_session):
    """Test GET /inbox/{id} returns specific item"""
    # Create test item
    item = InboxItem(
        original_filename="test.pdf",
        file_path="test/path.pdf",
        status="processing"
    )
    db_session.add(item)
    await db_session.commit()
    await db_session.refresh(item)

    response = await client.get(f"/inbox/{item.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(item.id)
    assert data["original_filename"] == "test.pdf"

@pytest.mark.asyncio
async def test_upload_file(client, db_session):
    """Test POST /inbox/upload creates inbox item"""
    # Create test file
    file_content = b"test pdf content"
    files = {"file": ("test.pdf", BytesIO(file_content), "application/pdf")}

    response = await client.post("/inbox/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["original_filename"] == "test.pdf"
    assert data["status"] == "processing"

    # Check database
    item = await db_session.get(InboxItem, data["id"])
    assert item is not None
    assert item.status == "processing"