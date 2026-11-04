import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.domain.entities import Report
from src.domain.exceptions import ReportAlreadyExistsError
from src.infrastructure.persistence.models import ReportModelSQLAlchemy
from src.infrastructure.persistence.repositories import SQLAlchemyReportRepository


@pytest.mark.asyncio
async def test_report_repository_persists_and_filters_reports():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(ReportModelSQLAlchemy.__table__.create)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        repository = SQLAlchemyReportRepository(session)
        saved = await repository.save(
            Report(
                user_id=1,
                target_id=2,
                target_entity="user",
                description="Abuso no perfil",
            )
        )

        found = await repository.get_by_id(saved.id)
        filtered = await repository.find_by_filter(
            target_id=2, target_entity="user"
        )

    await engine.dispose()

    assert found == saved
    assert filtered == [saved]


@pytest.mark.asyncio
async def test_report_repository_rejects_duplicate_user_target():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(ReportModelSQLAlchemy.__table__.create)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        repository = SQLAlchemyReportRepository(session)
        report = Report(
            user_id=1,
            target_id=2,
            target_entity="user",
            description="Abuso no perfil",
        )
        await repository.save(report)

        with pytest.raises(ReportAlreadyExistsError):
            await repository.save(
                Report(
                    user_id=1,
                    target_id=2,
                    target_entity="user",
                    description="Outra denúncia sobre o mesmo perfil",
                )
            )

    await engine.dispose()
