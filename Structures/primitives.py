from vispy import scene
from vispy.scene.visuals import Ellipse,Text,Rectangle
from Structures.base import VisualElementNode
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Components.scene import AlgoScene
class Node(VisualElementNode):
    def __init__(self, scene: "AlgoScene",parent=None, 
                 radius=0.5,text_color="white",**kwargs):
        super().__init__(parent=parent,scene=scene,**kwargs)
        self.body = Ellipse(radius=radius,center=(0,0),border_width=self.border_width,border_color=self.border_color,
                                                 color=self._base_color, parent=self)
        self.text = Text(str(self.value),pos=(0,0),anchor_x='center',anchor_y='center',font_size=20
                         ,color=text_color,parent=self) 
    
    def set_value(self, new_value):
        self.value = new_value
        self.text.text = str(new_value)

class Cell(VisualElementNode):
    def __init__(self,scene: "AlgoScene",parent = None,width=1,height=1,
                 text_color="white",**kwargs):
        super().__init__(parent=parent,scene=scene,**kwargs)
        self.body = Rectangle(center=(0,0),width=width, height=height,border_width=self.border_width,border_color=self.border_color,
                                                 color=self._base_color, parent=self)
        self.text = Text(str(self.value),pos=(0,0),anchor_x='center',anchor_y='center',font_size=20
                         ,color=text_color,parent=self) 
        
    def set_value(self, new_value):
        self.value = new_value
        self.text.text = str(new_value)
        