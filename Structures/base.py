from manim import *
import numpy as np
from Utils.utils import LazyAnimation,flatten_array,Event,resolve_value
from typing import Any
import weakref
class VisualStructure(VGroup):
    def __init__(self, scene,label, **kwargs):
        super().__init__(**kwargs)
        self.scene = scene
        self.label = label if label else ""
        self._trace = []
    # def __hash__(self): #Python removes this when you override comparasions(__eq__,..) for whatever reason
    #     return id(self)
    
 
 
    def play(self, *anims, **kwargs):
            """Recursive play: handles single or multiple animations\n
            Can accept either an array or multiple animations
            """
    
            
            if not self.scene:
                raise RuntimeError("No Scene bound. Pass scene=... when creating VisualArray.")
            for anim in flatten_array(result=[],objs=anims):
                #Checks if it's a builder animation or just plain animation
                if anim:
                    anim = anim.build() if isinstance(anim,LazyAnimation) else anim
                    if not isinstance(anim,Animation):
                        raise TypeError(f"Unexpected {type(anim)} passed to play()")
                    self.scene.play(anim, **kwargs)
    def get_element(self, index: int):
        """Placeholder. Subclasses should override this."""
        raise NotImplementedError("Subclasses must implement get_element().")
    def log_event(self,_type: str,
        indices: list[int] | None = None,other: Any | None = None, value: Any|None = None,
        result: bool | None = None,comment: str | None = None):
        """Helper to record a new Event into this structure’s _trace."""
        
        event = Event(
            _type=_type,
            target={
        "id": id(self),
        "name": type(self).__name__,
        "label": getattr(self, "label", None)
    },
            indices=indices,
            other=other,
            value=value,
            result=result,
            comment=comment
        )
        self._trace.append(event)
    
