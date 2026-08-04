import sys
from loguru import logger

def setup_os_logger():
    """Configures production-ready structured logging for AI Executive Operating System."""
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True
    )
    logger.info("🛡️ AI Executive OS Logging Architecture Configured.")
