from manim import *
from Structures.base import VisualStructure,VisualElement
from utils import get_offset_position
class Pointer(VisualStructure):
    def __init__(self,index:int,master:VisualStructure,scene:Scene,label:str = "",color=YELLOW,direction="up",**kwargs):
        self.scene = scene
        super().__init__(scene=self.scene,**kwargs)
        self.index = index #Pointer's current index
        self.master:VisualStructure = master
        self.label = label
        self.arrow = None
        self.color = color
        self.direction = direction
         

    def set_index(self,index):
        """Update pointer's index and animate movement to the new cell."""
        self.index = index
    
    
    def __index__(self): return self.index
    def __int__(self): return self.index
    def __repr__(self): return f"Pointer({self.index})"

    
    def __eq__(self, other): return int(self) == int(other)
    def __ne__(self, other): return int(self) != int(other)
    def __lt__(self, other): return int(self) < int(other)
    def __gt__(self, other): return int(self) > int(other)
    def __le__(self, other): return int(self) <= int(other)
    def __ge__(self, other): return int(self) >= int(other)
    
    def __add__(self, value):
        new_index = self.index + value
        self.scene.play(self.move_pointer(new_index))
        self.index = new_index
        return self

    def __sub__(self, value):
        new_index = self.index - value
        self.scene.play(self.move_pointer(new_index))
        self.index = new_index
        return self

  
    
    
    def create_arrow(self):
        master_element:VisualElement = self.master[self.index]
        
        # arrow_end = get_offset_position(master_element, direction=self.direction)
        # # arrow tail (further away)
        # arrow_start = get_offset_position(master_element,coordinate=arrow_end,direction=self.direction, buff=1.1)
        if self.direction is UP:
            arrow_end = get_offset_position(master_element, direction=self.direction, buff=0.05)
            arrow_start = get_offset_position(master_element,coordinate=arrow_end, direction=self.direction)
            
        self.arrow = Arrow(arrow_start, arrow_end, buff=0.1, stroke_width=master_element.body_width * 0.45)
        
        # Direction vector
        vec = arrow_end - arrow_start
        unit = vec / np.linalg.norm(vec)
        perp = np.array([-unit[1], unit[0], 0])  # perpendicular
        
        # Label positioned near tail
        text_scale = self.arrow.stroke_width * 0.8
        self.label = Text(self.label).scale(text_scale)
        # self.label.move_to(arrow_start + perp * (master_element.body_width * 0.3))
        # self.label.align_to(self.arrow, UP)  # aligns horizontally across the arrow shaft
        # self.label.next_to(self.arrow, self.direction, buff=0.1).align_to(self.arrow, -self.direction)
        arrow_length = np.linalg.norm(self.arrow.get_end() - self.arrow.get_start())
        self.label.move_to(self.arrow.get_start() + self.direction * (arrow_length))
        self.label.align_to(self.arrow, self.direction)
        

        
        self.add(self.arrow,self.label)
        return AnimationGroup(Create(self.arrow),Write(self.label),lag_ratio=0.2)
        
    def move_pointer(self,index:int):
        master_element:VisualElement = self.master.get_element(index)
        arrow_pos = self.arrow.get_center()
        if self.direction in (UP,DOWN):#Move to target's x
            new_pos = np.array([master_element.center[0], arrow_pos[1], 0])
        
        elif self.direction in ("left", "right"): #Move to target's y
            new_pos = np.array([arrow_pos[0], master_element.center[1], 0])
        else:
            raise ValueError(f"Invalid direction: {self.direction}")
        return ApplyMethod(self.move_to,new_pos)