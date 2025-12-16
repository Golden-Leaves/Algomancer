from vispy import scene
from typing import Any
from vispy.scene.visuals import Polygon
class VisualElementNode(scene.Node):
    def __init__(self,value:Any,pos = (0,0), color = (0.15, 0.55, 0.95, 1.0),border_width = 2,border_color = "white",
                 parent = None, name = None, transforms = None):
        super().__init__(parent, name, transforms)
        self.body:Polygon = None
        self.value = value
        self._pos = pos
        self.color = color
        self.border_width = border_width
        self.border_color = border_color   
    @property
    def pos(self):
        return self._pos
    
    @pos.setter
    def pos(self,pos):
        self._pos = pos
        