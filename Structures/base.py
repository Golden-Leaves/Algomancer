from manim import *
import numpy as np
from utils import LazyAnimation,flatten_array
class VisualStructure(VGroup):
    def __init__(self, scene, **kwargs):
         super().__init__(**kwargs)
         self.scene = scene
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
                    print(anim)
                    if not isinstance(anim,Animation):
                        raise TypeError(f"Unexpected {type(anim)} passed to play()")
                    self.scene.play(anim, **kwargs)
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
    def __init__(self, body: VMobject,**kwargs):
        super().__init__(**kwargs)
        self.body = body
        self.add(body)

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