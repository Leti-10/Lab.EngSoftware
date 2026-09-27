from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

async_engine = create_async_engine(
    url="sqlite+aiosqlite:///esperimento_x.db",
    echo=True,
)
AsyncSessionLocal = async_sessionmaker(bind=async_engine, expire_on_commit=False)


async def criar_tabelas(base):
    async with async_engine.begin() as conn:
        await conn.run_sync(base.metadata.create_all)


@asynccontextmanager
async def get_db_context():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
