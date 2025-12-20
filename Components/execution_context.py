from __future__ import annotations
from typing import TYPE_CHECKING
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
        self._in_compare :bool = False

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

def visualize(user_code:str):
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
    "scene": ctx.scene
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
    ctx.scene.play(animation)
    