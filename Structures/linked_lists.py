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
        self.scene = scene
        self.node_width = node_width
        self.node_height = node_height
        self.text_color = text_color
        self.length = 0
        
        if data:
            for idx,value in enumerate(data):
                node:Node = Node(value,scene=scene,width=node_width,height=node_height,text_color=text_color)
                if idx == 0:
                    self.head = node
                    self.tail = self.head
                    node.move_to(self.pos)
                    
                else:
                    prev = self.nodes[idx - 1]
                    node.next_to(prev.get_right(), buff=node_width * 0.7)
                    
                    prev.next = node
                    if self.doubly:
                        node.prev = prev

                        

                self.nodes.append(node)
                self.add(node)
                self.move_to(self.pos)
                self.tail = node
                self.length += 1
                
    def connect(self,node:Node) -> AnimationGroup: 
        """Connects the sides of the current node"""
        anims = []
        if node.next and not node.arrow_next:
            node.arrow_next = Arrow(node.get_right(), node.next.get_left(), buff=0.1)
            self.add(node.arrow_next)
            anims.append(Create(node.arrow_next,run_time=0.7))
            
        if node.prev and self.doubly and not node.arrow_prev: #Creates an arrow if doubly can has prev arrow
            node.arrow_prev = Arrow(node.get_left(),node.prev.get_right())  
            self.add(node.arrow_prev)
            anims.append(Create(node.arrow_prev,run_time=0.7))
            
        return AnimationGroup(*anims,lag_ratio=0.2) if anims else None
    
    def disconnect(self,node:Node,direction:str = "next") -> AnimationGroup:
        """Disconnects the specified arrow of the current node\n
        Direction can either be 'prev', 'next', or 'both'
        """
        anims = []
        if direction == "next":
            arrow = node.arrow_next
            anims.append(Uncreate(arrow,runtime=0.7))
            node.arrow_next = None
            node.next = None
            
        elif direction == "prev" and self.doubly:
            arrow = node.arrow_prev
            anims.append(Uncreate(arrow,runtime=0.7))
            node.arrow_prev = None
            node.prev = None
            
        elif direction == "both" and self.doubly:
            next_arrow = node.arrow_next
            prev_arrow = node.arrow_prev
            anims.append(Uncreate(next_arrow,runtime=0.7))
            anims.append(Uncreate(prev_arrow,runtime=0.7))
            node.next = None
            node.prev = None
            
        else:
            raise ValueError(f"Invalid direction: '{direction}'")
        
        return AnimationGroup(*anims,lag_ratio=0.1)
        
    def append(self,data:any,recenter=True) -> AnimationGroup:
        
        node:Node = Node(value=data,scene=self.scene,width=self.node_width,height=self.node_height)
        
        
        if self.nodes:
            prev = self.tail
            prev.next = node #Make sure to handle .doubly as well later on
            node.next_to(self.tail.get_right(),buff = self.node_width * 0.7)
            arrow_anim = self.connect(prev)
        else:
            self.head = node
            self.tail = node
            node.move_to(self.pos)
            
        # arrow_anims = self.connect(self.tail) #This is needed because .create() only links
        
        
        self.add(node)
        self.nodes.append(node)
        self.tail = node
        node_anim = node.body.create()
        if recenter:
            self.move_to(self.pos)

        self.length += 1
        return AnimationGroup(node_anim,arrow_anim,lag_ratio=0.5)
    
                
    def create(self,nodes:list[Node] = None ) -> list[AnimationGroup]:
        """Creates the linked list, links arrows if they exist
        Returns a list where the first element is the node animations while the second one is the arrow animations
        """
        if nodes is None:
            nodes = self.nodes

        node_anims = [node.body.create() for node in nodes] #create nodes
        # arrow_anims = AnimationGroup(*[self.connect(node) for node in nodes if self.connect(node)],lag_ratio=0.1) #connect arrows
        arrow_anims = []
        for node in nodes:
            conn = self.connect(node)
            if conn:
                arrow_anims.append(conn)
                    
                    
        print(arrow_anims)
        # return [node_anims,arrow_anims] 
        return AnimationGroup(*node_anims, *arrow_anims, lag_ratio=0.2)
     
                    
        