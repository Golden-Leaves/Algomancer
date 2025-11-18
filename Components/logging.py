import logging
import os
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler
from typing import Any, TYPE_CHECKING
from pprint import pformat
if TYPE_CHECKING:
    from Structures.base import VisualElement,VisualStructure
LOGGING_READY = False
LOG_FILE = os.path.join("DEBUG","algomancer.log")

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

    Key methods
    -----------
    - log_stucture_state(structure, label="state", level="debug")
      Logs high-level info for a structure and, if provided, its elements.
    - log_element_state(element, label="state", level="debug", depth=2)
      Logs a detailed snapshot of a single visual element.
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
        
    def log_stucture_state(
        self,
        structure: "VisualStructure",
        label: str = "state",
        elements: list["VisualElement"] | None = None,
        level: str = "debug",
    ) -> None:
        """Log structure state and optionally its elements' state.
        """
        from Components.helpers import flatten_array
        from Structures.base import VisualElement
        import numpy as np

        logger = getattr(self, "logger", None)
        if logger is None:
            return
        log_fn = getattr(logger, level.lower(), None) or logger.debug

        struct_payload = {
            "label": label,
            "type": type(structure).__name__,
            "id": hex(id(structure)),
            "pos": (
                np.array2string(structure.get_center(), precision=3)
                if hasattr(structure, "get_center")
                else None
            ),
            "z_index": getattr(structure, "z_index", None),
            "submobjects": [type(sm).__name__ for sm in getattr(structure, "submobjects", [])],
            "element_count": len(getattr(structure, "elements", [])),
        }
        # Pretty print to put attributes on separate lines with indent
        log_fn("structure.state %s\n%s", label, pformat(struct_payload, indent=2, width=120))

        targets:list[VisualElement] = elements if elements is not None else getattr(structure, "elements", [])
        for idx, element in enumerate(flatten_array(result=[], objs=targets)):
            if isinstance(element, VisualElement):
                if getattr(element, "master", None) is None:
                   self.warning("Element %s  has no master bound; cannot log state.",element)
                   continue
                self.log_element_state(element, label=f"{label}.element[{idx}]", level=level)
                
    def log_element_state(
        self,
        element: "VisualElement",
        *,
        label: str = "state",
        level: str = "debug",
        depth: int = 2,
    ) -> None:
        """Emit a snapshot of a single element's visual state.

        Uses the element's own `master` reference for index lookup.
        Errors out if the element has no master bound.
        """
        from Structures.base import VisualElement
        from Components.snapshot import get_mobject_state

        master = getattr(element, "master", None)
        if master is None:
            raise ValueError("Element has no master bound; cannot log state.")
        logger: logging.Logger = getattr(master, "logger", None)
        if logger is None:
            return
        log_fn = getattr(logger, level.lower(), None) or logger.debug

        index = None
        elements = getattr(master, "elements", None)
        if elements:
            for idx, el in enumerate(elements):
                if el is element:
                    index = idx
                    break

        body = getattr(element, "body", None)
        text = getattr(element, "text", None)

        payload = {
            "label": label,
            "index": index,
            "value": getattr(element, "value", None),
            "z_index": getattr(element, "z_index", None),
            "opacity": getattr(element, "opacity", None),
            "submobjects": [type(sm).__name__ for sm in element.submobjects],
            "body": get_mobject_state(body, depth=depth),
            "text": get_mobject_state(text, depth=depth) if text is not None else {},
        }
        log_fn("element.state %s\n%s", label, pformat(payload, indent=2, width=120))
        
