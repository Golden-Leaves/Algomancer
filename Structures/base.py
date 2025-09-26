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