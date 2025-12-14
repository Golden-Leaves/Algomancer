from __future__ import annotations
from manim import *
from manim.renderer.opengl_renderer import OpenGLRenderer
from manim.renderer.cairo_renderer import CairoRenderer
from manim_slides import Slide
import contextvars
import contextlib
import sys
from pathlib import Path
import weakref
import numpy as np
from typing import TYPE_CHECKING,Callable,Any,Generator,Iterable
from types import FrameType
from screeninfo import get_monitors
from enum import Enum
import os

from Components.logging import DebugLogger
from Components.animations import LazyAnimation
from Components.helpers import flatten_array
from Components.config import DEFAULT_CONFIG as CFG
from manim.utils.hashing import get_hash_from_play_call
if TYPE_CHECKING:
    from Structures.base import VisualStructure

def compute_window_size(scale: float = 0.75) -> tuple[int, int]:
      monitor = get_monitors()[0]  #primary display
      width = int(monitor.width * scale)
      height = int(monitor.height * scale)
      return width, height

config.pixel_width = CFG.render.pixel_width
config.pixel_height = CFG.render.pixel_height
config.window_size = compute_window_size(0.75)  #75% of the screen
config.samples=CFG.render.samples

EXCLUDED_DIRS = {".venv", "site-packages", "manim", "Components","Structures"}
ACTIVE_SCRIPT = None
PROJECT_ROOT = Path.cwd().resolve()

