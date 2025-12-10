import json
from pathlib import Path
from pypdf import PdfReader
from openai import AsyncOpenAI
import os
from typing import Dict, Any

class DocumentExtractionService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key != "your-openai-api-key-here":
            self.client = AsyncOpenAI(api_key=api_key)
        else:
            self.client = None
    
    async def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract raw text from PDF using pypdf"""
        try:
            pdf_path = Path(file_path)
            reader = PdfReader(pdf_path)
            
            text_content = ""
            for page in reader.pages:
                text_content += page.extract_text() + "\n"
            
            return text_content.strip()
        except Exception as e:
            raise Exception(f"PDF extraction failed: {str(e)}")
    
    async def analyze_document(self, text: str) -> Dict[str, Any]:
        """Use GPT to analyze and structure document data"""
        if not self.client:
            # Mock response for testing when API key is not configured
            return {
                "title": "Test Document",
                "document_date": "2025-12-10",
                "counterparty": "Test Party",
                "total_value": "Test Amount",
                "summary": "This is a test document for development purposes."
            }

        prompt = """
        Analyze this legal document and extract the following information as JSON:
        - title: A concise title for the document
        - document_date: The date of the document (YYYY-MM-DD format if possible)
        - counterparty: The other party/parties involved
        - total_value: Any monetary amounts mentioned (as a string)
        - summary: A brief 2-3 sentence summary of the document's purpose

        Return only valid JSON with these exact keys.
        """

        try:
            response = await self.client.chat.completions.create(
                # model="gpt-5-mini",
                model="gpt-5-nano",
                messages=[
                    {"role": "system", "content": "You are a legal document analysis assistant. Always return valid JSON."},
                    {"role": "user", "content": f"Document text:\n\n{text[:4000]}"}  # Limit text length
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )

            result = response.choices[0].message.content
            return json.loads(result)

        except Exception as e:
            raise Exception(f"LLM analysis failed: {str(e)}")
    
    async def process_document(self, file_path: str) -> Dict[str, Any]:
        """Complete document processing pipeline"""
        # Extract text
        text = await self.extract_text_from_pdf(file_path)
        
        # Analyze with LLM
        analysis = await self.analyze_document(text)
        
        return analysis