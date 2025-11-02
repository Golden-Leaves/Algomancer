from typing import Any
import math
import numpy as np
from manim import *
from Components.animations import LazyAnimation, hop_element, slide_element
from Components.geometry import get_offset_position
from Components.logging import setup_logging
from Components.runtime import AlgoScene, is_animating
from Structures.base import VisualStructure,VisualElement
from Structures.pointers import Pointer
BRIGHT_GREEN = "#00FF00"

    
class Cell(VisualElement):
    """Visual representation of a single array slot with body + text managed together."""
    def __init__(self, value:Any,master:VisualStructure,
                cell_width:int=1, cell_height:int=1, text_color:ManimColor=WHITE,rounded=False,border=True,**kwargs):

        self.rounded = rounded
        corner_radius = 0.3 if rounded else 0
        self.body = (RoundedRectangle(width=cell_width, height=cell_height, corner_radius=corner_radius) if rounded else 
                Rectangle(width=cell_width, height=cell_height))
        self.body.set_fill(BLACK, opacity=0.5)
        if not border:
            self.body.set_stroke(opacity=0)
        self.value = value
        super().__init__(body=self.body,master=master,value=self.value,**kwargs)

        


        text_scale = 0.4 * cell_height / MathTex(0).height #38% of cell area
        self._base_text_color = text_color
        self.text = MathTex(value).set_color(text_color).scale(text_scale)
        self.text.move_to(self.body.get_center())
        self.text.add_updater(lambda m, body=self.body: m.move_to(body.get_center()))
        self.body.z_index = 0
        self.text.z_index = 1
        self.add(self.body, self.text)
        self._cell_height = cell_height
        self._cell_width = cell_width
        
    def create(self,runtime:float=0.5) -> AnimationGroup:
        return AnimationGroup(Create(self.body),Write(self.text),lag_ratio=runtime)

    def set_value(self, value: Any, *, color: ManimColor | None = None, runtime: float = 0.5) -> Transform:
        """Update the cell's stored value and return the corresponding text transform."""
        resolved = value.value if hasattr(value, "value") else value
        text_color = color or self._base_text_color
        text_scale = 0.45 * self._cell_height / MathTex(0).height
        new_text = MathTex(resolved).set_color(text_color).scale(text_scale)
        new_text.move_to(self.body.get_center())
        new_text.add_updater(lambda m, body=self.body: m.move_to(body.get_center()))
        self.value = resolved
        return Transform(self.text, new_text, run_time=runtime)

    def add_foreground_text(self):
        text = self.text.copy()
        

    # Ensure copies keep a valid text→body tracking updater
    def copy(self):
        clone = super().copy()
        if hasattr(clone, "text") and hasattr(clone, "body"):
            try:
                clone.text.clear_updaters()
            except Exception:
                pass
            clone.text.add_updater(lambda m, body=clone.body: m.move_to(body.get_center()))
        return clone

    def deepcopy(self):
        clone = super().deepcopy()
        if hasattr(clone, "text") and hasattr(clone, "body"):
            try:
                clone.text.clear_updaters()
            except Exception:
                pass
            clone.text.add_updater(lambda m, body=clone.body: m.move_to(body.get_center()))
        return clone
    
