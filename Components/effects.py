from __future__ import annotations

from manim import *
from typing import TYPE_CHECKING

from Components.logging import DebugLogger

if TYPE_CHECKING:
    from Structures.base import VisualElement


class EffectsManager:
    def __init__(self, scene=None, logger: DebugLogger | None = None):
        self.scene = scene
        self.logger = logger or DebugLogger(logger_name=f"{__name__}.EffectsManager")

    def highlight(self, element: "VisualElement", color=YELLOW, opacity=0.5, runtime=0.5) -> ApplyMethod:
        element_body = getattr(element, "body", element)
        if self.logger:
            element_name = getattr(element, "label", type(element).__name__)
            self.logger.info("highlight element=%s color=%s opacity=%s", element_name, color, opacity)
        return ApplyMethod(element_body.set_fill, color, opacity, run_time=runtime)

    def unhighlight(self, element: "VisualElement", runtime=0.5) -> ApplyMethod:
        element_body = getattr(element, "body", element)
        if self.logger:
            element_name = getattr(element, "label", type(element).__name__)
            self.logger.info("unhighlight element=%s opacity=%s", element_name, 0.5)
        return ApplyMethod(element_body.set_fill, BLACK, 0.5, run_time=runtime)

    def indicate(self, element: "VisualElement", color=YELLOW, scale_factor=1.1, runtime=0.5) -> Animation:
        """Return a pulse animation for the given element."""

        element_body = getattr(element, "body", element)
        if self.logger:
            element_name = getattr(element, "label", type(element).__name__)
            self.logger.info("indicate element=%s color=%s scale=%s", element_name, color, scale_factor)

        pulse = Indicate(element_body, color=color, scale_factor=scale_factor, run_time=runtime)

        finalize = Wait(0)
        _orig_finish = finalize.finish

        def _finish_restore():
            _orig_finish()
            self.unhighlight(element=element, runtime=0)

        finalize.finish = _finish_restore
        return Succession(pulse, finalize)

    def outline(self, element: "VisualElement", color=PURE_GREEN, width=6, runtime=0.5) -> ApplyMethod:
        element_body = getattr(element, "body", element)
        if self.logger:
            element_name = getattr(element, "label", type(element).__name__)
            self.logger.info("outline element=%s color=%s width=%s", element_name, color, width)
        return ApplyMethod(element_body.set_stroke, color, width, 1.0, run_time=runtime)

    def unoutline(self, element: "VisualElement", color=WHITE, width=4, runtime=0.5) -> ApplyMethod:
        element_body = getattr(element, "body", element)
        if self.logger:
            element_name = getattr(element, "label", type(element).__name__)
            self.logger.info("unoutline element=%s color=%s width=%s", element_name, color, width)
        return ApplyMethod(element_body.set_stroke, color, width, 1.0, run_time=runtime)
