from __future__ import annotations
from typing import TYPE_CHECKING
from contextlib import contextmanager
from typing import Iterator
if TYPE_CHECKING:
    from Components.animations import Animation,Sequence,Parallel
    from Components.scene import AlgoScene
class Tracer:
    def __init__(self):
        """
        Initializes a Tracer instance.

        It is used to record animations before they are played.

        Attributes
        ----------
        enabled : bool
            Whether the Tracer instance is enabled or disabled.
        animations : list[Animation|Sequence|Parallel]
            The list of animations recorded by the Tracer instance.
        """
        self.enabled = False
        self.animations: list[Animation|Sequence|Parallel] = []
    
    def begin(self):
        self.enabled = True
        self.animations.clear()

    def end(self):
        self.enabled = False

    def record_animation(self, animation: Animation):
        if self.enabled:
            self.animations.append(animation)
            
_current_tracer: None | Tracer = None
def get_tracer() -> Tracer | None:
    return _current_tracer

_current_scene:None | AlgoScene = None
def get_scene() -> AlgoScene | None:
    return _current_scene

class ExecutionContext:
    def __init__(self):
        """
        Initializes an ExecutionContext instance.

        Attributes
        ----------
        tracer : Tracer
            Instance of Tracer used to record animations before they are played.
        scene : AlgoScene
            Instance of AlgoScene used to render the recorded animations.
        """
        from Components.scene import AlgoScene
        self.tracer = Tracer()
        self.scene = AlgoScene()
    def __enter__(self):
        global _current_tracer,_current_scene
        _current_tracer = self.tracer
        _current_scene = self.scene
        self.tracer.begin()
        return self

    def __exit__(self, exc_type, exc, tb):
        global _current_tracer
        self.tracer.end()
        _current_tracer = None
    def run(self,user_code:str,user_globals:dict):
        exec(user_code,user_globals)

def visualize_text(user_code:str):
    """
    Visualize a code snippet by executing it and animating the result.
    This takes code as a text input.
    
    Parameters
    ----------
    user_code : str
        The code snippet to visualize.

    Notes
    -----
    The code snippet is executed in a separate execution context, which allows the user to access
    all Algomancer animations and structures without importing.
    """
    from Structures.arrays import VisualArray,Cell
    from Components.animations import Sequence
    from Components.logging import DebugLogger
    logger = DebugLogger(f"{__name__}.visualize")
    ctx = ExecutionContext()
    user_globals = {
    "__builtins__": __builtins__,
    "VisualArray": VisualArray,
    "Cell": Cell,
    "DebugLogger":DebugLogger,
    "scene": ctx.scene,
    "animations": ctx.tracer.animations
}
    with ctx:
        ctx.run(user_code=user_code,user_globals=user_globals)
    events = ctx.tracer.animations
    logger.debug("Animations: %s",events)
    if not events:
        return
    if len(events) == 1:
        animation = events[0]
    else:
        animation = Sequence(*events)
    logger.debug("Animation: %s",animation)
    ctx.scene.play(animation)
@contextmanager
def visualize() -> Iterator[ExecutionContext]:
    """
    Visualize a code snippet by executing it and animating the result.

    Yields
    -------
    ctx : ExecutionContext
        Instance of ExecutionContext used to execute the code snippet.

    Returns
    -------
    Iterator[ExecutionContext]
        An iterator that yields the ExecutionContext instance.
    """
    from Structures.arrays import VisualArray,Cell
    from Components.animations import Sequence
    from Components.logging import DebugLogger
    logger = DebugLogger(f"{__name__}.visualize")
    ctx = ExecutionContext()          

    with ctx:                         
        yield ctx                    

    events = ctx.tracer.animations
    logger.debug("Animations: %s", events)
    if not events:
        return

    if len(events) == 1:
        animation = events[0]
    else:
        animation = Sequence(*events)

    ctx.scene.play(animation)