ANIMATION_CONTEXT = contextvars.ContextVar("ANIMATION_CONTEXT", default=False) 
CURRENT_LINE = contextvars.ContextVar("CURRENT_LINE", default=None)
@contextlib.contextmanager
def enable_animation() -> Generator[None, None, None]:
    """Temporarily enable animation mode for user-level operations.

    Enables animation mode for the duration of the context manager.
    Use this context manager to wrap user-level operations that should be
    animated.

    :return: None
    :rtype: Generator[None, None, None]
    """
    from Components.helpers import is_user_file
    token = ANIMATION_CONTEXT.set(True)
    previous_tracer = sys.gettrace()
   
    def trace(frame: FrameType, event: str, arg: Any) -> Callable[[FrameType, str, Any], None]:
        if event == "line" :
            CURRENT_LINE.set((frame.f_code.co_filename, frame.f_lineno, frame.f_code.co_name))
        return trace

    try:
        sys.settrace(trace)
        yield
    finally:
        sys.settrace(previous_tracer)
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
        os.makedirs("DEBUG",exist_ok=True)
        self.logger = DebugLogger(logger_name=__name__)
        super().__init__(renderer, camera_class, always_update_mobjects, random_seed, skip_animations)
        self._trace = []
        self._structures: weakref.WeakValueDictionary[int, VisualStructure] = weakref.WeakValueDictionary()
        self._active_structure = None
        self.player = PlaybackController(scene=self)
        self._keys_down:set = set([])
        self._last_toggle:float = 0.0 #There shuold be a 200ms cooldown between each key combination

    @contextlib.contextmanager
    def animation_context(self):
        #Do this so the user doesn't need to import the other one but simply do "with self.animation_context():"
        with enable_animation():
            yield

    @property
    def in_play(self):  # convenience lol
        return self._inside_play_call

    def play(self, *animations, sequential: bool = True, **kwargs):
        """
        Play one or more animations with optional parallel execution.

        Parameters
        ----------
        animations : Animation or LazyAnimation, or iterables
            Animation or LazyAnimation to play. Non-animation inputs raise TypeError.
        sequential : bool, optional
            When True (default), runs resolved animations back-to-back.
            When False, forwards all resolved animations in a single call so Manim
            plays them in parallel.
        kwargs : dict, optional
            Passed through to Manim/renderer (e.g., run_time, rate_func).

        Notes
        -----
        - To play animations in parallel, pass sequential=False.
        - To play animations sequentially, pass sequential=True.
        """
        self.logger.info(animations)
        def resolve_animations(animations: Iterable[Animation | LazyAnimation]) -> Iterable[Animation]:
            """
            Resolve a list of Animation or LazyAnimation objects into a list of Animation objects.
            
            Parameters
            ----------
            animations : Iterable[Animation | LazyAnimation]
                Animation or LazyAnimation objects to resolve.
            
            Returns
            -------
            Iterable[Animation]
                Resolved list of Animation objects.
            
            Raises
            ------
            TypeError
                If an unexpected object type is passed to resolve_animations.
            """
            resolved = []
            for anim in flatten_array(result=[],objs=animations):
                if not anim:
                    continue
                anim = anim.build() if isinstance(anim, LazyAnimation) else anim
                if not isinstance(anim, Animation):
                    raise TypeError(f"Unexpected {type(anim)} passed to play()")
                resolved.append(anim)
            if resolved:
                self.logger.debug("List of animations(inside check): %s", resolved)
            return resolved
        
        resolved = resolve_animations(animations)
        if sequential:
            for anim in resolved:
                self.player.play(anim,**kwargs)
        else:
            self.player.play(*resolved,**kwargs)
    
    def register_structure(self, structure: VisualStructure) -> None:
        """Remember a structure so we can find it later."""
        self._structures[id(structure)] = structure
    
    def get_structure_under_cursor(self, point) -> VisualStructure:
        """Return the top-most structure whose rectangle contains the given point."""
        for structure in reversed(list(self._structures.values())):
            if structure is None:
                continue
            x_min,x_max = structure.get_left()[0],structure.get_right()[0]
            y_min,y_max = structure.get_bottom()[1],structure.get_top()[1]
            if (x_min <= point[0] <= x_max) and (y_min <= point[1] <= y_max):
                return structure
    
    def _start_drag(self, structure: VisualStructure, point) -> None:
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
    
    
    def _update_drag(self, point) -> bool:
        """Adjust the active structure's scale based on the current cursor position."""
        structure_under_point = self.get_structure_under_cursor(point=point)
        state = self._active_structure

        if state:
            current_structure:VisualStructure = state["structure"]
            # print("Is structure_under_point the same as current_structure?",structure_under_point is current_structure)
            if structure_under_point is not current_structure:
                self._end_drag()
                state = None

        if not state:
            if structure_under_point is None: #Theres no structure under the cursor, prevents "scaling" when clicking elsewhere
                return False
            self._start_drag(structure=structure_under_point, point=point)
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
        structure.scale(incremental, about_point=state["origin"])
        state["scale"] = scale_factor
        return True
        
    def _end_drag(self):
        if self._active_structure:
            self._active_structure = None
        

    def on_mouse_drag(self, point, d_point, buttons, modifiers) -> None:
        from pyglet.window import mouse
        draggable = False
        if buttons & mouse.LEFT: #Resizing
            draggable = self._update_drag(point=point)
        else:
            self._end_drag()
            
        if not draggable:
            self._end_drag()
            return super().on_mouse_drag(point=point,d_point=d_point,buttons=buttons,modifiers=modifiers)
        return None
    
    def on_key_press(self, symbol, modifiers) -> None: #Symbol is the key pressed, while modifiers are keys held(CTRL,...)
        from pyglet.window import key
        import time
        
        def cooldown_ended(cooldown:float=0.2) -> bool:
            now = time.time()
            return True if now - self._last_toggle > cooldown else False  #Default 200ms between each key combination
        
        if symbol in self._keys_down: #Guards against repetitive spam , e.g when some one holds ctrl + p
            return
        
        if symbol == key.SPACE:
            self._keys_down.add(key.SPACE)
            if cooldown_ended():
                if self.player.state == PlaybackState.PLAYING:
                    self.player.pause()
                elif self.player.state == PlaybackState.PAUSED:
                    self.player.resume()
                self._last_toggle = time.time()
                
        if symbol == key.PERIOD:
            self._keys_down.add(key.PERIOD)
            if cooldown_ended(cooldown=0.1):
                if self.player.state == PlaybackState.PAUSED:
                    self.player.step_frames(frames=1)
                self._last_toggle = time.time()
            
        
                
        return super().on_key_press(symbol, modifiers)
    
    def on_key_release(self, symbol, modifiers):
        if symbol in self._keys_down:
            self._keys_down.remove(symbol)
        return super().on_key_release(symbol, modifiers)



