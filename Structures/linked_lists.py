from __future__ import annotations
from manim import *
import numpy as np
import math
from Structures.arrays import VisualArray
from Structures.base import VisualStructure

class Node(VGroup):
    def __init__(self,value:any,scene:Scene,height:int|float,width:int|float,text_color:ManimColor=WHITE,prev:Node = None,next:Node = None,**kwargs):
        super().__init__(**kwargs)
        self.body = VisualArray([value],scene=scene,cell_height=height,cell_width=width,text_color=text_color,rounded=True)
        self.add(self.body)

        self.prev: Node = prev
        self.next: Node = next
        

        self.arrow_prev = None
        self.arrow_next = None
        
class VisualLinkedList(VisualStructure):
    def __init__(self,data:any,scene:Scene,node_width:int|float=1.25,node_height:int|float=0.5,text_color:ManimColor=WHITE,doubly:bool=False,**kwargs):
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
                
        super().__init__(scene,**kwargs)
        self.nodes:list[Node] = []
        self.head:Node = None
        self.tail:Node = None
        self.doubly = doubly
        
        if data:
            for idx,value in enumerate(data):
                node:Node = Node(value,scene=scene,width=node_width,height=node_height,text_color=text_color)
                if idx == 0:
                    self.head = node
                    node.move_to(self.pos)
                    
                else:
                    prev = self.nodes[idx - 1]
                    node.next_to(prev.get_right(), buff=node_width * 0.8)
                    
                    prev.next = node
                    if self.doubly:
                        node.prev = prev
                        

                self.nodes.append(node)
                self.add(node)
                self.move_to(self.pos)
                
    def connect(self,node:Node) -> AnimationGroup: #Use Animation Groups
        """Connects the sides of the current node"""
        anims = []
        if node.next:
            node.arrow_next = Arrow(node.get_right(), node.next.get_left(), buff=0.1)
            anims.append(GrowArrow(node.arrow_next,run_time=1.5))
            
        if node.prev and self.doubly:
            node.arrow_prev = Arrow(node.get_left(),node.prev.get_right())  
            anims.append(GrowArrow(node.arrow_prev,run_time=1.5))
            
        return AnimationGroup(*anims,lag_ratio=0.2) if anims else None
        
    def create(self) -> AnimationGroup:
        
        """Creates the linked list"""
        nodes = AnimationGroup(*[node.body.create() for node in self.nodes], lag_ratio=0.2)
        arrows = AnimationGroup(*[self.connect(node) for node in self.nodes if self.connect(node)],lag_ratio=0.1)
    
        return [nodes,arrows]
                    
        