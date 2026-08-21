from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.settings import Settings

settings = Settings()
async_engine = create_async_engine(settings.DATABASE_URL)

AsyncSessionLocal = async_sessionmaker( bind=async_engine, class_=AsyncSession, expire_on_commit=False)

async def get_session():
    async with AsyncSessionLocal() as session:
        yield session