class VisualElement(VGroup):
    r"""
    Base class for all visualized data structure elements in Algomancer.

    This class wraps a Manim ``VMobject`` (e.g., ``Rectangle``, ``RoundedRectangle``, etc.)
    and exposes its geometric and positional attributes through a standardized API.
    Subclasses like ``Cell`` or ``Node`` can inherit from ``VisualElement`` to gain
    consistent access to commonly used properties such as ``width``, ``height``,
    ``top``, ``bottom``, and so on.

    Parameters
    ----------
    body : VMobject
        The Manim shape representing the visual element (e.g., a rectangle for a cell,
        or a rounded rectangle for a node).

    Notes
    -----
    - This class is designed to unify geometry handling across all visualized structures
      (arrays, linked lists, trees, hash tables, etc.).
    - Subclasses should initialize their own ``body`` and pass it to ``super().__init__(body)``.
    - The body is automatically added to the group hierarchy, so additional graphical
      elements (e.g., text labels) can be added directly with ``self.add(...)``.

    Example
    -------
    >>> rect = Rectangle(width=1, height=0.5)
    >>> elem = VisualElement(rect)
    >>> elem.body_width
    1.0
    >>> elem.top
    array([0. , 0.25, 0. ])
    """
    def __init__(self, body: VMobject,master:VisualStructure,value:any,**kwargs):
        super().__init__(**kwargs)
        self.body = body
        #Since master has references to elements, and the elements store a reference to the master
        #Python's pickle() will explode as it tries to recursively traverse through attributes...
        self._master_ref = weakref.ref(master) if master else None 
        self.value = value
        self.add(body)
    @property
    def master(self):
        """Return the dereferenced master object, or None if dead."""
        return self._master_ref() if self._master_ref else None
    @master.setter
    def master(self, new_master):
        """Rebind or clear the master reference."""
        if new_master is None:
            self._master_ref = None
        else:
            self._master_ref = weakref.ref(new_master)
    
    def __hash__(self):
        return id(self)


    
    def _compare(self, other, op: str):
        """Internal unified comparison handler."""
        
        if isinstance(other, VisualElement):
            if op == "==":
                result = self.value == other.value
            elif op == "!=":
                result = self.value != other.value
            elif op == "<":
                result = self.value < other.value
            elif op == "<=":
                result = self.value <= other.value
            elif op == ">":
                result = self.value > other.value
            elif op == ">=":
                result = self.value >= other.value
            else:
                raise ValueError(f"Unsupported comparison operator: {op}")

            # Log and visualize
            self.master.log_event(_type="compare", other=other, result=result)
            if self.master.scene:
                self.master.play(self.master.compare(self, other, result=result))
            return result

        elif isinstance(other, (int, float, str, bool)):
            if op == "==":
                return self.value == other
            elif op == "!=":
                return self.value != other
            elif op == "<":
                return self.value < other
            elif op == "<=":
                return self.value <= other
            elif op == ">":
                return self.value > other
            elif op == ">=":
                return self.value >= other
            else:
                raise ValueError(f"Unsupported comparison operator: {op}")

        return NotImplemented
    def __eq__(self, other):
        return self._compare(other=other, op="==")
    def __ne__(self, other):
        return self._compare(other=other, op="!=")

    def __lt__(self, other):
        print("Entering __lt__")
        return self._compare(other=other, op="<")

    def __le__(self, other):
        return self._compare(other=other, op="<=")

    def __gt__(self, other):
        return self._compare(other=other, op=">")

    def __ge__(self, other):
        return self._compare(other=other, op=">=")
    
    def _arith(self, other, op):
        ARITHMETIC_COLOR_MAP = {
            "+": BLUE_C,
            "-": GOLD_E,
            "*": PURPLE_A,
            "/": ORANGE,
        }
        SCALE_MAP = {
        "+": 1.2,
        "*": 1.3,
        "-": 0.85,
        "/": 0.8,
    }
        if not isinstance(other,VisualElement):
            result = eval(f"self.value {op} other")
        else:
            result = eval(f"self.value {op} other.value")
        color = ARITHMETIC_COLOR_MAP[op]
        anim = AnimationGroup(
            self.master.highlight(self,color=color, runtime=0.1),
            Indicate(self, color=color, scale_factor=SCALE_MAP[op]),
            self.master.unhighlight(self,runtime=0.15)
        )
        self.master.log_event(_type=f"arithmetic-{op}", result=result)
        if self.master.scene:
            self.master.play(anim)
        return result
    def __add__(self, other):
        return self._arith(other=other,op="+")
    def __sub__(self, other):
        return self._arith(other=other,op="-")
    def __mul__(self, other):
        return self._arith(other=other,op="*")
    def __truediv__(self, other):
        return self._arith(other=other,op="/")
    def __iadd__(self, other):
        result = self._arith(other=other, op="+")
        self.value = result  # update this object’s internal value
        return self          # must return self for in-place ops

    def __isub__(self, other):
        result = self._arith(other=other, op="-")
        self.value = result
        return self

    def __imul__(self, other):
        result = self._arith(other=other, op="*")
        self.value = result
        return self

    def __itruediv__(self, other):
        result = self._arith(other=other, op="/")
        self.value = result
        return self
        
    # --- Dimensions ---
    @property
    def body_width(self):
        return self.body.width

    @property
    def body_height(self):
        return self.body.height

    # --- Positioning ---
    @property
    def center(self):
        return self.body.get_center()

    @property
    def top(self):
        return self.body.get_top()

    @property
    def bottom(self):
        return self.body.get_bottom()

    @property
    def left(self):
        return self.body.get_left()

    @property
    def right(self):
        return self.body.get_right()

    # --- Extra geometric points if needed ---
    @property
    def corners(self):
        return self.body.get_vertices()

    @property
    def bounding_box(self):
        return self.body.get_bounding_box()

    # --- Allow direct shift/scale/rotate if you want ---
    def shift(self, *args, **kwargs):
        return self.body.shift(*args, **kwargs)

    def scale(self, *args, **kwargs):
        return self.body.scale(*args, **kwargs)

    def rotate(self, *args, **kwargs):
        return self.body.rotate(*args, **kwargs)