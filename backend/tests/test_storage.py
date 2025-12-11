import pytest
import tempfile
from pathlib import Path
from io import BytesIO
from fastapi import UploadFile
from app.services.storage import LocalStorage

@pytest.fixture
def temp_storage():
    """Create temporary storage for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage = LocalStorage(base_path=temp_dir)
        yield storage

@pytest.mark.asyncio
async def test_save_file_creates_directory(temp_storage):
    """Test that save_file creates base directory if it doesn't exist"""
    # Directory should be created in __init__
    assert temp_storage.base_path.exists()
    assert temp_storage.base_path.is_dir()

@pytest.mark.asyncio
async def test_save_file_saves_content(temp_storage):
    """Test that save_file saves file content correctly"""
    # Create test file content
    test_content = b"Hello, World!"
    file_obj = BytesIO(test_content)
    upload_file = UploadFile(filename="test.txt", file=file_obj)

    # Save file
    relative_path = await temp_storage.save_file(upload_file)

    # Check file was saved
    full_path = temp_storage.base_path / Path(relative_path).name
    assert full_path.exists()
    assert full_path.is_file()

    # Check content
    with open(full_path, "rb") as f:
        saved_content = f.read()
    assert saved_content == test_content

@pytest.mark.asyncio
async def test_save_file_returns_relative_path(temp_storage):
    """Test that save_file returns correct relative path"""
    file_obj = BytesIO(b"test")
    upload_file = UploadFile(filename="test.pdf", file=file_obj)

    relative_path = await temp_storage.save_file(upload_file)

    # Should start with the expected prefix
    assert relative_path.startswith("byro_data/uploads/")
    # Should end with .pdf
    assert relative_path.endswith(".pdf")

@pytest.mark.asyncio
async def test_save_file_generates_unique_filename(temp_storage):
    """Test that save_file generates unique filenames"""
    file_obj1 = BytesIO(b"content1")
    upload_file1 = UploadFile(filename="test.txt", file=file_obj1)

    file_obj2 = BytesIO(b"content2")
    upload_file2 = UploadFile(filename="test.txt", file=file_obj2)

    path1 = await temp_storage.save_file(upload_file1)
    path2 = await temp_storage.save_file(upload_file2)

    # Paths should be different
    assert path1 != path2

    # Both files should exist
    full_path1 = temp_storage.base_path / Path(path1).name
    full_path2 = temp_storage.base_path / Path(path2).name
    assert full_path1.exists()
    assert full_path2.exists()

@pytest.mark.asyncio
async def test_save_file_preserves_extension(temp_storage):
    """Test that save_file preserves file extension"""
    test_cases = [
        ("document.pdf", ".pdf"),
        ("image.png", ".png"),
        ("file.txt", ".txt"),
        ("no_extension", "")  # No extension case
    ]

    for filename, expected_ext in test_cases:
        file_obj = BytesIO(b"test")
        upload_file = UploadFile(filename=filename, file=file_obj)

        relative_path = await temp_storage.save_file(upload_file)

        if expected_ext:
            assert relative_path.endswith(expected_ext)
        else:
            # For files without extension, should still have a UUID
            assert len(Path(relative_path).stem) == 36  # UUID length