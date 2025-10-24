import logging
import os
from logging.handlers import RotatingFileHandler

LOGGING_READY = False

LOG_FILE = os.path.join("DEBUG","algomancer.log")

def setup_logging(logger_name: str = "algomancer", output: bool = True) -> logging.Logger:
    """Configure root handlers once and return the requested logger."""
    global LOGGING_READY
    if not LOGGING_READY:
        os.makedirs("DEBUG",exist_ok=True)
        handlers = [
            RotatingFileHandler(
                LOG_FILE,
                mode="a",
                maxBytes=1_000_000, #around 1MB
                backupCount=5, #Creates 5 archives at max
                encoding="utf-8",
            )
        ]
        if output:
            handlers.append(logging.StreamHandler())
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s",
            handlers=handlers,
            force=True,
        )
        LOGGING_READY = True
    logger = logging.getLogger(logger_name)
    logger.info("=" * 60)
    logger.info("Run started for %s", logger_name)
    return logger
