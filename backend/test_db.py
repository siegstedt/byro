import asyncio
from sqlalchemy import text
from app.core.database import async_session
from app.models import InboxItem, Matter, Document

async def test_database():
    async with async_session() as session:
        # Test basic query
        result = await session.execute(text("SELECT version()"))
        print("✅ Database connected:", result.scalar())

        # Test table counts
        inbox_count = await session.execute(text("SELECT COUNT(*) FROM inbox_items"))
        matters_count = await session.execute(text("SELECT COUNT(*) FROM matters"))
        docs_count = await session.execute(text("SELECT COUNT(*) FROM documents"))

        print(f"📊 Tables created successfully:")
        print(f"   - inbox_items: {inbox_count.scalar()} records")
        print(f"   - matters: {matters_count.scalar()} records")
        print(f"   - documents: {docs_count.scalar()} records")

        # Test pgvector extension
        vector_result = await session.execute(text("SELECT '[1,2,3]'::vector(3) as test_vector"))
        print(f"🧮 pgvector working: {vector_result.scalar()}")

if __name__ == "__main__":
    asyncio.run(test_database())