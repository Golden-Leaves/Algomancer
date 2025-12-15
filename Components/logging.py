import logging
import os
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler
from typing import Any, TYPE_CHECKING
from pprint import pformat
if TYPE_CHECKING:
    from Structures.base import VisualElement
LOGGING_READY = False
LOG_FILE = os.path.join("DEBUG","algomancer.log")
if not os.path.exists(os.path.dirname(LOG_FILE)):
    os.mkdir(os.path.dirname(LOG_FILE))
open(LOG_FILE,"a").close()
class DebugLogger:
    """
    Compose a standard Python logger with Algomancer-specific helpers.

    This wrapper configures logging on first use and exposes convenience
    passthroughs (debug/info/warning/error) plus structured state logging for
    visual structures and elements. Prefer using this over subclassing
    ``logging.Logger`` to avoid global side effects.

    Parameters
    ----------
    logger_name : str | None
        Namespace for the underlying logger (e.g., "Structures.arrays").
        Defaults to the module name of this wrapper when ``None``.
    output : bool
        When True, also attach a stream handler for console output.

    """
    def __init__(self, logger_name: str | None = None, output: bool = True) -> None:
        """Configure root handlers once and return the requested logger."""
        global LOGGING_READY
        if not LOGGING_READY:
            current_directory = os.path.dirname(os.path.abspath(__file__))
            env_path = os.path.join(current_directory,"..",".env")
            print(env_path)
            load_dotenv(env_path)
            logging_level = (os.getenv("LOGGING_LEVEL") or "INFO").upper()
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
                format="%(asctime)s %(levelname)s %(name)s %(message)s",
                handlers=handlers,
                force=True,
            )

        name = logger_name or __name__
        self.logger = logging.getLogger(name)
        if not LOGGING_READY:
            self.logger.info("Algomancer run initialized…")
            LOGGING_READY = True
        self.logger.info("=" * 60)
        self.logger.info("Run started for %s", name)
        
    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.logger.error(msg, *args, **kwargs)
        
