from manim import *
from base import VisualStructure
class Pointer(VGroup):
    def __init__(self,value:int,master:VisualStructure,label:str|None = None,color=YELLOW,direction="up",**kwargs):
        self.value = value
        self.master = master
        self.label = label
        self.color = color
        def make_labeled_arrow(start, end, label, buff=0.1):
        #     arrow = Arrow(start, end, buff=buff, stroke_width=self.cell_width * 0.45)
            
        #     # Direction vector
        #     vec = end - start
        #     unit = vec / np.linalg.norm(vec)
        #     perp = np.array([-unit[1], unit[0], 0])  # perpendicular
            
        #     # Label positioned near tail
        #     text_scale = arrow.stroke_width * 0.8
        #     text = Text(label).move_to(start + perp * (self.cell_height * 0.3)).scale(text_scale)
            
        #     return VGroup(arrow, text)
    def set_value(self,value):
        """Update pointer's index and animate movement to the new cell."""
        self.value = value
        
    def move_pointer(self,index:int):
        