from __future__ import annotations
from manim import *
import numpy as np
from Utils.utils import LazyAnimation,flatten_array,Event,resolve_value
from typing import Any
import weakref
from Utils.runtime import is_animating,AlgoScene
class VisualStructure(VGroup):
    def __init__(self, scene,label, **kwargs):
        super().__init__(**kwargs)
        self.pos = kwargs.pop("pos",None) #Center of the array
        if self.pos is not None:
            self.pos = np.array(self.pos)
        
        else:
            x = kwargs.get("x",None)
            y = kwargs.get("y",None)
            z = kwargs.get("z",None)
            if x is None and y is None and z is None:
                self.pos = ORIGIN
                x = x if x is not None else ORIGIN[0]
                y = y if y is not None else ORIGIN[1]
                z = z if z is not None else ORIGIN[2]
                self.pos = np.array([x,y,z])
        self.scene:AlgoScene = scene
        self.label = label if label else ""
        self.elements:list[VisualElement] = []
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
                    
    def get_element(self, cell_or_index:VisualElement|int):
        """Error handling opps, can also be used to retrieve an element with an index"""
        from Structures.pointer import Pointer
    # Case 1: int → lookup in self.elements
        print("Get Element:",cell_or_index,type(cell_or_index))
        
        if isinstance(cell_or_index, int):
            print("Accessed Index:", self.elements[cell_or_index])
            try:
                return self.elements[cell_or_index]
            except IndexError:
                raise IndexError(
                    f"Invalid index {cell_or_index}. "
                    f"Valid range is 0 to {len(self.elements) - 1}."
                )

        # Case 2: already a Cell 
        elif isinstance(cell_or_index, VisualElement):
            if not any(c is cell_or_index for c in self.elements): #This is used because 'in' calls __eq__ -> Inf Recursion
            # if not cell_or_index in self.elements: 
                raise ValueError(
                    "Cell object does not belong to this VisualStructure."
                )
            return cell_or_index
        elif isinstance(cell_or_index, Pointer):
            cell_or_index = cell_or_index.index
        # Case 3: goofy input
        else:
            raise TypeError(
                f"Expected int or Cell object, got {type(cell_or_index).__name__}."
            )       
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
    def highlight(self, cell:int|VisualElement, color=YELLOW, opacity=0.5, runtime=0.5) -> ApplyMethod:
        cell: VisualElement = self.get_element(cell).body  
        return ApplyMethod(cell.set_fill, color, opacity, run_time=runtime)

    def unhighlight(self, cell:int|VisualElement, runtime=0.5) -> ApplyMethod:
        cell: VisualElement = self.get_element(cell).body
        return ApplyMethod(cell.set_fill, BLACK,0, run_time=runtime)
    
    def outline(self, cell:int|VisualElement, color=PURE_GREEN, width=6, runtime=0.5) -> ApplyMethod:
        cell:Rectangle = self.get_element(cell).body
        return ApplyMethod(cell.set_stroke, color, width, 1.0, run_time=runtime)

    def unoutline(self, cell:int|VisualElement, color=WHITE, width=4, runtime=0.5) -> ApplyMethod:
        cell:Rectangle = self.get_element(cell).body
        return ApplyMethod(cell.set_stroke, color, width, 1.0, run_time=runtime)
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
    def __init__(self, body: VMobject=None,master:VisualStructure=None,value:any=None,label:str=None,**kwargs):
        super().__init__(**kwargs)
        self.body = body 
        #Since master has references to elements, and the elements store a reference to the master
        #Python's pickle() will explode as it tries to recursively traverse through attributes...
        self._master_ref = weakref.ref(master) if master else None 
        self.value = value
        self.label = label
        if body:
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

        if resolve_value(other) is NotImplemented:
            return None
        if self is other:
            return True
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
            if self.master.scene and is_animating() and self.master.scene.in_play:
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
    def __eq__(self, other): #TODO: Culprit
        comparison = self._compare(other=other, op="==")
        if comparison is NotImplemented:
            # If it's purely graphical, maybe just attach or combine
            return super().__eq__(other)
        return comparison
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
        from Structures.pointer import Pointer
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
        if not isinstance(other,Pointer):
            color = ARITHMETIC_COLOR_MAP[op]

            self.master.log_event(_type=f"arithmetic-{op}", result=result)
            print("Is animating?",is_animating())
            if self.master.scene and is_animating() and self.master.scene.in_play:
                anim = AnimationGroup(
                self.master.highlight(self,color=color, runtime=0.1),
                Indicate(self, color=color, scale_factor=SCALE_MAP[op]),
                self.master.unhighlight(self,runtime=0.15)
            )
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