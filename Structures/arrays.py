from manim import *
import numpy as np
import math
from Utils.utils import LazyAnimation,get_offset_position
from Structures.base import VisualStructure,VisualElement
from Structures.pointer import Pointer
from Utils.runtime import is_animating,AlgoScene
BRIGHT_GREEN = "#00FF00"

    
class Cell(VisualElement):
    def __init__(self, value:any,master:VisualStructure,
                cell_width:int=1, cell_height:int=1, text_color:ManimColor=WHITE,rounded=False,**kwargs):

        self.rounded = rounded
        corner_radius = 0.3 if rounded else 0
        self.body = (RoundedRectangle(width=cell_width, height=cell_height, corner_radius=corner_radius) if rounded else 
                Rectangle(width=cell_width, height=cell_height))
        self.body.set_fill(color=BLACK, opacity=0)
        self.value = value
        super().__init__(body=self.body,master=master,value=self.value,**kwargs)

        
        # Create the text inside

        text_scale = 0.4 * cell_height / MathTex("0").height #38% of cell area
        self.text = MathTex(str(value)).set_color(text_color).scale(text_scale)
        self.text.move_to(self.get_center())
        self.text.add_updater(lambda m: m.move_to(self.get_center()))
        
        self.add(self.body, self.text)

        
        
    
