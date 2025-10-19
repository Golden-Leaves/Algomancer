from __future__ import annotations
from manim import *
import numpy as np
from Utils.utils import LazyAnimation, flatten_array, Event, resolve_value, get_operation
from Utils.runtime import is_animating, AlgoScene, get_current_line_metadata
from typing import Any
import contextvars
import weakref

_COMPARE_GUARD = contextvars.ContextVar("_COMPARE_GUARD", default=False)
class VisualStructure(VGroup):
    """Base container for Algomancer data structures.

    A ``VisualStructure`` groups the elements belonging to a structure (array cells, list nodes,
    etc.)
    It centralises common behaviours such as logging events, dispatching animations via ``play``, and
    providing helper lookups (``get_element``, ``get_index``).

    Parameters
    ----------
    scene : AlgoScene
        Scene that owns the structure. Required to drive animations.
    label : str
        Human-readable label used in overlays and event logs.
    **kwargs :
        Additional positioning options that mirror Manim's ``VGroup`` constructor
        (e.g. ``pos`` or ``x``/``y``/``z`` coordinates).
    """
    def __init__(self, scene:AlgoScene,label:str, **kwargs):
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
        self._scene_ref = weakref.ref(scene) if scene else None
        self.label = label if label else ""
        self.elements:list[VisualElement] = []
        self._trace = []
        if scene is not None:
            scene.register_structure(self)
            
    # def __hash__(self): #Python removes this when you override comparasions(__eq__,..) for whatever reason
    #     return id(self)
    
 
 
    def play(self, *anims, **kwargs):
            """Recursive play: handles single or multiple animations\n
            Can accept either an array or multiple animations
            """
    
            
            scene = self.scene
            if not scene:
                raise RuntimeError("No Scene bound. Pass scene=... when creating VisualArray.")
            for anim in flatten_array(result=[],objs=anims):
                #Checks if it's a builder animation or just plain animation
                if anim:
                    anim = anim.build() if isinstance(anim,LazyAnimation) else anim
                    if not isinstance(anim,Animation):
                        raise TypeError(f"Unexpected {type(anim)} passed to play()")
                    scene.play(anim, **kwargs)
                    
    def get_element(self, cell_or_index:VisualElement|int) -> VisualElement:
        """Error handling opps, can also be used to retrieve an element with an index"""
        from Structures.pointers import Pointer
    # Case 1: int → lookup in self.elements
        
        if isinstance(cell_or_index, int):
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
                raise ValueError(
                    "Cell object does not belong to this VisualStructure."
                )
            return cell_or_index
        
        elif isinstance(cell_or_index, Pointer):
            cell_or_index:Pointer = cell_or_index.value
        # Case 3: goofy input
        else:
            raise TypeError(
                f"Expected int or Cell object, got {type(cell_or_index).__name__}."
            )       
    def get_index(self, element: VisualElement) -> int:
        """Returns the index of a visual element"""
        elements = getattr(element.master, "elements", None)
        if elements is None:
            raise AttributeError(f"{type(element.master).__name__} has no attribute 'elements'.")

        if isinstance(element, int):
            # Why would you wanna pass an index in here???
            if 0 <= element < len(elements):
                return element
            else:
                raise IndexError(f"Index {element} out of bounds for array of size {len(elements)}.")

        elif isinstance(element, VisualElement):
            # manual identity comparison to avoid triggering __eq__()
            for i, el in enumerate(elements):
                if el is element:
                    return i
            raise ValueError("Element does not belong to this VisualStructure.")
        else:
            raise TypeError(f"Expected int or VisualElement, got {type(element).__name__}")
        
    def log_event(
        self,
        _type: str,
        indices: list[int] | None = None,
        other: Any | None = None,
        value: Any | None = None,
        result: bool | None = None,
        comment: str | None = None,
    ):
        """Append a new :class:`Event` describing the current visual operation.

        Parameters
        ----------
        _type : str
            Category of the action (e.g. ``\"compare\"``, ``\"swap\"``).
        indices : list[int] | None, optional
            Index or indices touched by the operation.
        other : Any | None, optional
            Secondary operand (another element/pointer) involved in the action.
        value : Any | None, optional
            Payload value (assignment target, lookup result, etc.).
        result : bool | None, optional
            Outcome flag for comparisons or predicates.
        comment : str | None, optional
            Free-form annotation describing the step.
        """

        event = Event(
            _type=_type,
            target={
                "id": id(self),
                "name": type(self).__name__,
                "label": getattr(self, "label", None),
            },
            indices=indices,
            other=other,
            value=value,
            result=result,
            comment=comment,
            line_info=get_current_line_metadata(),
        )
        self._trace.append(event)
        scene = self.scene
        if scene is not None:
            scene._trace.append(event)

    def __getstate__(self):
        state = dict(self.__dict__)
        state["_scene_ref"] = None
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

    @property
    def scene(self):
        return self._scene_ref() if self._scene_ref else None

    @scene.setter
    def scene(self, new_scene):
        self._scene_ref = weakref.ref(new_scene) if new_scene else None
        
    def highlight(self, cell:int|VisualElement, color=YELLOW, opacity=0.5, runtime=0.5) -> ApplyMethod:
        cell_obj: VisualElement = self.get_element(cell)
        cell_index = self.get_index(cell_obj)
        self.log_event(
            _type="highlight",
            indices=[cell_index],
            value={"color": color, "opacity": opacity},
            comment=f"highlight cell[{cell_index}]",
        )
        return ApplyMethod(cell_obj.body.set_fill, color, opacity, run_time=runtime)

    def unhighlight(self, cell:int|VisualElement, runtime=0.5) -> ApplyMethod: 
        cell_obj: VisualElement = self.get_element(cell)
        cell_index = self.get_index(cell_obj)
        self.log_event(
            _type="unhighlight",
            indices=[cell_index],
            value={"color": BLACK, "opacity": 0.5},
            comment=f"clear highlight cell[{cell_index}]",
        )
        return ApplyMethod(cell_obj.body.set_fill, BLACK,0.5, run_time=runtime)
    
    def outline(self, cell:int|VisualElement, color=PURE_GREEN, width=6, runtime=0.5) -> ApplyMethod:
        cell_element: VisualElement = self.get_element(cell)
        cell_obj: Rectangle = cell_element.body
        cell_index = self.get_index(cell_element)
        self.log_event(
            _type="outline",
            indices=[cell_index],
            value={"color": color, "width": width},
            comment=f"outline cell[{cell_index}]",
        )
        return ApplyMethod(cell_obj.set_stroke, color, width, 1.0, run_time=runtime)

    def unoutline(self, cell:int|VisualElement, color=WHITE, width=4, runtime=0.5) -> ApplyMethod:
        cell_element: VisualElement = self.get_element(cell)
        cell_obj: Rectangle = cell_element.body
        cell_index = self.get_index(cell_element)
        self.log_event(
            _type="unoutline",
            indices=[cell_index],
            value={"color": color, "width": width},
            comment=f"clear outline cell[{cell_index}]",
        )
        return ApplyMethod(cell_obj.set_stroke, color, width, 1.0, run_time=runtime)