class AlgoSlide(Slide, AlgoScene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def next_slide(self, loop: bool = False, *args, **kwargs):
        """Advances to the next slide in the presentation.

        If loop is True, the animation will continually replay itself

        Parameters
        ----------
        loop : bool, optional
            If loop is True, the animation will continually replay itself\n
            Defaults to False.
        *args : Any
            Additional arguments to pass to the underlying `Slide.next_slide` method.
        **kwargs : Any
            Additional keyword arguments to pass to the underlying `Slide.next_slide` method.
        """
        super().next_slide(loop=loop, *args, **kwargs)
        
class PlaybackState(str, Enum):
    """Lifecycle states for PlaybackController."""

    IDLE = "idle"
    PLAYING = "playing" #in_play property of AlgoScene is still needed to guard against internals
    PAUSED = "paused"
    FINISHED = "finished"

class PlaybackController:
    """Cooperative playback engine that owns AlgoScene.play lifecycle.

    Parameters
    ----------
    scene : AlgoScene
        Scene instance whose renderer, file writer, and animations are managed.
    """

    def __init__(self,scene:AlgoScene,**kwargs):
        self.paused = False
        self.scene = scene
        self.logger = DebugLogger(logger_name=f"{__name__}.PlaybackController")
        self.renderer: OpenGLRenderer | CairoRenderer = scene.renderer
        self.state: PlaybackState = PlaybackState.IDLE
        self._playback_queue = {}
        self._playback_timeline = []
        self.capture_enabled:bool = True
        self._step_time_delta:float = 0.0 #Time difference for n frames stepped
        self._last_t:float = 0.0
    def capture_data(self,animation:Animation):
        line_info = CURRENT_LINE.get()
        if line_info not in self._playback_queue:
            self._playback_queue[line_info] = animation
            self._playback_timeline.append(line_info)
        
    def play(self,*animations,capture:bool=True,**kwargs): #Hijacks Scene.play(), set the flag to True if playing and False when finished
        import threading
        import time
        #Some functionality were taken from manim's repo
        #https://github.com/ManimCommunity/manim/blob/main/manim
        def begin_animations(
            scene:AlgoScene,renderer:CairoRenderer|OpenGLRenderer,
            animations:list[Animation], **kwargs) -> None:
            """Initialize rendering state for the given scene and animations.
            Parameters
            ----------
            scene : AlgoScene
                Scene instance whose renderer, file writer, and animations are managed.
            renderer : CairoRenderer | OpenGLRenderer
                Renderer instance to manage the rendering state.
            animations : list[Animation]
                List of Animation instances to render.
            **kwargs
                Additional keyword arguments passed to the scene's compile_animation_data method.
            """
            if not hasattr(renderer, "animations_hashes"):
                renderer.animations_hashes = []  # type: ignore[attr-defined]

            if not config["disable_caching"]:
                hash_play = get_hash_from_play_call(
                    renderer,
                    renderer.camera,
                    animations,
                    scene.mobjects,
                )
                if renderer.file_writer.is_already_cached(hash_play):
                    renderer.skip_animations = True
            else:
                hash_play = f"uncached_{renderer.num_plays:05}"

            renderer.animations_hashes.append(hash_play)
            renderer.file_writer.add_partial_movie_file(hash_play)

            renderer.file_writer.begin_animation(not renderer.skip_animations)
            scene.compile_animation_data(*animations,**kwargs)
            scene.begin_animations()
            
        def finalize_animations(renderer:OpenGLRenderer|CairoRenderer,scene:AlgoScene) -> None:
            renderer.file_writer.end_animation(not renderer.skip_animations)
            renderer.time += scene.duration
            renderer.num_plays += 1
            
        def render_frozen_frame(renderer: OpenGLRenderer | CairoRenderer, scene: AlgoScene) -> None:
                """Render a single frozen frame, duplicating it to match scene.duration.

                Mirrors Manim's OpenGLRenderer.play frozen-frame branch
                """
                renderer.update_frame(scene)
                if not renderer.skip_animations:
                    renderer.file_writer.write_frame(
                        renderer,
                        num_frames=int(config.frame_rate * scene.duration),
                    )
                if not isinstance(renderer,CairoRenderer) and renderer.window is not None :
                    renderer.window.swap_buffers()
                    while time.time() - renderer.animation_start_time < scene.duration:
                        pass
                renderer.animation_elapsed_time = scene.duration
        def run_animation_loop(scene: AlgoScene,renderer:OpenGLRenderer|CairoRenderer, skip_rendering: bool = False) -> None:
            """Advance animations for the given scene frame-by-frame and render each frame.

            Mirrors Scene.play_internal() logic
            """
            assert scene.animations is not None
            scene.duration = scene.get_run_time(scene.animations)
            scene.time_progression = scene._get_animation_time_progression(
                scene.animations,
                scene.duration,
            )
            for t in scene.time_progression:  
                # self.logger.debug("Current time progression: %s; time progression type: %s",t,type(t))
                while self.state == PlaybackState.PAUSED and self._step_time_delta == 0:
                    renderer.render(scene, self._last_t, scene.moving_mobjects) #so inputs and changes(scaling) can still be rendered
                    time.sleep(0.01)
                    
                if self.state == PlaybackState.PAUSED and self._step_time_delta > 0: #Step to the correct frame first before pausing
                    self._step_time_delta -= (1/config.frame_rate)
                    
                scene.update_to_time(t) #Animations will be rendered as if they're at the time t
                if not skip_rendering and not scene.skip_animation_preview:
                    renderer.render(scene, t, scene.moving_mobjects)
                if scene.stop_condition is not None and scene.stop_condition():
                    scene.time_progression.close()
                    break
                self._last_t = t

            for animation in scene.animations:
                animation.finish()
                animation.clean_up_from_scene(scene)
            if not scene.renderer.skip_animations:
                scene.update_mobjects(0)
            # TODO: The OpenGLRenderer does not have the property static.image.
            scene.renderer.static_image = None  # type: ignore[union-attr]
            # Closing the progress bar at the end of the play.
            scene.time_progression.close()
        
        # animations = resolve_animations(animations=animations)
        type(self.scene)._inside_play_call = True
        if self.state != PlaybackState.PAUSED: 
            self.state = PlaybackState.PLAYING
        # if self.capture_enabled:
        #     self.capture_data(animation=animations)
        #     self.logger.info("Playback queue: %s",self._playback_queue)
        #     self.logger.info("Playback timeline: %s",self._playback_timeline)
        #     return
        self.renderer.animation_start_time = time.time()
        begin_animations(scene=self.scene, renderer=self.renderer, animations=animations)
        
        if self.scene.is_current_animation_frozen_frame():  # Frozen frame
            render_frozen_frame(self.renderer, self.scene)
            finalize_animations(self.renderer, self.scene)
            type(self.scene)._inside_play_call = False
            self.state = PlaybackState.IDLE
            return None

        run_animation_loop(self.scene,renderer=self.renderer, skip_rendering=False)
        finalize_animations(self.renderer, self.scene)
        type(self.scene)._inside_play_call = False
        self.state = PlaybackState.IDLE
        return None
            
            
            

            

            
            
            
    def pause(self): self.state = PlaybackState.PAUSED
    def resume(self): self.state = PlaybackState.PLAYING
    def step_frames(self,frames:float=1):
        if self.state == PlaybackState.PAUSED:
            self._step_time_delta += (frames / config.frame_rate)
            
    def seek_seconds(self,seconds:float=1.0):
        if self.state == PlaybackState.PAUSED:
            self.step_frames(seconds * config.frame_rate)
