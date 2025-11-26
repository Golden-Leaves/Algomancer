from typing import Any,Generic,TypeVar
import math
import numpy as np
from manim import *
from Components.animations import LazyAnimation, hop_element, slide_element
from Components.geometry import get_offset_position
from Components.logging import DebugLogger
from Components.runtime import AlgoScene, is_animating
from Structures.base import VisualStructure,VisualElement
from Structures.pointers import Pointer
BRIGHT_GREEN = "#00FF00"
T = TypeVar("T")
    
class Cell(VisualElement):
    """
        A Cell, a rectangle and a fundamental visual building-block.

        Parameters
        ----------
        value : Any
            The value represented by the cell.
        master : VisualStructure
            Owning structure (typically the `VisualArray`) responsible for playback/logging.
        cell_width : int, optional
            Width for the cell.
        cell_height : int, optional
            Height for the cell.
        text_color : ManimColor, optional
            Color of the rendered text.
        text_size : float, optional
            Scales the rendered text relative to its original size.
        rounded : bool, optional
            If True, the cell will be rendered with rounded corners.
        border : bool, optional
            If False, the cell will not have a border.
        **kwargs :
            Additional positioning arguments.

        Notes
        -----
        - The cell is rendered with a black background and white text by default.
        - The cell's text is centered within the cell's body.
        """

    def __init__(self, value:Any,master:VisualStructure,
                cell_width:int=1, cell_height:int=1, text_color:ManimColor=WHITE, text_size:float=1.0,
                rounded=False,border=True,
                **kwargs):
        self.rounded = rounded
        corner_radius = 0.3 if rounded else 0
        self.body = (RoundedRectangle(width=cell_width, height=cell_height, corner_radius=corner_radius) if rounded else 
                Rectangle(width=cell_width, height=cell_height))
        self.body.set_fill(BLACK, opacity=1.0)
        if not border:
            self.body.set_stroke(opacity=0)
        self.value = value
        super().__init__(body=self.body,master=master,value=self.value,**kwargs)

        
        self.text = MathTex(value).set_color(text_color)
        pad_w = 0.75 
        pad_h = 0.75
        text_scale = min(pad_w * (cell_width / self.text.height), pad_h * (cell_height / self.text.width)) #pad * old_ratio = new_ratio
        self.text.scale(text_scale * text_size)
        self._base_text_color = text_color
        self.text.move_to(self.body.get_center())
        self.text.add_updater(lambda m, body=self.body: m.move_to(body.get_center()))
        self.body.z_index = 0
        self.text.z_index = 1
        self.add(self.body, self.text)
        self._cell_height = cell_height
        self._cell_width = cell_width
        
    def create(self,runtime:float=0.5) -> AnimationGroup:
        return AnimationGroup(Create(self.body),Write(self.text),lag_ratio=runtime)

    def set_value(self, value: Any, *, text_color:ManimColor,text_size:float, runtime: float = 0.5) -> Transform:
        """Update the cell's stored value and return the corresponding text transform."""
        resolved = value.value if hasattr(value, "value") else value
        text_color = text_color or self.text_color
        text_size = text_size or self.text_size
        pad_w = 0.75 
        pad_h = 0.75 
        text_scale = min(pad_w * (self._cell_width / self.text.width), pad_h * (self._cell_height / self.text.height)) #pad * old_ratio = new_ratio
        new_text = MathTex(resolved).set_color(text_color).scale(text_scale * self.text_size)
        new_text.move_to(self.body.get_center())
        new_text.add_updater(lambda m, body=self.body: m.move_to(body.get_center()))
        self.value = resolved
        return Transform(self.text, new_text, run_time=runtime)

    def add_foreground_text(self):
        text = self.text.copy()
        

    #Ensure copies keep a valid text -> body tracking updater
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
class VisualArray(VisualStructure,Generic[T]):
    def __init__(self,data:Any,scene:AlgoScene=None,element_width:int=1,element_height:int=1,
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
        self.logger = DebugLogger(logger_name=__name__, output=False)
        self._raw_data = data if isinstance(data, list) else list(data) #The original structure the user passed in, maybe don't touch this beyond create()
        self.border = kwargs.pop("border",True)
        super().__init__(scene,label,**kwargs)
        self.rounded = kwargs.pop("rounded",False)
        self.element_width = element_width
        self.element_height = element_height
        self._instantiated = False
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
        self.logger.debug("__getitem__ at index=%s",index)
        if isinstance(index, Pointer):
            return self.get_element(index.value).value
        if self.scene and is_animating() and not self.scene.in_play:#Dunders should only execute if a scene is passed(otherwise only log)
            #A weird text dimming bug will occur if we use Succession or AnimationGroup
            self.play([self.highlight(index,runtime=0.4),self.unhighlight(index,runtime=0.3)]) 
        return self.get_element(index).value
    
    def __setitem__(self, index, value):
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
            slots = [element.get_center() for element in self.elements] #Snap shot the current positions of each index
            self.elements.sort(key= lambda el: el.value, reverse=reverse)
            for i, elem in enumerate(self.elements):

                elem.move_to(slots[i])
                
            self.submobjects = list(self.elements)
            print("Sorted elements: ",self.elements)
            self.play(Wait(0.1))
            return self
        else:
            return super().sort(*args,**kwargs)

          
    def set_value(self,index:int|Cell,value:Any) -> Succession|Transform:
        """Update the value cell for ``index`` and animate the change when possible.
        
        Args:
            index (int or Cell): Index of the cell to update or the Cell object itself.
            value (Any): New value to set for the cell.
            
        Returns:
            Succession or Transform: Animation to update the cell's value.
        """
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

    def shift_cell(self,from_idx:int,to_idx:int) -> LazyAnimation:
        """
        Move the cell at from_idx to to_idx,
        shifting all cells in between accordingly.
        """
        def build():
            self.logger.debug("array.shift_cell from=%s to=%s", from_idx, to_idx)
            anims = []
            step = -1 if from_idx > to_idx else 1 #If from_idx is larger than to_idx then shift right else shift left
            
            destination = self.get_element(to_idx).get_center()
            key:Cell = self.get_element(from_idx)
            anims.append(hop_element(element=key))
            for i in range(from_idx + step,to_idx + step,step):
                cell:Cell = self.elements[i]
                prev:Cell = self.elements[i - step]
                anims.append(slide_element(element=cell,target_pos=prev.get_center()))
                
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
    
            
        
            

    def move_cell(self, cell: int | Cell, target_position: np.ndarray, runtime: float = 1.0, direction = UP) -> Succession:
        """Moves specified cell to desired position"""
        cell_element = self.get_element(cell)
        start_position = np.array(cell_element.get_center(), dtype=float).copy()
        target_position = np.array(target_position, dtype=float).copy()

        hop_position = get_offset_position(element=cell_element, direction=direction)
        x_shift_position = np.array([target_position[0], hop_position[1], start_position[2]])
        y_shift_position = np.array([target_position[0], target_position[1], start_position[2]])

        cell_shift = Succession(
            ApplyMethod(cell_element.move_to, hop_position),
            ApplyMethod(cell_element.move_to, x_shift_position),
            ApplyMethod(cell_element.move_to, y_shift_position),
        )
        return cell_shift
    
    def move_to(self, target_position: np.ndarray,run_time:float=1.0) -> None:
        """Moves all elements in the array to the desired position.

        Parameters
        ----------
        target_position : np.ndarray
            The desired position for the center of the array.

        Returns
        -------
        None
        """
        from Structures.base import _COMPARE_GUARD
        token = _COMPARE_GUARD.set(True)
        try:
            target_position = target_position.copy()
            cell_shifts = []
            for i, element in enumerate(self.elements):
                center_shift = (len(self.elements)-1)/2
                cell_target_position = [target_position[0] + (i - center_shift),target_position[1],target_position[2]]
                cell_shift = ApplyMethod(element.move_to, cell_target_position,run_time=run_time)
                cell_shifts.append(cell_shift)
            self.play(cell_shifts)
        finally:
            _COMPARE_GUARD.set(token)
    
   
    
    def append(self,data:Any|VisualElement,runtime=0.5,recenter=True) -> None:
        """Appends an element to the array.

        Parameters
        ----------
        data : Any | VisualElement
            The value to append to the array.
        runtime : float, optional
            The runtime of the animation.
        recenter : bool, optional
            Whether to recenter the array after appending.

        Returns
        -------
        None
        """
        data_value = data.value if isinstance(data,VisualElement) else data
        self.logger.debug("data_type=%s data_value=%s",type(data),data_value)
        before_move = self.get_center()
        if not self._instantiated:
            self.play(self.create())
        if isinstance(data,VisualElement):
            data:VisualElement = data.value
        cell = Cell(
            value=data,
            master=self,
            cell_width=self.element_width,
            cell_height=self.element_height,
            border=self.border,
            text_color=self.text_color,
            text_size=self.text_size,
        )

        last_cell:Cell = self.elements[-1] if self.elements else cell
        
        if self.elements:
            cell_position = get_offset_position(element=last_cell,direction=RIGHT,buff=0.5)
        else:
            cell_position = self.pos
            
        cell.move_to(cell_position)
        
        self.add(cell)
        self.elements.append(cell)
        self.play(self.create(cells=[cell]))
        self.logger.debug("Elements after append: %s",self.elements)
        
       
        if recenter:
            self.move_to(before_move)
            
        self.logger.debug("array.append value=%s -> len=%d", data, len(self.elements))
        
    def extend(self,iterable,recenter=True) -> None:
        """Extend list by appending elements from the iterable"""
        if not hasattr(iterable,"__iter__"):
            raise TypeError("extend() argument must be iterable")
        for item in iterable:
            self.append(item,recenter=recenter)
            self.wait(0.05)
            
    def __delitem__(self, index: int | Cell) -> None:
        cell: Cell = self.get_element(index)
        idx = self.get_index(cell)
        if self.scene and is_animating() and not self.scene.in_play:
            self.pop(idx)
            return
        self.elements.pop(idx)
        self.logger.debug("array.del index=%s -> len=%d", idx, len(self.elements))

    def pop(self,index:int|Cell=-1,runtime=0.5) -> Any:
        """Removes and returns the element at the given index.

        Animates the popping and shifting of cells to fill up the popped cell.

        Parameters
        ----------
        index : int | Cell
            The index or cell to pop.
        runtime : float, optional
            The runtime of the animation.

        Returns
        -------
        Any
            The popped cell's value.
        """
        mid = len(self.elements) // 2
        popped_cell:Cell = self.get_element(index)
      
        anims = []
        anims.append(FadeOut(popped_cell))
        if index <= mid:
            for i in range(index - 1,-1,-1): #Shift cells to the right to fill up the popped cell
                cell:Cell = self.elements[i]
                prev:Cell = self.elements[i + 1]
                anims.append(slide_element(element=cell,target_pos=prev.get_center()))
        else:
            for i in range(index + 1,len(self.elements)): #Shift cells to the left to fill up the popped cell
                cell:Cell = self.elements[i]
                prev:Cell = self.elements[i - 1]
                anims.append(slide_element(element=cell,target_pos=prev.get_center()))
       
            
        self.play(*anims,runtime=runtime)    
        self.elements.pop(index)
        self.remove(popped_cell)
        popped_cell.become(VGroup())
        self.logger.debug("array.pop index=%s -> len=%d", index, len(self.elements))
        
        return popped_cell.value
    
    def insert(self,data,index:int|Cell) -> None:
        self.append(data)
        self.play(self.shift_cell(from_idx=len(self.elements) - 1,to_idx=index))
        self.logger.debug("array.insert index=%s value=%s -> len=%d", index, data, len(self.elements))
        
    
    def swap(self, idx_1: VisualElement|int, idx_2: VisualElement|int, color=YELLOW, runtime=0.5) -> Succession:
        """Swaps two elements that may or may not be from different structures"""
        if not isinstance(idx_1, (VisualElement, int)) or not isinstance(idx_2, (VisualElement, int)):
            raise TypeError("swap() only accepts VisualElements or ints")

        cell_1 = self.get_element(idx_1) if isinstance(idx_1, int) else idx_1
        cell_2 = self.get_element(idx_2) if isinstance(idx_2, int) else idx_2

        idx_1 = cell_1.master.get_index(cell_1) if isinstance(idx_1, VisualElement) else idx_1
        idx_2 = cell_2.master.get_index(cell_2) if isinstance(idx_2, VisualElement) else idx_2

        pos_1 = np.array(cell_1.get_center(), dtype=float).copy()
        pos_2 = np.array(cell_2.get_center(), dtype=float).copy()

        move_1 = self.move_cell(cell_1, target_position=pos_2.copy(), runtime=runtime)
        move_2 = self.move_cell(cell_2, target_position=pos_1.copy(), runtime=runtime)

        finalize = Wait(0)

        def _finish_swap():
            finalize.finish()
            self.elements[idx_1], self.elements[idx_2] = self.elements[idx_2], self.elements[idx_1]

        finalize.finish = _finish_swap

        return Succession(move_1, move_2, finalize, runtime=runtime)
    


    def create(self, cells: list[Cell] | None = None, runtime: float = 0.5) -> AnimationGroup:
        """Creates the Cell object or index passed, defaults to creating the entire array"""
        def instantiate(raw_data: list[Any], position: np.ndarray) -> None:
            """
            Instantiates the VisualArray from raw data.

            Parameters
            ----------
            raw_data : list[Any]
                A list of values to populate the array with.
            position : np.ndarray
                The position of the array in the scene.
            """
            for text in raw_data:
                cell: Cell = Cell(
                    value=text,
                    master=self,
                    cell_width=self.element_width,
                    cell_height=self.element_height,
                    rounded=self.rounded,
                    border=self.border,
                    text_color=self.text_color,
                    text_size=self.text_size
                )
                self.add(cell)
                self.elements.append(cell)

            self._instantiated = True

            if self.elements:
                element_width = float(self.element_width)
                center_shift = (len(self.elements) - 1) / 2
                for idx, cell in enumerate(self.elements):
                    offset = (idx - center_shift) * element_width #Distribute cells evenly based on a center point
                    cell.move_to(position + RIGHT * offset)
            super(VisualArray, self).move_to(position)


        if not self._instantiated:
            instantiate(raw_data=self._raw_data, position=self.pos)

        if not self.scene:
            return None

        self.pos = np.array(self.get_center()) #Update anchor in case it moved

        if cells is None:
            cells = self.elements
        if not cells:
            return Wait(1e-6)

        cell_anims = [cell.create(runtime=runtime) for cell in cells]

        return AnimationGroup(*cell_anims, lag_ratio=0.1, runtime=runtime)

        
        
    



            
