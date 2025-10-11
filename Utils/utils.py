from __future__ import annotations
from typing import TYPE_CHECKING
from manim import *
import numpy as np
from typing import Any
if TYPE_CHECKING:
    from Structures.base import VisualElement

class LazyAnimation:
    
    """Wrapper for a function that builds an Animation lazily.
    This is used to allow multiple animations to be passed to play(), since this prevents them from being evaluated
    set_value() for example shouldn't get evaluated before the array gets created lol
    """
    def __init__(self, builder):
        self.builder = builder
   
    def build(self) -> Animation:
        anim = self.builder()
        return anim
    
def resolve_value(obj):
    """
    Resolve an operand (VisualElement or primitive) into its comparable value.

    Supports:
        - VisualElement → obj.value
        - int, float, str, bool → obj
    Raises:
        TypeError for unsupported operand types.
    """
    from Structures.base import VisualElement
    if isinstance(obj, (VisualElement)):
        return obj.value
    elif isinstance(obj, (int, float, str, bool)):
        return obj
    else:
        # raise TypeError(f"Unsupported operand type: {type(obj).__name__}")
        return NotImplemented
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

class Event:
    def __init__(self,_type:str,target:object,
    indices:list[int]|None=None,other:Any|None=None,value:Any|None=None,step_id:int|None=None,result:bool|None=None,comment:str|None=None):
        self._type = _type
        self.target = target
        self.indices = indices
        self.other = other
        self.value = value
        self.step_id = step_id
        self.result = result
        self.comment = comment
    def __repr__(self):
        return f"<Event type={self._type} target={type(self.target).__name__}>"
        