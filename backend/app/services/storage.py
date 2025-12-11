import os
import uuid
from pathlib import Path
from fastapi import UploadFile

class LocalStorage:
    def __init__(self, base_path: str = None):
        if base_path is None:
            base_path = os.getenv("UPLOAD_DIR", "./byro_data/uploads")
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    async def save_file(self, file: UploadFile) -> str:
        """Save uploaded file and return the relative path"""
        # Generate unique filename
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = self.base_path / unique_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Return relative path for database storage
        return f"byro_data/uploads/{unique_filename}"