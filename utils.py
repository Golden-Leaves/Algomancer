from manim import *
class LazyAnimation:
    """Wrapper for a function that builds an Animation lazily.
    Anything that modifies self.cells will use this\n
    This is used to allow multiple animations to be passed to play(), since this prevents them from being evaluated
    """
    def __init__(self, builder):
        self.builder = builder
    def build(self) -> Animation:
        anim = self.builder()
        return anim
    
