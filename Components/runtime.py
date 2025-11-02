from __future__ import annotations
from manim import *
import contextvars
import contextlib
import sys
import weakref
import numpy as np
from typing import TYPE_CHECKING
from screeninfo import get_monitors
from Components.logging import setup_logging
from Components.animations import LazyAnimation
from Components.helpers import flatten_array
if TYPE_CHECKING:
    from Structures.base import VisualStructure

def compute_window_size(scale: float = 0.75) -> tuple[int, int]:
      monitor = get_monitors()[0]  #primary display
      width = int(monitor.width * scale)
      height = int(monitor.height * scale)
      return width, height

config.pixel_width = 1920
config.pixel_height = 1080
config.window_size = compute_window_size(0.75)  #75% of the screen
config.samples=1

ANIMATION_CONTEXT = contextvars.ContextVar("ANIMATION_CONTEXT", default=False) 
CURRENT_LINE = contextvars.ContextVar("CURRENT_LINE", default=None)
@contextlib.contextmanager
def animation_context():
    """Temporarily enable animation mode for user-level operations."""
    previous_trace = sys.gettrace()
    token = ANIMATION_CONTEXT.set(True)

    def tracer(frame, event, arg):
        if event == "line":
            code = frame.f_code
            CURRENT_LINE.set((code.co_filename, frame.f_lineno, code.co_name))
        return tracer

    try:
        sys.settrace(tracer)
        yield  # "Pause" and let the user do whatever
    finally:
        sys.settrace(previous_trace)  #Resets tracer state
        ANIMATION_CONTEXT.reset(token)
        CURRENT_LINE.set(None)
        

def is_animating() -> bool:
    """Return True if currently inside an animation context."""
    return ANIMATION_CONTEXT.get()

class AlgoScene(Scene):
    """Scene subclass that tracks play state, registered structures, and drag-scaling."""

    _inside_play_call = False

    def __init__(
        self,
        renderer=None,
        camera_class=None,
        always_update_mobjects=False,
        random_seed=None,
        skip_animations=False,
    ):
        self.logger = setup_logging(logger_name=__name__)
        super().__init__(renderer, camera_class, always_update_mobjects, random_seed, skip_animations)
        self._trace = []
        self._structures: weakref.WeakValueDictionary[int, VisualStructure] = weakref.WeakValueDictionary()
        self._active_structure = None
        self.player = PlayManager(scene=self)

    @contextlib.contextmanager
    def animation_context(self):
        # Do this so the user doesn't need to import the other one but simply call self.animation_context()
        with animation_context():
            yield

    @property
    def in_play(self):  # convenience lol
        return self._inside_play_call

    def play(self, *anims, **kwargs):
        return self.player.play(*anims, source=None, **kwargs)

    def _play_direct(self, *anims, **kwargs):
        return super().play(*anims, **kwargs)
    
    def register_structure(self,structure:VisualStructure) -> None:
        """Remember a structure so we can find it later."""
        self._structures[id(structure)] = structure
    
    def get_structure_under_cursor(self,point) -> VisualStructure:
        """Return the top-most structure whose rectangle contains the given point."""
        for structure in reversed(list(self._structures.values())):
            if structure is None:
                continue

            x_min,x_max = structure.get_left()[0],structure.get_right()[0]
            y_min,y_max = structure.get_bottom()[1],structure.get_top()[1]
            if (x_min <= point[0] <= x_max) and (y_min <= point[1] <= y_max):
                return structure
    
    def _start_drag(self,structure:VisualStructure,point):
        """Lock in the grab point so drag updates scale around this reference."""
        origin = structure.get_center()
        vec = point - origin
        norm = np.linalg.norm(vec)
        if norm < 1e-6:
            axis = RIGHT
            base = 1.0
        else:
            axis = vec / norm  # unit vector
            base = norm  # current distance from origin
        self._active_structure = {
            "structure": structure,
            "origin":origin,
            "axis":axis,
            "base":base,
            "scale":1.0 #structure's current scale,because we want to scale off the original size
        }
    
    
    def _update_drag(self,point):
        """Adjust the active structure's scale based on the current cursor position."""
        structure_under_point = self.get_structure_under_cursor(point=point)
        state = self._active_structure

        if state:
            current_structure:VisualStructure = state["structure"]
            print("Is structure_under_point the same as current_structure?",structure_under_point is current_structure)
            if structure_under_point is not current_structure:
                self._end_drag()
                state = None

        if not state:
            if structure_under_point is None: #Theres no structure under the cursor, prevents "scaling" when clicking elsewhere
                return False
            self._start_drag(structure=structure_under_point,point=point)
            state = self._active_structure
            if not state:
                return False
        
        structure:VisualStructure = state["structure"]
        cursor_vec = point - state["origin"]
        length = max(0.1,np.linalg.norm(cursor_vec)) #structure's new "size"

        scale_factor = length / state["base"] #new_length / old_length
        incremental = scale_factor / state["scale"] #Divide by previous scale to get actual scale(we want additive scaling)
        if not np.isfinite(incremental) or incremental == 0:
            return False
        structure.scale(incremental,about_point=state["origin"])
        state["scale"] = scale_factor
        return True
        
    def _end_drag(self):
        if self._active_structure:
            self._active_structure = None
        

    def on_mouse_drag(self, point, d_point, buttons, modifiers):
        from pyglet.window import mouse
        draggable = False
        if buttons & mouse.LEFT:
            draggable = self._update_drag(point=point)
        else:
            self._end_drag()
        if not draggable:
            self._end_drag()
            return super().on_mouse_drag(point=point,d_point=d_point,buttons=buttons,modifiers=modifiers)
        return None
    
    
    
        
    
def get_current_line_metadata() :
    return CURRENT_LINE.get()

class PlayManager:
    def __init__(self,scene:AlgoScene,**kwargs):
        self.scene = scene
        
    def play(self,*anims, source=None, **kwargs): #Hijacks Scene.play(), set the flag to True if playing and False when finished
        type(self.scene)._inside_play_call = True 
        try:
            resolved = []
            for anim in flatten_array(result=[],objs=anims):
                if not anim:
                    continue
                anim = anim.build() if isinstance(anim, LazyAnimation) else anim
                if not isinstance(anim, Animation):
                    raise TypeError(f"Unexpected {type(anim)} passed to play()")
                resolved.append(anim)
            if resolved:
                self.scene._play_direct(*resolved, **kwargs)
        finally:
            type(self.scene)._inside_play_call = False
