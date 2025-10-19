from manim import *
import contextvars
import contextlib
import sys

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
        sys.settrace(previous_trace)  # Resets tracer state
        ANIMATION_CONTEXT.reset(token)
        CURRENT_LINE.set(None)

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
            yield 

    def play(self, *args, **kwargs): #Hijacks Scene.play(), set the flag to True if playing and False when finished
        type(self)._inside_play_call = True 
        try:
            super().play(*args, **kwargs)
        finally:
            type(self)._inside_play_call = False

    @property
    def in_play(self): #convinience lol
        return self._inside_play_call
    
def get_current_line_metadata():
    return CURRENT_LINE.get()
