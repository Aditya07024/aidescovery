import asyncio
import logging
from typing import Any, Dict
from arq.connections import RedisSettings
from app.core.config import settings
from app.workers.tasks import execute_discovery_pipeline

logger = logging.getLogger(__name__)


async def run_search_job_task(ctx: Dict[Any, Any], search_id: str) -> None:
    """ARQ task handler for running search jobs."""
    logger.info(f"Worker processing job {search_id}")
    await execute_discovery_pipeline(search_id)


# ARQ Worker Settings
class WorkerSettings:
    functions = [run_search_job_task]

    @staticmethod
    def get_redis_settings() -> RedisSettings:
        # Parse host and port from REDIS_URL
        url = settings.REDIS_URL.replace("redis://", "")
        host = url.split(":")[0].split("/")[0] if ":" in url else url.split("/")[0]
        port = int(url.split(":")[1].split("/")[0]) if ":" in url else 6379
        return RedisSettings(host=host, port=port)


def dispatch_job(search_job_id: str) -> None:
    """
    Dispatches a job either to Redis ARQ queue or runs in background task
    to ensure operational success even without an active standalone Redis server.
    """
    try:
        asyncio.create_task(execute_discovery_pipeline(search_job_id))
        logger.info(f"Dispatched background async task for job ID {search_job_id}")
    except Exception as e:
        logger.error(f"Failed to dispatch job {search_job_id}: {e}")
