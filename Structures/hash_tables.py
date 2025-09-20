from manim import *
import numpy as np
import math
from Structures.arrays import VisualArray,Cell,LazyAnimation
from Structures.base import VisualStructure
class VisualHashTable(VisualStructure):
    def __init__(self,data:dict,scene,table_width,table_height,text_color=WHITE,**kwargs):
        super().__init__(scene,**kwargs)
        self.table_width = table_width
        self.table_height = table_height
        self.scene = scene
        self.text_color = WHITE
        self.table = {}
        
        if data:
            for key,value in data.items():
                pass
            