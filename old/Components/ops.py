from __future__ import annotations

import operator as op
from typing import Callable, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from Structures.base import VisualElement

_OPS = {
    # Arithmetic
    "+": op.add,
    "-": op.sub,
    "*": op.mul,
    "/": op.truediv,
    "//": op.floordiv,
    "%": op.mod,
    "**": op.pow,

    # Bitwise
    "&": op.and_,
    "|": op.or_,
    "^": op.xor,
    "~": op.invert,
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


def get_operation(op: str) -> Callable[..., Any]:
    """
    Retrieve a Python operator function based on its symbol.

    Parameters
    ----------
    symbol : str
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
    except KeyError as exc:
        raise ValueError(f"Unsupported operator: {op!r}") from exc


def resolve_value(obj):
    """
    Resolve an operand (VisualElement or primitive) into its comparable value.

    Supports:
        - VisualElement → obj.value
        - int, float, str, bool → obj
    Raises:
        TypeError for unsupported operand types.
    """
    from Structures.base import VisualElement  # lazy import to avoid circular dependency

    if isinstance(obj, VisualElement):
        return obj.value
    if isinstance(obj, (int, float, str, bool)):
        return obj
    return NotImplemented
