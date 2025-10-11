from manim import *
import contextvars
import contextlib


ANIMATION_CONTEXT = contextvars.ContextVar("ANIMATION_CONTEXT", default=False)

@contextlib.contextmanager
def animation_context():
    """Temporarily enable animation mode for user-level operations."""
    token = ANIMATION_CONTEXT.set(True)
    try:
        yield
    finally:
        ANIMATION_CONTEXT.reset(token)

def is_animating() -> bool:
    """Return True if currently inside an animation context."""
    return ANIMATION_CONTEXT.get()
class AlgoScene(Scene):
    """Scene subclass that knows when it's playing an animation."""
    _inside_play_call = False

    @contextlib.contextmanager
    def animation_context(self):
        #Do this so the user doesn't need to import the other one but simply call self.animation_context()
        with animation_context():
            yield #"Pause" and let the user do whatever

    def play(self, *args, **kwargs): #Hijacks Scene.play(), set the flag to True if playing and False when finished
        type(self)._inside_play_call = True
        try:
            super().play(*args, **kwargs)
        finally:
            type(self)._inside_play_call = False

    @property
    def in_play(self): #convinience lol
        return self._inside_play_call