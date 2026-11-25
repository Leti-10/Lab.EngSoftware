from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.core.config import settings

async_engine = create_async_engine(
    url=settings.database_url,
    echo=True,
)

AsyncSessionLocal = async_sessionmaker(bind=async_engine, expire_on_commit=False)

async def get_db_context():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
