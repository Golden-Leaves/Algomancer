from manim import *
from Structures.base import VisualStructure,VisualElement
from Utils.utils import get_offset_position,get_operation
from Utils.runtime import is_animating
import numpy as np
class Pointer(VisualElement):
    """
    A logical and visual reference marker for navigating within a structure.

    The `Pointer` represents an index inside a `VisualStructure` such as a
    `VisualArray`. It behaves like an integer reference for logical operations,
    but also manifests as a Manim object that can move, highlight, and 
    animate transitions between elements. 

    You can also instantiate a `Pointer()` instance like `i = Pointer(...)`, useful for stuff like two pointers

    Parameters
    ----------
    value : int
        The initial index or logical position of the pointer.
    master : VisualStructure | None
        The parent object (e.g., `VisualArray`) this pointer belongs to.
    label : str | None
        Optional textual label rendered above the pointer.
    direction : np.ndarray
        The Manim direction vectors (e.g., `UP`, `DOWN`, `LEFT`, `RIGHT`) 
    """
    _next_id = 0
    def __init__(self,value:int,master:VisualStructure,label:str = "",color=YELLOW,direction:np.ndarray=UP,**kwargs):
        self.id = Pointer._next_id
        self.size = kwargs.pop("size",1)
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
    def __repr__(self) -> str:
          """Human-friendly pointer debug string."""
          master = self.master
          scene = getattr(master, "scene", None)
          animating = bool(scene and is_animating() and not scene.in_play)
          label = f' label="{self.label}"' if self.label else ""

          return f"<Pointer id={self.id} idx={self.value}{label} master={master}>"
    def __str__(self):
        return self.__repr__()

    
    def __eq__(self, other): return self._compare(other=other,op="==")
    def __ne__(self, other): return self._compare(other=other,op="!=")
    def __lt__(self, other): return self._compare(other=other,op="<")
    def __gt__(self, other): return self._compare(other=other,op=">")
    def __le__(self, other): return self._compare(other=other,op="<=")
    def __ge__(self, other): return self._compare(other=other,op=">=")
    
    def _apply_pointer_op(self, other: int, op: str):
        if not isinstance(other, int):
            return NotImplemented
        operation = get_operation(op=op)
        new_index = operation(self.value, other)

        if self.master and self.master.scene and is_animating() and not self.master.scene.in_play:
            anim = self.move_pointer(old_index=self.value, new_index=new_index)
            self.master.play(anim)
            return self
        return new_index
       
    def __add__(self, other: int):
        return self._apply_pointer_op(other, "+")
   
   
    def __sub__(self, other: int):
        return self._apply_pointer_op(other, "-")

    def __mul__(self, other: int):
        return self._apply_pointer_op(other, "*")

    def __floordiv__(self, other: int):
        if not isinstance(other, int):
            return NotImplemented
        if other == 0:
            raise ZeroDivisionError("Pointer floordiv by zero")
        return self._apply_pointer_op(other, "//")

    def __mod__(self, other: int):
        if not isinstance(other, int):
            return NotImplemented
        if other == 0:
            raise ZeroDivisionError("Pointer modulo by zero")
        return self._apply_pointer_op(other, "%")



    def __iadd__(self, other: int):
        result = self._apply_pointer_op(other, "+")
        if result is NotImplemented:
            return NotImplemented
        if isinstance(result, type(self)):
            return result
        self.value = result
        return result

    def __isub__(self, other: int):
        result = self._apply_pointer_op(other, "-")
        if result is NotImplemented:
            return NotImplemented
        if isinstance(result, type(self)):
            return result
        self.value = result
        return result


    def __imul__(self, other: int):
        result = self._apply_pointer_op(other, "*")
        if result is NotImplemented:
            return NotImplemented
        if isinstance(result, type(self)):
            return result
        self.value = result
        return result


    def __itruediv__(self, other: int):
        result = self._apply_pointer_op(other, "/")
        if result is NotImplemented:
            return NotImplemented
        if isinstance(result, type(self)):
            return result
        self.value = result
        return result


    def __ifloordiv__(self, other: int):
        if not isinstance(other, int):
            return NotImplemented
        if other == 0:
            raise ZeroDivisionError("Pointer floordiv by zero")
        result = self._apply_pointer_op(other, "//")
        if isinstance(result, type(self)):
            return result
        self.value = result
        return result
    
        
    
    def create(self):
        master_element:VisualElement = self.master.get_element(self.value)
    
        arrow_end = get_offset_position(master_element, direction=self.direction,buff=0.05)
        arrow_start = get_offset_position(master_element,coordinate=arrow_end, direction=self.direction)
    
        self.body = Arrow(arrow_start, arrow_end, buff=0.1, stroke_width=master_element.body_width * 0.45,color=self.color)
        self.body.scale(self.size,about_point=arrow_end)
        # Label positioned near start
        text_scale = self.body.stroke_width * 0.8
        self.label = Text(self.label).scale(text_scale)
        self.label.next_to(self.body, self.direction, buff=0.15).align_to(self.body, ORIGIN)
        self.label.add_updater(
    lambda m: m.next_to(self.body, self.direction, buff=0.15).align_to(self.body, ORIGIN)
)
        self.add(self.body,self.label)

        return AnimationGroup(Create(self.body),Write(self.label),lag_ratio=0.2)
        
    def move_pointer(self,old_index:int,new_index:int):
        old_index = old_index.value if isinstance(old_index,VisualElement) else old_index
        new_index = new_index.value if isinstance(new_index,VisualElement) else new_index
        old_master_element = self.master.get_element(old_index)
        master_element:VisualElement = self.master.get_element(new_index)
        old_pos = get_offset_position(old_master_element, direction=self.direction,buff=0.05)
        new_pos = get_offset_position(master_element, direction=self.direction,buff=0.05)
        arrow_pos = new_pos - old_pos
        
        anim = ApplyMethod(self.shift, arrow_pos)
        self.value = new_index
        return anim
    
    def destroy(self):
        if self.master and self.master.scene and is_animating() and not self.master.scene.in_play:
            self.master.play(FadeOut(self))
        self.clear_updaters()
        self.label = None
        self.body = None
        self.become(VGroup())  # clears content, removing the pointer normally doens't work? Itll just reappear later
    
