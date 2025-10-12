from manim import *
from Structures.base import VisualStructure,VisualElement
from Utils.utils import get_offset_position,get_operation
from Utils.runtime import is_animating
class Pointer(VisualElement):
    _next_id = 0
    def __init__(self,value:int,master:VisualStructure,label:str = "",color=YELLOW,direction=UP,**kwargs):
        self.id = Pointer._next_id
        type(self)._next_id += 1 #Polymorphism-friendly, since it calls the class that inherited and not Pointer if that's the case
        super().__init__(label=label,value=value,master=master,**kwargs)
        self.color = color
        self.direction = direction
         
         
    def __hash__(self):
        return id(self)
    
    def _compare(self, other, op: str):
        """Internal unified comparison handler."""
        
        if isinstance(other, VisualElement):
            if op == "==":
                result = self.value == other.value
            elif op == "!=":
                result = self.value != other.value
            elif op == "<":
                result = self.value < other.value
            elif op == "<=":
                result = self.value <= other.value
            elif op == ">":
                result = self.value > other.value
            elif op == ">=":
                result = self.value >= other.value
            else:
                raise ValueError(f"Unsupported comparison operator: {op}")

            # Log and visualize
            self.master.log_event(_type="compare", other=other, result=result)
            return result
            
        elif isinstance(other, (int, float, str, bool)):
            if op == "==":
                return self.value == other
            elif op == "!=":
                return self.value != other
            elif op == "<":
                return self.value < other
            elif op == "<=":
                return self.value <= other
            elif op == ">":
                return self.value > other
            elif op == ">=":
                return self.value >= other
            else:
                raise ValueError(f"Unsupported comparison operator: {op}")

        return NotImplemented
  
    def __index__(self): return self.value
    def __int__(self): return self.value
    def __repr__(self): return f"Pointer({self.value})"

    
    def __eq__(self, other): return self._compare(other=other,op="==")
    def __ne__(self, other): return self._compare(other=other,op="!=")
    def __lt__(self, other): return self._compare(other=other,op="<")
    def __gt__(self, other): return self._compare(other=other,op=">")
    def __le__(self, other): return self._compare(other=other,op="<=")
    def __ge__(self, other): return self._compare(other=other,op=">=")
    
       
    def __add__(self, other: int):
        if not isinstance(other, int):
            return NotImplemented
        new_index = self.value + other
        anim = self.move_pointer(old_index=self.value, new_index=new_index)
        if self.master and self.master.scene and is_animating() and not self.master.scene.in_play:
            self.master.play(anim)
        return self

    def __sub__(self, other: int):
        if not isinstance(other, int):
            return NotImplemented
        new_index = self.value - other
        anim = self.move_pointer(old_index=self.value, new_index=new_index)
        if self.master and self.master.scene and is_animating() and not self.master.scene.in_play:
            self.master.play(anim)
        return self

    def __mul__(self, other: int):
        if not isinstance(other, int):
            return NotImplemented
        new_index = self.value * other
        anim = self.move_pointer(old_index=self.value, new_index=new_index)
        if self.master and self.master.scene and is_animating() and not self.master.scene.in_play:
            self.master.play(anim)
        return self

    def __floordiv__(self, other: int):
        if not isinstance(other, int):
            return NotImplemented
        if other == 0:
            raise ZeroDivisionError("Pointer floordiv by zero")
        new_index = self.value // other
        anim = self.move_pointer(old_index=self.value, new_index=new_index)
        if self.master and self.master.scene and is_animating() and not self.master.scene.in_play:
            self.master.play(anim)
        return self

    def __mod__(self, other: int):
        if not isinstance(other, int):
            return NotImplemented
        if other == 0:
            raise ZeroDivisionError("Pointer modulo by zero")
        new_index = self.value % other
        anim = self.move_pointer(old_index=self.value, new_index=new_index)
        if self.master and self.master.scene and is_animating() and not self.master.scene.in_play:
            self.master.play(anim)
        return self



    def __iadd__(self, other: int):
        if not isinstance(other, int):
            return NotImplemented
        new_index = self.value + other
        if self.master and self.master.scene and is_animating() and not self.master.scene.in_play:
            anim = self.move_pointer(old_index=self.value, new_index=new_index)
            self.master.play(anim)
        self.value += other
        return self

    def __isub__(self, other: int):
        if not isinstance(other, int):
            return NotImplemented
        new_index = self.value - other
        if self.master and self.master.scene and is_animating() and not self.master.scene.in_play:
            anim = self.move_pointer(old_index=self.value, new_index=new_index)
            self.master.play(anim)
        self.value -= other
        return self

    def __imul__(self, other: int):
        if not isinstance(other, int):
            return NotImplemented
        new_index = self.value * other
        if self.master and self.master.scene and is_animating() and not self.master.scene.in_play:
            anim = self.move_pointer(old_index=self.value, new_index=new_index)
            self.master.play(anim)
        self.value *= other
        return self

    def __ifloordiv__(self, other: int):
        if not isinstance(other, int):
            return NotImplemented
        if other == 0:
            raise ZeroDivisionError("Pointer floordiv by zero")
        new_index = self.value // other
        if self.master and self.master.scene and is_animating() and not self.master.scene.in_play:
            anim = self.move_pointer(old_index=self.value, new_index=new_index)
            self.master.play(anim)
        self.value //= other
        return self

    def __imod__(self, other: int):
        if not isinstance(other, int):
            return NotImplemented
        if other == 0:
            raise ZeroDivisionError("Pointer modulo by zero")
        new_index = self.value % other
        if self.master and self.master.scene and is_animating() and not self.master.scene.in_play:
            anim = self.move_pointer(old_index=self.value, new_index=new_index)
            self.master.play(anim)
        self.value %= other
        return self
    
        
    
    def create(self):
        master_element:VisualElement = self.master[self.value]
    
        arrow_end = get_offset_position(master_element, direction=self.direction,buff=0.05)
        arrow_start = get_offset_position(master_element,coordinate=arrow_end, direction=self.direction)
    
        self.body = Arrow(arrow_start, arrow_end, buff=0.1, stroke_width=master_element.body_width * 0.45)

        # Label positioned near tail
        text_scale = self.body.stroke_width * 0.8
        self.label = Text(self.label).scale(text_scale)
        self.label.next_to(self.body, self.direction, buff=0.15).align_to(self.body, ORIGIN)
        self.label.add_updater(
    lambda m: m.next_to(self.body, self.direction, buff=0.15).align_to(self.body, ORIGIN)
)
        self.add(self.body,self.label)

        return AnimationGroup(Create(self.body),Write(self.label),lag_ratio=0.2)
        
    def move_pointer(self,old_index:int,new_index:int):
        if isinstance(new_index,Pointer):
            new_index = new_index.value
        old_master_element = self.master.get_element(old_index)
        master_element:VisualElement = self.master.get_element(new_index)
        old_pos = get_offset_position(old_master_element, direction=self.direction,buff=0.05)
        new_pos = get_offset_position(master_element, direction=self.direction,buff=0.05)
        arrow_pos = new_pos - old_pos
        
        return ApplyMethod(self.shift,arrow_pos)