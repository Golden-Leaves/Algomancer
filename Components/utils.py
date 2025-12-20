from __future__ import annotations
from typing import Callable, Any
import operator as op
def rgba(r, g, b, a=255):
    return (r/255, g/255, b/255, a/255)
def normalize_color(c):
    #Hexadecimal
    """
    Normalize a color to a tuple of four float values between 0 and 1.

    The color can be provided as a string representing a hexadecimal color code,
    a tuple or list of three or four float values between 0 and 1 or
    a single integer representing the grayscale value of the color.

    Args:
        c: str, tuple or list. The color to be normalized.

    Returns:
        tuple: A tuple of four float values representing the normalized color.

    Raises:
        ValueError: If the provided color format is not supported.
    """
    if isinstance(c, str):
        c = c.lstrip("#")
        r = int(c[0:2], 16) / 255
        g = int(c[2:4], 16) / 255
        b = int(c[4:6], 16) / 255
        return (r, g, b, 1.0)

    #Tuple/list
    if len(c) == 3:
        return (*c, 1.0)
    if len(c) == 4:
        return tuple(c)

    raise ValueError("Unsupported color format")
_OPS: dict[str, Callable[..., Any]] = {
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
    "<": op.lt,
    "<=": op.le,
    ">": op.gt,
    ">=": op.ge,

    # Logical
    "and": lambda a, b: a and b,
    "or": lambda a, b: a or b,
    "not": lambda a: not a,
}


def get_operation(operation: str) -> Callable[..., Any]:
    
    """
    Retrieve a Python operator function based on its symbol.

    Parameters
    ----------
    operation : str
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
    """
    try:
        return _OPS[operation]
    except KeyError as exc:
        raise ValueError(f"Unsupported operator: {operation!r}") from exc
