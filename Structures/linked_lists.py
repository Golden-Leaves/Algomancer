from manim import *
import numpy as np
import math
from Structures.arrays import VisualArray
from Structures.base import VisualStructure
from __future__ import annotations

class Node(VGroup):
    def __init__(self,value:any,height:int|float,width:int|float,text_color:ManimColor,prev:Node,next:Node,**kwargs):
        super().__init__(**kwargs)
        self.body = VisualArray([value],cell_height=height,cell_width=width,text_color=text_color,rounded=True)
        self.add(self.body)

        self.prev: Node = None
        self.next: Node = None
        

        self.arrow_prev = None
        self.arrow_next = None
        
class VisualLinkedList(VisualStructure):
    def __init__(self,data:any,scene:Scene,node_width:int=2,node_height:int=2,text_color:ManimColor=WHITE,doubly:bool=False,**kwargs):
        self.pos = kwargs.pop("pos",None) #Center of the array
        if self.pos is not None:
            self.pos = np.array(self.pos)
        
        else:
            x = kwargs.get("x",None)
            y = kwargs.get("y",None)
            z = kwargs.get("z",None)
            if x is None and y is None and z is None:
                self.pos = ORIGIN
                x = x if x is not None else ORIGIN[0]
                y = y if y is not None else ORIGIN[1]
                z = z if z is not None else ORIGIN[2]
                self.pos = np.array([x,y,z])
                
        super.__init__(scene,**kwargs)
        self.nodes:list[Node] = []
        self.head:Node = None
        self.tail:Node = None
        self.doubly = doubly
        if data:
            for idx,value in enumerate(data):
                node:Node = Node(value,width=node_width,height=node_height)
                if idx == 0:
                    self.move_to(self.pos)
                else:
                    prev_node:Node = data[idx - 1]
                    self.move_to(prev_node.get_right(),buff=node_width * 0.8)
                    #Some connection logic
                self.nodes.append(node)
                self.add(node)
                        
        def connect(self,node:Node):
            node.right
                