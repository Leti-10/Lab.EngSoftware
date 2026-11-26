import logging

import pytest

from src.infrastructure.telemetry import logger_decorator


@pytest.mark.asyncio
async def test_logger_decorator_awaits_operation_without_logging_payload(caplog):
    @logger_decorator
    async def save_user(password: str) -> str:
        return password

    with caplog.at_level(
        logging.INFO, logger="src.infrastructure.telemetry.log_decorator"
    ):
        result = await save_user("sensitive-password")

    assert result == "sensitive-password"
    assert "Starting persistence operation: " in caplog.text
    assert "Completed persistence operation: " in caplog.text
    assert "sensitive-password" not in caplog.text


@pytest.mark.asyncio
async def test_logger_decorator_logs_failure_and_reraises_without_payload(caplog):
    @logger_decorator
    async def save_user(password: str) -> None:
        raise ValueError(password)

    with caplog.at_level(
        logging.INFO, logger="src.infrastructure.telemetry.log_decorator"
    ):
        with pytest.raises(ValueError, match="sensitive-password"):
            await save_user("sensitive-password")

    assert "Persistence operation failed: " in caplog.text
    assert "sensitive-password" not in caplog.text
