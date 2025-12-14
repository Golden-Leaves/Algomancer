from __future__ import annotations

import numpy as np
from manim import DOWN, LEFT, RIGHT, UP
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Structures.base import VisualElement,VisualStructure


def get_offset_position(
    element: "VisualElement"|VisualStructure, coordinate=None, direction: np.ndarray = UP, buff: float = 1
):
    """
    Return a position offset relative to the given element, staying above/below/
    left/right by `buff`× its size.

    Parameters
    ----------
    element : VisualElement
        The element whose dimensions determine the offset scale.
    coordinate : np.ndarray | None, optional
        The base position to offset from. If None, defaults to the element's center.
        Must be a numeric 3D vector if provided.
    direction : str, optional
        One of {"up", "down", "left", "right"} indicating offset direction.
    buff : float, optional
        Fraction of the element's size to offset by.

    Returns
    -------
    np.ndarray
        A coordinate offset from the given base position.

    Notes
    -----
    - The offset *distance* is determined by the element's body size.
    - The offset *origin* is `coordinate` (defaults to element center).
    """
    vec = direction
    element_height = getattr(element,"body_height",element.height)
    element_width = getattr(element,"body_width",element.width)
    if direction is UP:
        base = element.get_top() if coordinate is None else np.array(coordinate)
        scale = element_height
    elif direction is DOWN:
        base = element.get_bottom() if coordinate is None else np.array(coordinate)
        scale = element_height
    elif direction is LEFT:
        base = element.get_left() if coordinate is None else np.array(coordinate)
        scale = element_width
    elif direction is RIGHT:
        base = element.get_right() if coordinate is None else np.array(coordinate)
        scale = element_width
    else:
        raise ValueError(f"Invalid direction: {direction}")

    
    return base + vec * scale * buff
