from __future__ import annotations
from typing import TYPE_CHECKING
from manim import *
import numpy as np
if TYPE_CHECKING:
    from Structures.base import VisualElement
    
class LazyAnimation:
    """Wrapper for a function that builds an Animation lazily.
    Anything that modifies self.cells will use this\n
    This is used to allow multiple animations to be passed to play(), since this prevents them from being evaluated
    """
    def __init__(self, builder):
        self.builder = builder
    def build(self) -> Animation:
        anim = self.builder()
        return anim
    
def flatten_array(result,objs) -> list:
    """Flattens an iterable"""
    if not isinstance(objs,(tuple,list)):
            result.append(objs)
            return 
    for obj in objs:
        flatten_array(result=result,objs=obj)
    return result
def get_offset_position(element:VisualElement, coordinate=None, direction:np.ndarray=UP, buff=1):
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

    if direction is UP:
        base = element.top if coordinate is None else np.array(coordinate)
        vec = direction
        scale = element.body_height
    elif direction is DOWN:
        base = element.bottom if coordinate is None else np.array(coordinate)
        vec = direction
        scale = element.body_height
    elif direction is LEFT:
        base = element.left if coordinate is None else np.array(coordinate)
        vec = direction
        scale = element.body_width
    elif direction is RIGHT:
        base = element.right if coordinate is None else np.array(coordinate)
        vec = RIGHT
        scale = element.body_width
    else:
        raise ValueError(f"Invalid direction: {direction}")

    
    return base + vec * scale * buff

   
