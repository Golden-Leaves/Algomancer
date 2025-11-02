import logging
import os
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler

LOGGING_READY = False

LOG_FILE = os.path.join("DEBUG","algomancer.log")

def setup_logging(logger_name: str = "algomancer", output: bool = True) -> logging.Logger:
    """Configure root handlers once and return the requested logger."""
    global LOGGING_READY
    if not LOGGING_READY:
        current_directory = os.path.dirname(os.path.abspath(__file__))
        env_path = os.path.join(current_directory,"..",".env")
        print(env_path)
        load_dotenv(env_path)
        os.makedirs("DEBUG",exist_ok=True)
        logging_level = os.getenv("LOGGING_LEVEL").upper()
        level = getattr(logging,logging_level,logging.INFO)
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
            level=level,
            format="%(asctime)s %(levelname)s %(message)s",
            handlers=handlers,
            force=True,
        )

    logger = logging.getLogger(logger_name)
    if not LOGGING_READY:
        logger.info("Algomancer run initialized…")
        LOGGING_READY = True
    logger.info("=" * 60)
    logger.info("Run started for %s", logger_name)
    return logger
from __future__ import annotations

import logging
import os
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler

LOGGING_READY = False
LOG_FILE = os.path.join("DEBUG", "algomancer.log")


def setup_logging(logger_name: str = "algomancer", output: bool = True) -> logging.Logger:
    """Configure the shared logging handlers and return a namespaced logger."""
    global LOGGING_READY
    if not LOGGING_READY:
        current_directory = os.path.dirname(os.path.abspath(__file__))
        env_path = os.path.join(current_directory, "..", ".env")
        load_dotenv(env_path)
        os.makedirs("DEBUG", exist_ok=True)
        logging_level = (os.getenv("LOGGING_LEVEL") or "INFO").upper()
        level = getattr(logging, logging_level, logging.INFO)
        handlers = [
            RotatingFileHandler(
                LOG_FILE,
                mode="a",
                maxBytes=1_000_000,
                backupCount=5,
                encoding="utf-8",
            )
        ]
        if output:
            handlers.append(logging.StreamHandler())
        logging.basicConfig(
            level=level,
            format="%(asctime)s %(levelname)s %(message)s",
            handlers=handlers,
            force=True,
        )

    logger = logging.getLogger(logger_name)
    if not LOGGING_READY:
        logger.info("Algomancer run initialized…")
        LOGGING_READY = True
    logger.info("=" * 60)
    logger.info("Run started for %s", logger_name)
    return logger
