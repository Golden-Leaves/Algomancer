from Structures.primitives import Cell
from Structures.base import VisualElementNode,VisualStructureNode
from vispy import scene
from typing import Any
from Components.animations import *
from Components.constants import *
from Components.scene import AlgoScene
class VisualArray(VisualStructureNode):
    def __init__(self,values:list[Any], parent = None,height:int=1,width:int=1, **kwargs):
        super().__init__(parent=parent,height=height,width=width, **kwargs)
        values = values if isinstance(values, list) else list(values)
        self.create_elements(values=values)
    def create_elements(self,values:list[Any]):
        for i in range(len(values)):
            center = (len(values) - 1) / 2
            x = (i - center) * self.width
            cell = Cell(parent=self,value=values[i],pos=(x,self.pos[1])
                        ,color=self.body_color,text_color=self.text_color,text_size=self.text_size)
    
    def __getitem__(self, index):
        return self.get_element(index)
    def __setitem__(self, index, value):
        cell:Cell = self.get_element(index)
        cell.set_value(value)
    def __len__(self):
        return len(self.get_elements())
    
   