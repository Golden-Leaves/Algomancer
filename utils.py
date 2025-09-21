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
    
def flatten_array(result,objs) -> list:
    """Flattens an iterable"""
    if not isinstance(objs,(tuple,list)):
            result.append(objs)
            return 
    for obj in objs:
        flatten_array(result=result,objs=obj)
    return result