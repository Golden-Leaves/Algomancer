from __future__ import annotations

import operator as op
from typing import TYPE_CHECKING, Sequence

import numpy as np
from manim import Animation, ApplyMethod, DOWN, LEFT, RIGHT, UP
from typing import Any

if TYPE_CHECKING:
    from Structures.base import VisualElement
_OPS = {
    # Arithmetic
    "+":  op.add,
    "-":  op.sub,
    "*":  op.mul,
    "/":  op.truediv,
    "//": op.floordiv,
    "%":  op.mod,
    "**": op.pow,

    # Bitwise
    "&":  op.and_,
    "|":  op.or_,
    "^":  op.xor,
    "~":  op.invert,
    "<<": op.lshift,
    ">>": op.rshift,

    # Comparisons
    "==": op.eq,
    "!=": op.ne,
    "<":  op.lt,
    "<=": op.le,
    ">":  op.gt,
    ">=": op.ge,


    "and": lambda a, b: a and b,
    "or":  lambda a, b: a or b,
    "not": lambda a: not a,   
}
def get_operation(op: str) -> Callable:
    """
    Retrieve a Python operator function based on its symbol.

    Parameters
    ----------
    op : str
        The string representation of the operator
        (e.g. '+', '-', '*', '/', '==', 'and', etc.)

    Returns
    -------
    callable
        The corresponding function from the operator module
        or a logical lambda for 'and', 'or', 'not'.

    Raises
    ------
    ValueError
        If the operator symbol is not supported.

    Examples
    --------
    >>> add = get_operation('+')
    >>> add(2, 3)
    5
    """
    try:
        return _OPS[op]
    except KeyError:
        raise ValueError(f"Unsupported operator: {op!r}")
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

def hop_element(
    element: "VisualElement",
    *,
    lift: float = 0.5,
    runtime: float = 0.3,
) -> Animation:
    """Return a hop animation for a visual element."""
    start = element.center
    shift_vec = (element.top - start) / np.linalg.norm(element.top - start)
    hop_pos = start + shift_vec * (element.body_height + lift)
    return ApplyMethod(element.move_to, hop_pos, run_time=runtime)


def slide_element(
    element: "VisualElement",
    *,
    target_pos: Sequence[float] | np.ndarray,
    runtime: float = 0.5,
) -> Animation:
    """Return a slide animation while preserving vertical alignment."""
    current = element.center
    goal = np.asarray(target_pos, dtype=float)
    planar_goal = np.array([goal[0], current[1], current[2]])
    return ApplyMethod(element.move_to, planar_goal, run_time=runtime)

class Event:
    """Structured record of a single visualization action.

    Parameters
    ----------
    _type : str
        Category of the event (e.g. ``"compare"``, ``"swap"``).
    target : object
        Metadata describing the structure that emitted the event.
    indices : list[int] | None, optional
        Index or indices affected by the event.
    other : Any | None, optional
        Secondary operand (e.g. another cell/pointer) involved in the event.
    value : Any | None, optional
        Payload value (new assignment, lookup result, etc.).
    step_id : int | None, optional
        Optional sequential identifier when replaying events.
    result : bool | None, optional
        Outcome flag for comparisons or predicates.
    comment : str | None, optional
        Free-form human-readable annotation.
    line_info : tuple[str, int, str] | None, optional
        Source metadata captured by the tracer as ``(filename, lineno, func_name)``.
    """

    def __init__(self,_type:str,target:object,
    indices:list[int]|None=None,other:Any|None=None,value:Any|None=None,step_id:int|None=None,result:bool|None=None,comment:str|None=None,
    line_info:tuple[str,int,str]|None=None):
        self._type = _type
        self.target = target
        self.indices = indices
        self.other = other
        self.value = value
        self.step_id = step_id
        self.result = result
        self.comment = comment
        self.line_info = line_info
    def __repr__(self):
        return f"<Event type={self._type} target={type(self.target).__name__}>"
