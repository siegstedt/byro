import os
import json
from pypdf import PdfReader
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)

class DocumentExtractionService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key != "your-openai-api-key-here":
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = None

    async def extract_text(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Failed to extract text from {file_path}: {str(e)}")
            raise

    async def analyze_with_llm(self, text: str) -> dict:
        """Analyze text with GPT-4o and return structured JSON"""
        try:
            system_prompt = """You are a legal AI. Extract the following fields from the document text:
- title: The document title or subject
- document_date: Date in YYYY-MM-DD format (extract from any date mentions) or null if none found
- counterparty: The other party involved or null if none found
- total_value: Numeric monetary amount (e.g., 50000.00) or null if none found
- summary: Brief summary of the document
- category: One of: invoice, contract, letter

Return only valid JSON with these fields. Use null for missing values, not placeholder text."""

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Document text:\n{text}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )

            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            logger.error(f"Failed to analyze text with LLM: {str(e)}")
            raise