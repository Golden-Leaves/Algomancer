from manim import *
import numpy as np
import math
from Structures.arrays import VisualArray,Cell,LazyAnimation
class Node(VGroup):
    def __init__(self,value,left,right,doubly=False, **kwargs):
        super().__init__(**kwargs)
        self.body = VisualArray([value])
        self.add(self.body)
        if doubly:
            self.left = left
        self.right = right
        
class VisualLinkedList(VGroup):
    def __init__(self,data,scene,node_width=2,node_height=2,text_color=WHITE,**kwargs):
        super.__init__(**kwargs)