import asyncio
import json
import urllib.error
import urllib.request

from src.domain.exceptions import CatalogUnavailableError

USER_AGENT = "estante-lab-engsoftware/1.0"


def _get(url: str, timeout: float) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


async def fetch_json(url: str, timeout: float = 8.0) -> dict:
    try:
        return await asyncio.to_thread(_get, url, timeout)
    except (
        urllib.error.URLError,
        TimeoutError,
        json.JSONDecodeError,
        OSError,
    ) as error:
        raise CatalogUnavailableError() from error
