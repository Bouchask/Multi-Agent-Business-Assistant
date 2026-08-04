import sys
from loguru import logger
from backend.app.config.settings import settings

def setup_logging():
    logger.remove()
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL.upper(),
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )
    logger.info(f"Initialized enterprise application logging with level: {settings.LOG_LEVEL}")
