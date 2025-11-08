from __future__ import annotations
from manim import *
import numpy as np
from Components.events import Event
from Components.ops import get_operation, resolve_value
from Components.runtime import AlgoScene, get_current_line_metadata, is_animating
from Components.effects import EffectsManager
from typing import Any, TYPE_CHECKING
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
        self.pos = kwargs.pop("pos",None)
        if self.pos is not None:
            self.pos = np.array(self.pos)
        
        else:
            x = kwargs.get("x",None)
            y = kwargs.get("y",None)
            z = kwargs.get("z",None)
            if x is None and y is None and z is None: #Fills in missing axis values if not provided
                self.pos = ORIGIN
                x = x if x is not None else ORIGIN[0]
                y = y if y is not None else ORIGIN[1]
                z = z if z is not None else ORIGIN[2]
                self.pos = np.array([x,y,z])
        self._scene_ref = weakref.ref(scene) if scene else None
        self.label = label if label else ""
        self.elements: list[VisualElement] = []
        self._trace = []
        logger = getattr(self, "logger", None)
        self.effects = EffectsManager(logger=logger)
        if scene is not None:
            scene.register_structure(self)
    
    def add(self, *mobjects):
        """Ensure Manim duplicate checks use identity, not value-based equality."""
        token = _COMPARE_GUARD.set(True)
        try:
            return super().add(*mobjects)
        finally:
            _COMPARE_GUARD.reset(token)

    def remove(self, *mobjects):
        """Mirror add-guarding when removing so equality hooks stay inert."""
        token = _COMPARE_GUARD.set(True)
        try:
            return super().remove(*mobjects)
        finally:
            _COMPARE_GUARD.reset(token)
    
    def __len__(self):
        return len(self.elements)

    def highlight(self, element: "VisualElement|int", *, color: ManimColor = YELLOW,
                opacity: float | None = None, runtime: float = 0.5) -> ApplyMethod:
        element = self.get_element(element) if isinstance(element, int) else element
        return self.effects.highlight(element, color=color, opacity=opacity, runtime=runtime)

    def unhighlight(self, element: "VisualElement|int", *, opacity: float | None = None, runtime: float = 0.5) -> ApplyMethod:
        element = self.get_element(element) if isinstance(element, int) else element
        return self.effects.unhighlight(element, opacity=opacity, runtime=runtime)

    def indicate(self, element: "VisualElement|int", *, color: ManimColor = YELLOW,
                scale_factor: float = 1.1, runtime: float = 0.5) -> Animation:
        element = self.get_element(element) if isinstance(element, int) else element
        return self.effects.indicate(element, color=color, scale_factor=scale_factor, runtime=runtime)

    def outline(self, element: "VisualElement|int", *, color: ManimColor = PURE_GREEN,
                width: float = 6, runtime: float = 0.5) -> ApplyMethod:
        element = self.get_element(element) if isinstance(element, int) else element
        return self.effects.outline(element, color=color, width=width, runtime=runtime)

    def unoutline(self, element: "VisualElement|int", *, color: ManimColor = WHITE,
                width: float = 4, runtime: float = 0.5) -> ApplyMethod:
        element = self.get_element(element) if isinstance(element, int) else element
        return self.effects.unoutline(element, color=color, width=width, runtime=runtime)

        
    def play(self, *anims, **kwargs):
        """Recursive play: handles single or multiple animations\n
        Can accept either an array or multiple comma-seperated animations
        """
        scene = self.scene
        if not scene:
            raise RuntimeError("No Scene bound. Pass scene=... when creating VisualStructure.")
        scene.player.play(*anims, source=None, **kwargs)
        for element in self.elements: 
            if element.master is not self: #OpenGL mobjects can lose the master ref for some reason
                element.master = self
    
                
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
            if cell_or_index.master is not self:
                # Fall back to identity check in case master references drifted
                if not any(c is cell_or_index for c in self.elements):
                    raise ValueError(
                        f"Cell object does not belong to this {self.__class__.__name__}."
                    )
            return cell_or_index
        
        elif isinstance(cell_or_index, Pointer):
            index = cell_or_index.value
            index = index if index >= 0 else index + len(self.elements)
            return self.get_element(index)
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
            if (0 <= element < len(elements)) or (-len(elements) <= element < len(elements)):#Negative indexing
                return element
            else:
                raise IndexError(f"Index {element} out of bounds for array of size {len(elements)}.")

        elif isinstance(element, VisualElement):
            #manual identity comparison to avoid triggering __eq__()
            owner = element.master
            #Traverses up the heirarchy to find the elemnt's index
            while not getattr(owner,"master",None) is not self and getattr(owner,"master",None) is not None:
                owner = owner.master
                
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


    @property
    def scene(self):
        return self._scene_ref() if self._scene_ref else None

    @scene.setter
    def scene(self, new_scene):
        self._scene_ref = weakref.ref(new_scene) if new_scene else None
        
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
    def __init__(self, body: VMobject=None,master:VisualStructure=None,value:Any=None,label:str=None,**kwargs):
        self.pos = kwargs.pop("pos",None)
        if self.pos is not None:
            self.pos = np.array(self.pos)
        
        else:
            x = kwargs.get("x",None)
            y = kwargs.get("y",None)
            z = kwargs.get("z",None)
            if x is None and y is None and z is None: #Fills in missing axis values if not provided
                self.pos = ORIGIN
                x = x if x is not None else ORIGIN[0]
                y = y if y is not None else ORIGIN[1]
                z = z if z is not None else ORIGIN[2]
                self.pos = np.array([x,y,z])
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
        
    @staticmethod
    def get_mobject_state(mobj: Mobject | None, depth: int = 1) -> dict[str, Any]:
        """Return a snapshot of a Manim mobject's visual attributes."""
        if mobj is None:
            return {}
        submobjects: list[Any] = []
        if depth > 0: #recursively traverses submobjects to get their state
            for child in getattr(mobj, "submobjects", []):
                submobjects.append(VisualElement.get_mobject_state(child, depth=depth - 1))
        else:
            submobjects = [type(child).__name__ for child in getattr(mobj, "submobjects", [])]
            
        state: dict[str, Any] = {
            "type": type(mobj).__name__,
            "z_index": getattr(mobj, "z_index", None),
            "submobjects": submobjects,
        }
        if hasattr(mobj, "get_center"): state["center"] = np.array2string(mobj.get_center(), precision=3)
        if hasattr(mobj, "get_x"):
            state["x"], state["y"], state["z"] = (
                round(float(mobj.get_x()), 3),
                round(float(mobj.get_y()), 3),
                round(float(mobj.get_z()), 3),
            )
        if hasattr(mobj, "get_width"):
            state["width"], state["height"] = (
                round(float(mobj.get_width()), 3),
                round(float(mobj.get_height()), 3),
            )
        if hasattr(mobj, "get_fill_color"): state["fill_color"] = mobj.get_fill_color().to_hex()
        if hasattr(mobj, "get_fill_opacity"): state["fill_opacity"] = float(mobj.get_fill_opacity())
        if hasattr(mobj, "get_stroke_color"): state["stroke_color"] = mobj.get_stroke_color().to_hex()
        if hasattr(mobj, "get_stroke_width"): state["stroke_width"] = float(mobj.get_stroke_width())
        if hasattr(mobj, "get_stroke_opacity"):
            state["stroke_opacity"] = float(mobj.get_stroke_opacity())
        if hasattr(mobj, "get_opacity"): state["opacity"] = float(mobj.get_opacity())
        return state

  

    def _compare(self, other, op: str):
        """Internal unified comparison handler."""
        if resolve_value(other) is NotImplemented:
            return NotImplemented
        if self is other:
            return True
        if _COMPARE_GUARD.get():
            return super().__eq__(other)
        
        token = _COMPARE_GUARD.set(True) #OpenGL does some goofy comparison shi tin .compare(), this is here to short-circuit that
        other_value = other.value if hasattr(other,"value") else other
        operation = get_operation(op=op)
        result = operation(self.value,other_value)

        # DEBUG
        if getattr(self, "master", None) is not None and hasattr(self.master, "logger"):
            idx = None
            if hasattr(self.master, "elements") and self.master.elements is not None:
                for i, el in enumerate(self.master.elements):
                    if el is self:
                        idx = i
                        break
            body = getattr(self, "body", None)
            text = getattr(self, "text", None)
            text_opacity = (
                text.get_fill_opacity() if (text is not None and hasattr(text, "get_fill_opacity"))
                else getattr(text, "fill_opacity", None)
            )
            body_opacity = getattr(body, "fill_opacity", None)
            self.master.logger.debug(
                "compare.visual idx=%s text_opacity=%s body_opacity=%s z_body=%s",
                idx,
                text_opacity,
                body_opacity,
                getattr(body, "z_index", None),
            )

        try:
            if self.master:
                self.master.log_event(_type="compare", other=other, result=result)
            if self.master and self.master.scene and is_animating() and not self.master.scene.in_play:
                if hasattr(self.master, "effects") and hasattr(self.master.effects, "compare"):
                    master_anim = self.master.effects.compare(self, other, result=result)
                    if master_anim:
                        self.master.play(*master_anim)
    
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
        # DEBUG: concise visual state for arithmetic op
        if getattr(self, "master", None) is not None and hasattr(self.master, "logger"):
            idx = None
            if hasattr(self.master, "elements") and self.master.elements is not None:
                for i, el in enumerate(self.master.elements):
                    if el is self:
                        idx = i
                        break
            body = getattr(self, "body", None)
            text = getattr(self, "text", None)
            text_opacity = (
                text.get_fill_opacity() if (text is not None and hasattr(text, "get_fill_opacity"))
                else getattr(text, "fill_opacity", None)
            )
            body_opacity = getattr(body, "fill_opacity", None)
            self.master.logger.debug(
                "arith.visual op=%s idx=%s text_opacity=%s body_opacity=%s z_body=%s",
                op,
                idx,
                text_opacity,
                body_opacity,
                getattr(body, "z_index", None),
            )
        if self.master:
            self.master.log_event(_type=f"arithmetic-{op}", result=result)

        if self.master and self.master.scene and is_animating() and not self.master.scene.in_play:
            master_anim = [ #TODO:Weird text dimming bug occurs if we use Succession or AnimationGroup, that's why a list is used
                self.master.highlight(self, color=color, runtime=0.1),
                self.master.indicate(self, color=color, scale_factor=SCALE_MAP[op], runtime=0.5),
                self.master.unhighlight(self, runtime=0.15),
            ]
            self.master.play(*master_anim)

            if isinstance(other, VisualElement):
                other_master:VisualStructure = getattr(other, "master", None)
                if other_master and other_master.scene and is_animating() is self.master.scene:
                    other_anim = [
                        other_master.highlight(other, color=color, runtime=0.1),
                        other_master.indicate(other, color=color, scale_factor=SCALE_MAP[op], runtime=0.5),
                        other_master.unhighlight(other, runtime=0.15),
                    ]
                    if other_master is self.master:
                        self.master.play(*other_anim)
                    else:
                        other_master.play(*other_anim)
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