class VisualArray(VisualStructure):
    def __init__(self,data:any,scene:AlgoScene|None=None,cell_width:int=1,cell_height:int=1,text_color:ManimColor=WHITE,
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
        cell_width : float, optional
            The side length of each square `Cell`
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
       
    
        super().__init__(scene,label,**kwargs)
        self.rounded = kwargs.pop("rounded",False)
        self.text_color = text_color
        # self.elements:list[Cell] = []
        self.cell_width = cell_width
        self.cell_height = cell_height
        if data:

            for idx,text in enumerate(data):
                    
                    cell = Cell(value=text,master=self,cell_width=self.cell_width,cell_height=self.cell_height,
                                text_color=text_color,rounded=self.rounded)
                    if idx == 0:
                        cell.move_to(self.pos)
                        cell.master = self
                    else:
                        cell.next_to(self.elements[idx - 1],RIGHT,buff=0)
                        
                    
                    # self.add(cell)          
                    self.elements.append(cell)
            self.move_to(self.pos)

            
    def __getitem__(self, index):
        self.log_event(_type="get",indices=[index],comment=f"Accessing index {index}")
        if isinstance(index, Pointer):
            return self.elements[index.index]
        
        if self.scene and is_animating() and self.scene.in_play:#Dunders should only execute if a scene is passed(otherwise only log)
         self.play(self.highlight(index))
        return self.get_element(index)
    
    def __setitem__(self, index, value):
        self.log_event(_type="set",indices=[index],value=value,comment=f"Setting index {index} to value {value}")
        if self.scene and is_animating() and not self.scene.in_play:
            self.play(self.set_value(index=index,value=value))
        return 
    
    def __len__(self):
        return len(self.elements)
    
    def __contains__(self,value):
        result = False
        target_val = value.value if hasattr(value, "value") else value
        for i in range(len(self)):
            cell:Cell = self.get_element(i)
            if self.scene and is_animating() and not self.scene.in_play: #Highlight cells that are looped through
                    animation = Succession(self.highlight(cell=cell,color=YELLOW,runtime=0.15),
                                        Wait(0.1),
                                        self.unhighlight(cell=cell,runtime=0.1),)
                    self.play(animation)
            if target_val == cell.value:
                result = True
                scale =  1.15
                if self.scene and is_animating():
                    self.play(Succession(self.highlight(cell=cell,color=GREEN,runtime=0.2),
                                        Indicate(cell,color=GREEN,scale_factor=scale),
                                        Wait(0.1),
                                        self.unhighlight(cell=cell,runtime=0.2)
                                        ))
                break
        self.log_event(_type="contains",value=value,result=result,comment=f"Find value {value} in array")
        return result
    def __iter__(self):
        self._iter_index = 0
        return self

    def __next__(self):
        if self._iter_index >= len(self):
            raise StopIteration

        cell: Cell = self.elements[self._iter_index]

        if self.scene and is_animating() and not self.scene.in_play:
            # Yellow traversal highlight, same as __contains__
            anim = Succession(
                self.highlight(cell=cell, color=YELLOW, runtime=0.15),
                Wait(0.1),
                self.unhighlight(cell=cell, runtime=0.1),
            )
            self.play(anim)

        self._iter_index += 1
        return cell
    
    def get_index(self, cell:Cell) -> int:
        """Returns the index of the cell"""
        if isinstance(cell, int):
            #Why would you wanna pass an index in here???
            if 0 <= cell < len(self.elements):
                return cell
            else:
                raise IndexError(f"Index {cell} out of bounds for array of size {len(self.elements)}.")
            
        elif isinstance(cell, Cell):
            try:
                return self.elements.index(cell)
            except ValueError:
                raise ValueError("Cell does not belong to this VisualArray.")
        else:
            raise TypeError(f"Expected int or Cell, got {type(cell).__name__}")
          
    def set_value(self,index:int|Cell,value:any):
        def build():
            element_value = value.value if hasattr(value,"value") else value
            print(element_value)
            cell:Cell = self.get_element(index)
            print("Before Transform:", cell, "master:", cell.master)
            text_scale = 0.45 * self.cell_height / MathTex("0").height
            new_text = MathTex(str(element_value)).set_color(self.text_color).scale(text_scale)
            new_text.move_to(cell.get_center())
            new_text.add_updater(lambda m: m.move_to(cell.get_center()))
            cell.value = element_value
        
            return Transform(cell.text,new_text,run_time=0.5)
        return LazyAnimation(builder=build)
    
    def compare(self,index_1:int|Cell,index_2:int|Cell,result:bool=True,scalar=False):
        if scalar:
            return Wait(0)
            
        cell_1, cell_2 = self.get_element(index_1), self.get_element(index_2)
        color = GREEN if result else RED
        scale = 1.08 if result else 1.15  # slightly larger pulse for "swap"   
        

        highlight = AnimationGroup(
            self.highlight(cell=cell_1,color=color,runtime=0.2),
            self.highlight(cell=cell_2,color=color,runtime=0.2)
        )  
        pulse = AnimationGroup(
            Indicate(cell_1,scale_factor=scale,color=color),
            Indicate(cell_2,color=color,scale_factor=scale),
            lag_ratio=0.1
        )
        unhighlight = AnimationGroup(
            self.unhighlight(cell=cell_1,runtime=0.2),
            self.unhighlight(cell=cell_2,runtime=0.2)
        )
        return Succession(highlight,pulse,Wait(0.1),unhighlight)

               
    def shift_cell(self,from_idx:int,to_idx:int) -> LazyAnimation:
        """
        Move the cell at from_idx to to_idx,
        shifting all cells in between accordingly.
        """
        def build():
            #move_cell components
            def hop_up( cell:int|Cell, lift=0.5, runtime=0.3):
                cell = self.get_element(cell)
                start = cell.center
                shift_vec = (cell.top - start) / np.linalg.norm(cell.top - start)
                hop_pos = start + shift_vec * (cell.body_height + lift)
                return ApplyMethod(cell.move_to, hop_pos, run_time=runtime)

            def slide_to(cell:int|Cell, target_pos, runtime=0.5):
                cell:Cell = self.get_element(cell)
                cell_pos = cell.center
                
                target_pos = np.array([target_pos[0],cell_pos[1],cell_pos[2]])
                return ApplyMethod(cell.move_to, target_pos, run_time=runtime)

            def drop_down(cell:int|Cell, target_pos, runtime=0.3):
                cell = self.get_element(cell)
                return ApplyMethod(cell.move_to, target_pos, run_time=runtime)
            
            anims = []
            step = -1 if from_idx > to_idx else 1 #If from_idx is larger than to_idx then shift right else shift left
            
            destination = self.get_element(to_idx).center
            key:Cell = self.get_element(from_idx)
            anims.append(hop_up(cell=key))
            for i in range(from_idx + step,to_idx + step,step):
                cell:Cell = self.elements[i]
                prev:Cell = self.elements[i - step]
                anims.append(slide_to(cell=cell,target_pos=prev.center))
                
            anims.append(slide_to(cell=key,target_pos=destination))
            anims.append(drop_down(cell=key,target_pos=destination))
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
            
        
            
       
        
        # if bezier:
        #     ctrl1 = start + shift_vec * lift
        #     ctrl2 = target_pos + shift_vec * lift
        #     arc_path = CubicBezier(start,ctrl1,ctrl2,target_pos) #The cell lifts then moves in an arc to the desired location
        #     return MoveAlongPath(cell,arc_path,runtime=runtime)
        

        # hop_pos = start + shift_vec * (cell.body_height + lift) #Makes it go up by height
        hop_pos = get_offset_position(element=cell,direction=UP)
        #Post-hop
        x_shift = np.array([target_pos[0],hop_pos[1],target_pos[2]])
        y_shift = target_pos
        
        cell_shift = Succession(
            ApplyMethod(cell.move_to, hop_pos),
            ApplyMethod(cell.move_to, x_shift),
            ApplyMethod(cell.move_to, y_shift),
            run_time=2
        )
        return cell_shift
    
   
    
    def append(self,data,runtime=0.5,recenter=True) -> None:

        cell = Cell(value=data,master=self,cell_width=self.cell_width)
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
            
    def pop(self,index:int|Cell,runtime=0.5) -> any:
        
        def slide_to(cell:int|Cell, target_pos, runtime=0.5):
                cell:Cell = self.get_element(cell)
                cell_pos = cell.get_center()
                
                target_pos = np.array([target_pos[0],cell_pos[1],cell_pos[2]])
                return ApplyMethod(cell.move_to, target_pos, run_time=runtime)
        
        popped_cell:Cell = self.get_element(index)
        anims = []
        anims.append(FadeOut(popped_cell))
        for i in range(index - 1,-1,-1): #Shift cells to the right to fill up the popped cell
            cell:Cell = self.elements[i]
            prev:Cell = self.elements[i + 1]
            anims.append(slide_to(cell=cell,target_pos=prev.get_center()))
       
            
        self.play(*anims,runtime=runtime)    
        self.elements.pop(index)
        
        return popped_cell.value
    
    def insert(self,data,index:int|Cell,runtime=0.5) -> None:

        self.append(data)
        self.play(self.shift_cell(from_idx=len(self.elements) - 1,to_idx=index))
        
    
    def swap(self, idx_1: int, idx_2: int, color=YELLOW, runtime=0.5):
        """Swaps two cells in an array"""
    
    # Fetch cells
        cell_1: Cell = self.get_element(idx_1)
        cell_2: Cell = self.get_element(idx_2)

        # Get their centers before moving
        pos_1 = cell_1.center
        pos_2 = cell_2.center

        # Build simple motion animations
        move_1 = self.move_cell(cell_1, target_pos=pos_2)
    
        move_2 = self.move_cell(cell_2, target_pos=pos_1)
        self.elements[idx_2] = cell_1
        self.elements[idx_1] = cell_2
        # Return simultaneous motion
        # return AnimationGroup(move_1, move_2, lag_ratio=0.2)
        return Succession(move_1, move_2, runtime=0.5)

    


    def create(self,cells:list[Cell]|int=None,runtime=0.5) -> AnimationGroup:
        """Creates the Cell object or index passed, defaults to creating the entire array"""
        if not self.scene:
            return None
        if cells is None:
            cells:list[Cell] = self.elements

        #AnimationGroup in here controls cell vs text behaviour
        runtime = max(0.5,runtime) #Stuff gets ugly if less than 0.5
        cell_objs = [AnimationGroup(Create(cell.body),Write(cell.text),lag_ratio=runtime) for cell in cells]
        
        return AnimationGroup( #Control cells relative to other cells
            *cell_objs,
            lag_ratio=0.1,
            runtime=runtime
        )

        
        
    



            