class VisualElement(VGroup):
    r"""Fundamental visual building-block managed by a :class:`VisualStructure`.

    ``VisualElement`` wraps a Manim ``VMobject`` (``Rectangle``, ``RoundedRectangle``,
    ``Dot``, etc.) and exposes geometry, metadata, and convenience APIs that all
    Algomancer elements share.  Subclasses (cells, nodes, pointers, …) inherit
    consistent access to positional helpers, value storage, and comparison/arith
    helpers used by the visual runtime.

    Parameters
    ----------
    body : VMobject, optional
        The underlying Manim object; will be added to the group automatically.
    master : VisualStructure | None
        Structure that owns this element
    value : Any, optional
        Logical value represented by the element (e.g. array cell contents,pointer's current index,.etc).
    label : str | None
        User-visible label rendered alongside the visual.
    **kwargs :
        Additional keyword arguments forwarded to ``VGroup``.

    Notes
    -----
    - ``master`` references are stored weakly so that scenes can garbage-collect
      without cycles.
    - ``body`` is appended to the group in ``__init__`` so additional adornments
      (text, highlight rings, etc.) can be added via ``self.add(...)``.
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

    def __getstate__(self): #Strips the master ref while deepcopying(opengl)
        state = dict(self.__dict__)
        state["_master_ref"] = None
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
    
    def __hash__(self):
        return id(self)


    
    def _compare(self, other, op: str):
        """Internal unified comparison handler."""
        if resolve_value(other) is NotImplemented:
            return NotImplemented
        if self is other:
            return True
        if _COMPARE_GUARD.get():
            return super().__eq__(other)
        token = _COMPARE_GUARD.set(True) #OpenGL does some goofy comparison shi in .compare(), this is here to circumvent that
        other_value = other.value if hasattr(other,"value") else other
        operation = get_operation(op=op)
        result = operation(self.value,other_value)
        # Log and visualize
        try:
            self.master.log_event(_type="compare", other=other, result=result)
            if self.master and self.master.scene and is_animating() and not self.master.scene.in_play:
                
                master_anim = self.master.compare(self, other, result=result)
                self.master.play(master_anim)
        except ValueError: #Manim's internals cooking
            return NotImplemented
        finally:
            _COMPARE_GUARD.reset(token)
        return result

    def __eq__(self, other): 
        comparison = self._compare(other=other, op="==")
        if comparison is NotImplemented:
            return super().__eq__(other)
        return comparison
    
    def __ne__(self, other):
        comparison = self._compare(other=other, op="!=")
        if comparison is NotImplemented:
            return super().__ne__(other)
        return comparison

    def __lt__(self, other):
        comparison = self._compare(other=other, op="<")
        if comparison is NotImplemented:
            return super().__lt__(other)
        return comparison

    def __le__(self, other):
        comparison = self._compare(other=other, op="<=")
        if comparison is NotImplemented:
            return super().__le__(other)
        return comparison

    def __gt__(self, other):
        comparison = self._compare(other=other, op=">")
        if comparison is NotImplemented:
            return super().__gt__(other)
        return comparison

    def __ge__(self, other):
        comparison = self._compare(other=other, op=">=")
        if comparison is NotImplemented:
            return super().__ge__(other)
        return comparison
    
    def _arith(self, other, op, other_on_left: bool = False):

        ARITHMETIC_COLOR_MAP = {
            "+": BLUE_C,
            "-": GOLD_E,
            "*": PURPLE_A,
            "/": ORANGE,
            "//": ORANGE,
            "%": TEAL_C,
        }
        SCALE_MAP = {
        "+": 1.2,
        "*": 1.3,
        "-": 0.85,
        "/": 0.8,
        "//": 0.8,
        "%": 0.9,
    }
      
        other_value = resolve_value(other)
        if other_value is NotImplemented:
            return NotImplemented
        
        left_value = other_value if other_on_left else self.value
        right_value = self.value if other_on_left else other_value
        operation = get_operation(op=op)
        result = operation(left_value,right_value)
        color = ARITHMETIC_COLOR_MAP[op]

        self.master.log_event(_type=f"arithmetic-{op}", result=result)

        if self.master.scene and is_animating() and not self.master.scene.in_play:
            anims = []
            master_anim = AnimationGroup(
            self.master.highlight(self,color=color, runtime=0.1),
            Indicate(self, color=color, scale_factor=SCALE_MAP[op]),
            # self.master.set_fill(opacity=0),
            self.master.unhighlight(self,runtime=0.15)
        )
            anims.append(master_anim)
            if isinstance(other,VisualElement) and getattr(other,"master",None) is not None : #Plays an animation if other is an element
                other_anim = AnimationGroup(
                other.master.highlight(self,color=color, runtime=0.1),
                Indicate(other, color=color, scale_factor=SCALE_MAP[op]),
                # self.master.set_fill(opacity=0),
                other.master.unhighlight(self,runtime=0.15))
                anims.append(other_anim)
            
            self.master.play(AnimationGroup(*anims))
        return result
    def __add__(self, other):
        return self._arith(other=other,op="+")
    def __sub__(self, other):
        return self._arith(other=other,op="-")
    def __mul__(self, other):
        return self._arith(other=other,op="*")
    def __truediv__(self, other):
        return self._arith(other=other,op="/")
    def __floordiv__(self,other):
        return self._arith(other=other,op="//")
    def __mod__(self,other):
        return self._arith(other=other,op="%")
    def __radd__(self, other):
        return self._arith(other=other, op="+", other_on_left=True)
    def __rsub__(self, other):
        return self._arith(other=other, op="-", other_on_left=True)
    def __rmul__(self, other):
        return self._arith(other=other, op="*", other_on_left=True)
    def __rtruediv__(self, other):
        return self._arith(other=other, op="/", other_on_left=True)
    def __rfloordiv__(self, other):
        return self._arith(other=other, op="//", other_on_left=True)
    def __rmod__(self, other):
        return self._arith(other=other, op="%", other_on_left=True)
    
    def __iadd__(self, other):
        result = self._arith(other=other, op="+")
        self.value = result  
        return self          

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
    
    def __ifloordiv__(self, other):
        result = self._arith(other=other, op="//")
        self.value = result
        return self
    
    def __imod__(self, other):
        result = self._arith(other=other, op="%")
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
        body = getattr(self, "body", None)
        if hasattr(body, "bounding_box"):
            return body.bounding_box
        if body is not None:
            return body.get_bounding_box()
        return getattr(self, "_bounding_box", None)

    @bounding_box.setter #OpenGL sets bounding_box on instantialization
    def bounding_box(self, value):
        body = getattr(self, "body", None)
        if hasattr(body, "bounding_box"):
            body.bounding_box = value
            return
        self._bounding_box = value #cache the value if nothing works

    # --- Allow direct shift/scale/rotate if you want ---
    def shift(self, *args, **kwargs):
        return self.body.shift(*args, **kwargs)

    def scale(self, *args, **kwargs):
        return self.body.scale(*args, **kwargs)

    def rotate(self, *args, **kwargs):
        return self.body.rotate(*args, **kwargs)
