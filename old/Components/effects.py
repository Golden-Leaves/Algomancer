from __future__ import annotations

from manim import *
from typing import TYPE_CHECKING

from Components.logging import DebugLogger
from Components.strategies import OpenGLStrategy,CairoStrategy
if TYPE_CHECKING:
    from numbers import Number
    from Structures.base import VisualElement,VisualStructure


class EffectsManager:
    """Factory for common, reusable visual effects.

    Centralizes small animations like highlight/pulse/outline so structures can
    keep a minimal API. Effects are renderer-aware via a simple strategy layer.
    """
    def __init__(self, logger: DebugLogger | None = None):

        self.logger = logger or DebugLogger(logger_name=f"{__name__}.EffectsManager")
        self.strategy = OpenGLStrategy() if config.renderer == RendererType.OPENGL else CairoStrategy()

    def highlight(self, element: "VisualElement", color=YELLOW, opacity=None, runtime=0.5) -> ApplyMethod:
        """Tint an element's fill to draw attention.

        Parameters
        - element: Visual element (or its body) to color.
        - color:   Fill color (default: YELLOW).
        - opacity: Fill opacity (defaults to renderer strategy value).
        - runtime: Duration in seconds.
        """
        element_body = getattr(element, "body", element)
        if opacity is None:
            opacity = self.strategy.get_fill_opacity()
        if self.logger:
            element_name = getattr(element, "label", type(element).__name__)
            self.logger.info("highlight element=%s color=%s opacity=%s", element_name, color, opacity)
        return ApplyMethod(element_body.set_fill, color, opacity, run_time=runtime)

    def unhighlight(self, element: "VisualElement", opacity=None, runtime=0.5) -> ApplyMethod:
        """Restore element fill back to base (black) with opacity.

        Parameters
        - element: Target element.
        - opacity: Fill opacity (defaults to renderer strategy value).
        - runtime: Duration in seconds.
        """
        element_body = getattr(element, "body", element)
        if opacity is None:
            opacity = self.strategy.get_fill_opacity()
        if self.logger:
            element_name = getattr(element, "label", type(element).__name__)
            self.logger.info("unhighlight element=%s opacity=%s", element_name, opacity)
        return ApplyMethod(element_body.set_fill, BLACK, opacity, run_time=runtime)
    

    def indicate(self, element: "VisualElement", color=YELLOW, scale_factor=1.1, runtime=0.8) -> Animation:
        """Pulse the element briefly (Manim Indicate)."""
        element_body = getattr(element, "body", element)
        if self.logger:
            element_name = getattr(element, "label", type(element).__name__)
            self.logger.info("indicate element=%s color=%s scale=%s", element_name, color, scale_factor)

        return Indicate(element_body, color=color, scale_factor=scale_factor, run_time=runtime)

    def outline(self, element: "VisualElement", color=PURE_GREEN, width=6, runtime=0.5) -> ApplyMethod:
        """Apply a colored stroke to outline the element."""
        element_body = getattr(element, "body", element)
        if self.logger:
            element_name = getattr(element, "label", type(element).__name__)
            self.logger.info("outline element=%s color=%s width=%s", element_name, color, width)
        return ApplyMethod(element_body.set_stroke, color, width, 1.0, run_time=runtime)

    def unoutline(self, element: "VisualElement", color=WHITE, width=4, runtime=0.5) -> ApplyMethod:
        """Revert outline to a neutral stroke."""
        element_body = getattr(element, "body", element)
        if self.logger:
            element_name = getattr(element, "label", type(element).__name__)
            self.logger.info("unoutline element=%s color=%s width=%s", element_name, color, width)
        return ApplyMethod(element_body.set_stroke, color, width, 1.0, run_time=runtime)
    
    def compare(self, element_1: VisualElement | Number, element_2: VisualElement | Number, result: bool = True) -> list[Animation]:
        """Build a simple visual compare sequence.

        Pulses the first operand, waits briefly, then pulses the second. Success
        uses green and a smaller scale; failure uses red and a slightly larger scale.

        Returns a list of Animation objects suitable for `scene.play(*anims)`.
        """
        from Structures.base import VisualElement
        color = GREEN if result else RED
        scale = 1.08 if result else 1.15
        
        element_name_1 = getattr(element_1, "label", type(element_1).__name__) if isinstance(element_1, VisualElement) else element_1
        element_name_2 = getattr(element_2, "label", type(element_2).__name__) if isinstance(element_2, VisualElement) else element_2
        if self.logger:
            self.logger.info("compare elements=%s,%s result=%s color=%s scale=%s", element_name_1, element_name_2, result, color, scale)
        
        animations = []
        if isinstance(element_1, VisualElement):
            animations.append(self.indicate(element=element_1, scale_factor=scale, color=color))
        animations.append(Wait(0.1))
        if isinstance(element_2, VisualElement):
            animations.append(self.indicate(element=element_2, scale_factor=scale, color=color))
        return animations
    #TODO: Substitute AnimationGroup with async maybe
