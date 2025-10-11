from manim import *
from Structures.base import VisualStructure,VisualElement
from Utils.utils import get_offset_position
from Utils.runtime import is_animating
class Pointer(VisualElement):
    _next_id = 0
    def __init__(self,value:int,master:VisualStructure,label:str = "",color=YELLOW,direction=UP,**kwargs):
        self.id = Pointer._next_id
        Pointer._next_id += 1
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
    
        # ─────────── In-place arithmetic ───────────
    def __iadd__(self, other: int):
        if not isinstance(other, int):
            return NotImplemented
        new_index = self.value + other
        print("Before play()")
        
        print("After play()")
        if self.master and self.master.scene and is_animating():
            anim = self.move_pointer(old_index=self.value,index=new_index)   # self.value == current index
            self.master.play(anim)
        self.value += other
        return self

    def __isub__(self, other: int):
        if not isinstance(other, int):
            return NotImplemented
        anim = self.move_pointer(self.value - other)
        if self.master and self.master.scene and is_animating():
            self.master.play(anim)
        return self

    # (Optionally) override __add__/__sub__ to just move and return self:
    def __add__(self, other: int):
        return self.__iadd__(other)
    def __sub__(self, other: int):
        return self.__isub__(other)

  
    
    
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
        
    def move_pointer(self,old_index:int,index:int):
        # if isinstance(index,Pointer):
        #     index = index.index
        print("Move Pointer:",type(index))
        old_master_element = self.master.get_element(old_index)
        master_element:VisualElement = self.master.get_element(index)
        old_pos = get_offset_position(old_master_element, direction=self.direction,buff=0.05)
        new_pos = get_offset_position(master_element, direction=self.direction,buff=0.05)
        arrow_pos = new_pos - old_pos
        # if self.direction in (UP,DOWN):#Move to target's x
        #     new_pos = np.array([master_element.center[0], arrow_pos[1], 0])
        
        # elif self.direction in ("left", "right"): #Move to target's y
        #     new_pos = np.array([arrow_pos[0], master_element.center[1], 0])
        # else:
        #     raise ValueError(f"Invalid direction: {self.direction}")
        return ApplyMethod(self.shift,arrow_pos)