class VisualArray(VisualStructure):
    def __init__(self,data:Any,scene:AlgoScene|None=None,element_width:int=1,element_height:int=1,text_color:ManimColor=WHITE,
                label:str=None,
                **kwargs):
        """
        Initialize a VisualArray, a visual representation of an array using `Cell` objects.

        Parameters
        ----------
        data : list
            The initial values to populate the array with.
        scene : Scene
            The active Manim Scene the array belongs to(pass self here)
        element_width : float, optional
            Width for each rendered element.
        element_height : float, optional
            Height for each rendered element.
        text_color : Color, optional
            The color of the text inside each cell
        **kwargs :
            Additional positioning arguments.
            
            - pos : np.ndarray, optional  
              A 3D vector specifying where to center the array in the scene.  
              Example: `pos=RIGHT*3+UP*2`
            - x, y, z : float, optional  
              Coordinates for the array’s center if `pos` is not provided.  
              Defaults to ORIGIN on each axis.
        """
        self.logger = setup_logging(logger_name="algomancer.arrays",output=False)
        self._raw_data = data #The original structure the user passed in, maybe don't touch this beyond create()
        self.border = kwargs.pop("border",True)
        super().__init__(scene,label,**kwargs)
        self.rounded = kwargs.pop("rounded",False)
        self.text_color = text_color
        self.element_width = element_width
        self.element_height = element_height
        self._layout_proxy: Mobject | None = None
        self._instantialized = False
        self._iter_pointer = None

        self.logger.info(
            "array.init len=%d w=%s h=%s rounded=%s border=%s label=%s pos=%s",
            len(self._raw_data),
            element_width,
            element_height,
            self.rounded,
            self.border,
            label,
            np.array2string(self.pos, precision=2) if hasattr(self, "pos") else None,
        )
    def __repr__(self):
        return f"VisualArray({[element.value for element in self.elements]})"

            
    def __getitem__(self, index):
        self.log_event(_type="get",indices=[index],comment=f"Accessing index {index}")
        if isinstance(index, Pointer):
            return self.elements[index.value]
        
        if self.scene and is_animating() and not self.scene.in_play:#Dunders should only execute if a scene is passed(otherwise only log)
            anim = Succession(self.highlight(index,runtime=0.2),Wait(0.1),self.unhighlight(index,runtime=0.2))
            self.play(anim)
        return self.get_element(index)
    
    def __setitem__(self, index, value):
        self.log_event(_type="set",indices=[index],value=value,comment=f"Setting index {index} to value {value}")
        if self.scene and is_animating() and not self.scene.in_play:
            self.play(self.set_value(index=index,value=value))
        return 
    
    def __contains__(self,value):
        result = False
        target_val = value.value if hasattr(value, "value") else value
        for i in range(len(self)):
            cell:Cell = self.get_element(i)
            if self.scene and is_animating() and not self.scene.in_play: #Highlight cells that are looped through
                    animation = Succession(self.highlight(element=cell,color=YELLOW,runtime=0.15),
                                        Wait(0.1),
                                        self.unhighlight(element=cell,runtime=0.1),)
                    self.play(animation)
                    
            if target_val == cell.value:
                result = True
                scale =  1.15
                if self.scene and is_animating():
                    self.play(Succession(self.highlight(element=cell,color=GREEN,runtime=0.2),
                                        self.indicate(element=cell,color=GREEN,scale_factor=scale,runtime=0.2),
                                        Wait(0.1),
                                        self.unhighlight(element=cell,runtime=0.2)
                                        ))
                break
        self.log_event(_type="contains",value=value,result=result,comment=f"Find value {value} in array")
        return result
    
    def __iter__(self):
        self._iter_index = 0 #Index of the NEXT iteration
        return self

    def __next__(self):
        
        if not self._iter_pointer:
            self._iter_pointer = Pointer(value=self._iter_index,master=self,color=GRAY_B,direction=UP,size=0.7)
            self.play(self._iter_pointer.create())
            
        if self._iter_index >= len(self):
            self._iter_pointer.destroy()
            self._iter_pointer = None
            raise StopIteration
        
   
        cell = self.get_element(self._iter_index)
        if self.scene and is_animating() and not self.scene.in_play:
           anim = self._iter_pointer.move_pointer(old_index=self._iter_pointer.value,new_index=self._iter_index)
           self.play(anim)

        self._iter_index += 1
        return cell
    
    def sort(self, key=None, reverse=False,*args,**kwargs):
        """
        Sorts the VisualArray immediately (no animation).
        Only updates visuals to reflect the new order.
        """
        if self.scene and is_animating() and not self.scene.in_play:
            slots = [element.center for element in self.elements] #Snap shot the current positions of each index
            self.elements.sort(key= lambda el: el.value, reverse=reverse)
            for i, elem in enumerate(self.elements):

                elem.move_to(slots[i])
                
            self.submobjects = list(self.elements)
            print("Sorted elements: ",self.elements)
            self.log_event(
                _type="sort",
                comment=f"VisualArray sorted (reverse={reverse}, key={key is not None})"
            )
            self.play(Wait(0.1))
            return self
        else:
            return super().sort(*args,**kwargs)

          
    def set_value(self,index:int|Cell,value:Any) -> Succession|Transform:
        def build():
            cell:Cell = self.get_element(index)
            animation = cell.set_value(value, color=self.text_color)
            element_value = cell.value
            try:
                idx_num = self.get_index(cell)
            except Exception:
                idx_num = index if isinstance(index, int) else None
            self.logger.debug("array.set_value index=%s value=%s", idx_num, element_value)
            return animation
        return LazyAnimation(builder=build)
    
    def compare(self,index_1:int|Cell,index_2:int|Cell,result:bool=True,scalar=False) -> Succession:
        if scalar:
            return Wait(0)
        
        cell_1, cell_2 = self.get_element(index_1), self.get_element(index_2) 

        i1 = self.get_index(cell_1)
        i2 = self.get_index(cell_2)
        b1, t1 = getattr(cell_1, "body", None), getattr(cell_1, "text", None)
        b2, t2 = getattr(cell_2, "body", None), getattr(cell_2, "text", None)
        self.logger.debug(
            "array.compare.visual i=%s text_opacity=%s body_opacity=%s z_body=%s",
            i1,
            (
                t1.get_fill_opacity() if (t1 is not None and hasattr(t1, "get_fill_opacity"))
                else getattr(t1, "fill_opacity", None)
            ),
            getattr(b1, "fill_opacity", None),
            getattr(b1, "z_index", None),
        )
        self.logger.debug(
            "array.compare.visual j=%s text_opacity=%s body_opacity=%s z_body=%s",
            i2,
            (
                t2.get_fill_opacity() if (t2 is not None and hasattr(t2, "get_fill_opacity"))
                else getattr(t2, "fill_opacity", None)
            ),
            getattr(b2, "fill_opacity", None),
            getattr(b2, "z_index", None),
        )
        color = GREEN if result else RED
        scale = 1.08 if result else 1.15  # slightly larger pulse for "swap"   
        

        highlight = AnimationGroup(
            self.highlight(element=cell_1,color=color,runtime=0.2),
            self.highlight(element=cell_2,color=color,runtime=0.2)
        )  
        pulse = AnimationGroup(
            self.indicate(element=cell_1,scale_factor=scale,color=color,runtime=0.2),
            self.indicate(element=cell_2,scale_factor=scale,color=color,runtime=0.2),
        )
        unhighlight = AnimationGroup(
            self.unhighlight(element=cell_1,runtime=0.2),
            self.unhighlight(element=cell_2,runtime=0.2),
        )
        self.logger.debug("array.compare i=%s j=%s result=%s", index_1, index_2, result)
        return Succession(highlight,pulse,Wait(0.1),unhighlight)

               
    def shift_cell(self,from_idx:int,to_idx:int) -> LazyAnimation:
        """
        Move the cell at from_idx to to_idx,
        shifting all cells in between accordingly.
        """
        def build():
            self.logger.debug("array.shift_cell from=%s to=%s", from_idx, to_idx)
            anims = []
            step = -1 if from_idx > to_idx else 1 #If from_idx is larger than to_idx then shift right else shift left
            
            destination = self.get_element(to_idx).center
            key:Cell = self.get_element(from_idx)
            anims.append(hop_element(element=key))
            for i in range(from_idx + step,to_idx + step,step):
                cell:Cell = self.elements[i]
                prev:Cell = self.elements[i - step]
                anims.append(slide_element(element=cell,target_pos=prev.center))
                
            anims.append(slide_element(element=key,target_pos=destination))
            anims.append(ApplyMethod(key.move_to, destination, run_time=0.3))
            finalize:Wait = Wait(0)
            finish_animation = finalize.finish
            #https://docs.manim.community/en/stable/reference/manim.animation.composition.Succession.html#manim.animation.composition.Succession.finish
            def new_finish(): #Monkeypatches the .finish method of the current Wait instance
                finish_animation()
                shifted_cell = self.elements.pop(from_idx)
                self.elements.insert(to_idx,shifted_cell)

            finalize.finish = new_finish      
            return Succession(*anims,finalize)
        return LazyAnimation(builder=build)
    
            
        
            

    def move_cell(self,cell:int|Cell,target_pos,runtime=1,direction="up") -> Succession:
        """Moves specified cell to desired position"""
        cell:Cell = self.get_element(cell)
        try:
            idx = self.get_index(cell)
        except Exception:
            idx = None
        #Freeze vectors so later moves don't affect targets
        start = np.array(cell.center, dtype=float).copy()
        target_pos = np.array(target_pos, dtype=float).copy()
            
        
            
       
        
        # if bezier:
        #     ctrl1 = start + shift_vec * lift
        #     ctrl2 = target_pos + shift_vec * lift
        #     arc_path = CubicBezier(start,ctrl1,ctrl2,target_pos) #The cell lifts then moves in an arc to the desired location
        #     return MoveAlongPath(cell,arc_path,runtime=runtime)
        

        # hop_pos = start + shift_vec * (cell.body_height + lift) #Makes it go up by height
        hop_pos = get_offset_position(element=cell,direction=UP)

        x_shift = np.array([target_pos[0], hop_pos[1], start[2]])
        y_shift = np.array([target_pos[0], target_pos[1], start[2]])

        cell_shift = Succession(
            ApplyMethod(cell.move_to, hop_pos),
            ApplyMethod(cell.move_to, x_shift),
            ApplyMethod(cell.move_to, y_shift),
        )
        self.logger.debug("array.move_cell index=%s target=%s rt=%.2f", idx, np.array2string(target_pos, precision=2), runtime)
        return cell_shift
    
   
    
    def append(self,data,runtime=0.5,recenter=True) -> None:
        if not self._instantialized:
            self.create()
        cell = Cell(
            value=data,
            master=self,
            cell_width=self.element_width,
            cell_height=self.element_height,
            border=self.border,
        )

        last_cell:Cell = self.elements[-1] if self.elements else cell
        if self.elements:#If an array already exists
            right_side = last_cell.right
            right_vec = right_side / np.linalg.norm(right_side)
            cell.move_to(last_cell.right + right_vec * (last_cell.body_width / 2)) #Spawns next to last_cell   
        
        self.add(cell)
        self.elements.append(cell)
        self.create(cells=[cell])
        
       
        if recenter: 
            self.move_to(self.pos)
        self.logger.debug("array.append value=%s -> len=%d", data, len(self.elements))
        
    def extend(self,iterable) -> None:
        """Extend list by appending elements from the iterable"""
        if not hasattr(iterable,"__iter__"):
            raise TypeError("extend() argument must be iterable")
        for item in iterable:
            self.append(item)
            self.wait(0.05)
            
    def __delitem__(self, index: int | Cell) -> None:
        cell: Cell = self.get_element(index)
        idx = self.get_index(cell)
        if self.scene and is_animating() and not self.scene.in_play:
            self.pop(idx)
            return
        self.elements.pop(idx)
        self.logger.debug("array.del index=%s -> len=%d", idx, len(self.elements))

    def pop(self,index:int|Cell,runtime=0.5) -> Any:
        mid = len(self.elements) // 2
        popped_cell:Cell = self.get_element(index)

        anims = []
        anims.append(FadeOut(popped_cell))
        if index <= mid:
            for i in range(index - 1,-1,-1): #Shift cells to the right to fill up the popped cell
                cell:Cell = self.elements[i]
                prev:Cell = self.elements[i + 1]
                anims.append(slide_element(element=cell,target_pos=prev.center))
        else:
            for i in range(index + 1,len(self.elements)): #Shift cells to the left to fill up the popped cell
                cell:Cell = self.elements[i]
                prev:Cell = self.elements[i - 1]
                anims.append(slide_element(element=cell,target_pos=prev.center))
       
            
        self.play(*anims,runtime=runtime)    
        self.elements.pop(index)
        self.remove(popped_cell)
        self.logger.debug("array.pop index=%s -> len=%d", index, len(self.elements))
        
        return popped_cell.value
    
    def insert(self,data,index:int|Cell,runtime=0.5) -> None:

        self.append(data)
        self.play(self.shift_cell(from_idx=len(self.elements) - 1,to_idx=index))
        self.logger.debug("array.insert index=%s value=%s -> len=%d", index, data, len(self.elements))
        
    
    def swap(self, idx_1: VisualElement|int, idx_2: VisualElement|int, color=YELLOW, runtime=0.5) -> Succession:
        """
        Swaps two elements that may or may not be from different structures
        """
        if not isinstance(idx_1,(VisualElement,int)) or not isinstance(idx_2,(VisualElement,int)):
            print("swap() only accepts VisualElements or ints")
            raise TypeError

        cell_1 = idx_1 if isinstance(idx_1,VisualElement) else self.get_element(idx_1)
        cell_2 = idx_2 if isinstance(idx_2,VisualElement) else self.get_element(idx_2)
        idx_1 = idx_1.master.get_index(idx_1) if isinstance(idx_1,VisualElement) else idx_1
        idx_2 = idx_2.master.get_index(idx_2) if isinstance(idx_2,VisualElement) else idx_2

        # Freeze absolute targets so they don't drift when the first move runs
        pos_1 = np.array(cell_1.center, dtype=float).copy()
        pos_2 = np.array(cell_2.center, dtype=float).copy()
        self.logger.debug(
            "array.swap start i=%s j=%s pos_i=%s pos_j=%s",
            idx_1,
            idx_2,
            np.array2string(pos_1, precision=2),
            np.array2string(pos_2, precision=2),
        )


        move_1 = self.move_cell(cell_1, target_pos=pos_2.copy(), runtime=runtime)
        move_2 = self.move_cell(cell_2, target_pos=pos_1.copy(), runtime=runtime)

        # Defer the actual list swap until after animations complete to avoid
        # mid-flight lookups snapping elements back to their old slots.
        finalize = Wait(0)
        original_finish = finalize.finish

        def _finish_swap():
            original_finish()
            self.elements[idx_1], self.elements[idx_2] = self.elements[idx_2], self.elements[idx_1]
            self.logger.debug("array.swap finalize i=%s j=%s", idx_1, idx_2)

        finalize.finish = _finish_swap

        # return Succession(AnimationGroup(move_1, move_2, lag_ratio=0.2), finalize)
        return Succession(move_1,move_2,finalize,runtime=runtime)
    


    def create(self,cells:list[Cell]|int=None,runtime=0.5) -> AnimationGroup:
        """Creates the Cell object or index passed, defaults to creating the entire array"""
        if not self._instantialized:
            self.logger.debug(
                "array.create start len=%d pos=%s",
                len(self._raw_data),
                np.array2string(self.get_center(), precision=2),
            )
        if not self._instantialized:  # instantiate cell geometry without animation
            anchor = np.array(self.get_center())
            if not np.allclose(anchor, 0):
                self.pos = anchor
                
            for text in self._raw_data:
                cell = Cell(
                    value=text,
                    master=self,
                    cell_width=self.element_width,
                    cell_height=self.element_height,
                    text_color=self.text_color,
                    rounded=self.rounded,
                    border=self.border,
                )
                self.add(cell)
                self.elements.append(cell)
                
            for cell in self.elements:
                cell.set_opacity(0)
            self._instantialized = True
            
            if self.elements: #offset logic
                element_width = float(self.element_width)
                center_shift = (len(self.elements) - 1) / 2
                for idx, cell in enumerate(self.elements):
                    #Indexes lower than center_shift will go left, higher will go right
                    offset = (idx - center_shift) * element_width 
                    cell.move_to(self.pos + RIGHT * offset)
            self.move_to(self.pos)
            self.set_opacity(0)  
            
            if not self.scene:
                return None


        if not self.scene:
            return None

        #Update stored anchor to reflect any external positioning (e.g., arrange/shift)
        self.pos = np.array(self.get_center())
        self.set_opacity(1)

        if cells is None:
            cells:list[Cell] = self.elements
        if not cells:
            return Wait(1e-6)
        
        
        #AnimationGroup in here controls cell vs text behaviour
        runtime = max(0.5,runtime) #Stuff gets ugly if less than 0.5
        cell_anims = [cell.create(runtime=runtime) for cell in cells]
        
    
        return AnimationGroup( 
            *cell_anims,
            lag_ratio=0.1,
            runtime=runtime
        )

        
        
    



            