class PointerRange:
    """
    `PointerRange` emulates Python's built-in `range`, but instead of yielding
    raw integers, it moves and returns a single live `Pointer` object
    
    It will behave just like `range` if `master` is not passed
    
    Each iteration updates the pointer's visual and logical position
    
    Parameters
    ----------
    start : int
        Starting index (inclusive). Behaves identically to `range(start, stop)`.
    stop : int | None
        Stopping index (exclusive)
    step : int
        Increment per iteration. Defaults to 1.
    master : VisualStructure | None
        The parent container (e.g., `VisualArray`) that manages the pointer, acts like a normal iterator if not passed
    label : str | None
        Optional label for the pointer during iteration.
    """
    def __init__(self,start,stop=None,step:int=1,master:VisualStructure=None,label:str=None,**kwargs):
        if stop is None:
            stop = start
            start = 0
        self.start = start.value if isinstance(start,VisualElement) else start
        self.stop = stop.value if isinstance(stop,VisualElement) else stop
        self.step = step.value if isinstance(step,VisualElement) else step
        self.master = master
        self.label = label
        self._current = start.value if isinstance(start,VisualElement) else start
        self.direction = kwargs.get("direction",UP)
        
        self._started = False #Checks if iteration ahs started yet(logic in __next__)
        # self.pointer:Pointer = Pointer(value=start,master=master,label=label,direction=self.direction)
        color = kwargs.get("color",YELLOW)
        if (step > 0 and start < stop) or (step < 0 and start > stop): #Checks if the direction is valid
            self.pointer:Pointer = Pointer(value=start,master=master,label=label,direction=self.direction,color=color)
        else:
            self.pointer = None
            
        
    def __iter__(self): #This returns an iterator
        return self
    
    #A for loop basically calls range().__iter__(), and the i gets assigned i = next(range().__iter__())
    #Then i gets updated over and over until StopIteration is raised
    def __next__(self):
        if self.pointer is None:
            raise StopIteration
        #Just yield the pointer on first iteration, since smth like range(0,5,10) would still return the start if valid direction
        if not self._started: 
            if getattr(self.pointer, "body", None) is None and self.master:
                self.master.play(self.pointer.create())
                
            self._started = True
            self.pointer.value = self._current     
            return self._current
        
        old_index = self._current
        next_index = old_index + self.step

        if (self.step > 0 and next_index >= self.stop) or (self.step < 0 and next_index <= self.stop): #Cant iterate further
          
            self.pointer.destroy()
            self.pointer = None
            raise StopIteration

        self._current = next_index

        if self.master and self.master.scene and is_animating() and not self.master.scene.in_play:
            anim = self.pointer.move_pointer(old_index=old_index, new_index=next_index)
            self.master.play(anim)



        return self._current
    
    

    def __repr__(self):
        return f"PointerRange({self.start}, {self.stop}, step={self.step})"
