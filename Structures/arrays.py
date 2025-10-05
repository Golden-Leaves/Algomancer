from manim import *
import numpy as np
import math
from utils import LazyAnimation,get_offset_position
from Structures.base import VisualStructure,VisualElement

BRIGHT_GREEN = "#00FF00"

    
class Cell(VisualElement):
    def __init__(self, value:any, cell_width:int=1, cell_height:int=1, text_color:ManimColor=WHITE,rounded=False,**kwargs):
        
        self.rounded = rounded
        corner_radius = 0.3 if rounded else 0
        self.body = (RoundedRectangle(width=cell_width, height=cell_height, corner_radius=corner_radius) if rounded else 
                Rectangle(width=cell_width, height=cell_height))
        self.body.set_fill(color=RED, opacity=0)
        
        super().__init__(self.body,**kwargs)
        self.value = value  #The value contained within the Cell
        
        # Create the text inside

        text_scale = 0.45 * cell_height / MathTex("0").height #38% of cell area
        self.text = MathTex(str(value)).set_color(text_color).scale(text_scale)
        self.text.move_to(self.get_center())
        self.text.add_updater(lambda m: m.move_to(self.get_center()))
        
        self.add(self.body, self.text)
        
    
class VisualArray(VisualStructure):
    def __init__(self,data:any,scene:Scene,cell_width:int=1,cell_height:int=1,text_color:ManimColor=WHITE,**kwargs):
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
        self.rounded = kwargs.pop("rounded",False)
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
        self.text_color = text_color
        self.cells:list[Cell] = []
        self.length = 0
        self.cell_width = cell_width
        self.cell_height = cell_height
        if data:
            for idx,text in enumerate(data):
                # text_scale = 0.45 * cell_width / MathTex("0").height    #30% of cell_height
                # cell_text = MathTex(str(text)).set_color(text_color).move_to(cell.get_center()).scale(text_scale)
                # cell_text.add_updater(lambda x, c = cell: x.move_to(c.get_center()))
                
                cell = Cell(value=text,cell_width=self.cell_width,cell_height=self.cell_height,
                            text_color=text_color,rounded=self.rounded)
                if idx == 0:
                    cell.move_to(ORIGIN)
                else:
                    cell.next_to(self.cells[idx - 1],RIGHT,buff=0)
                    
                
                
                self.cells.append(cell)

                self.add(cell)
                self.move_to(self.pos) #Moves the center of the array to the origin
        self.length = len(self.cells)
            
   
    def get_element(self, cell_or_index:Cell|int):
        """Error handling opps, can also be used to retrieve an element with an index"""
    # Case 1: int → lookup in self.cells
        if isinstance(cell_or_index, int):
            try:
                return self.cells[cell_or_index]
            except IndexError:
                raise IndexError(
                    f"Invalid index {cell_or_index}. "
                    f"Valid range is 0 to {len(self.cells) - 1}."
                )

        # Case 2: already a Cell 
        elif isinstance(cell_or_index, Cell):
            if cell_or_index not in self.cells:
                raise ValueError(
                    "Cell object does not belong to this VisualArray."
                )
            return cell_or_index

        # Case 3: goofy input
        else:
            raise TypeError(
                f"Expected int or Cell object, got {type(cell_or_index).__name__}."
            )        
    def get_index(self, cell:Cell) -> int:
        """Returns the index of the cell"""
        if isinstance(cell, int):
            #Why would you wanna pass an index in here???
            if 0 <= cell < len(self.cells):
                return cell
            else:
                raise IndexError(f"Index {cell} out of bounds for array of size {len(self.cells)}.")
            
        elif isinstance(cell, Cell):
            try:
                return self.cells.index(cell)
            except ValueError:
                raise ValueError("Cell does not belong to this VisualArray.")
        else:
            raise TypeError(f"Expected int or Cell, got {type(cell).__name__}")
          
            
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
                cell:Cell = self.cells[i]
                prev:Cell = self.cells[i - step]
                anims.append(slide_to(cell=cell,target_pos=prev.center))
                
            anims.append(slide_to(cell=key,target_pos=destination))
            anims.append(drop_down(cell=key,target_pos=destination))
            finalize:Wait = Wait(0)
            finish_animation = finalize.finish
            #https://docs.manim.community/en/stable/reference/manim.animation.composition.Succession.html#manim.animation.composition.Succession.finish
            def new_finish(): #Monkeypatches the .finish method of the current Wait instance
                finish_animation()
                shifted_cell = self.cells.pop(from_idx)
                self.cells.insert(to_idx,shifted_cell)

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
        hop_pos = get_offset_position(element=cell,direction="up")
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
    
   
        
    def highlight(self, cell:int|Cell, color=YELLOW, opacity=0.5, runtime=0.5) -> ApplyMethod:
        cell: Cell = self.get_element(cell).body  
        return ApplyMethod(cell.set_fill, color, opacity, run_time=runtime)

    def unhighlight(self, cell:int|Cell, runtime=0.5) -> ApplyMethod:
        cell: Cell = self.get_element(cell).body
        return ApplyMethod(cell.set_fill, 0, run_time=runtime)
    
    def outline(self, cell:int|Cell, color=PURE_GREEN, width=6, runtime=0.5) -> ApplyMethod:
        cell:Rectangle = self.get_element(cell).body
        return ApplyMethod(cell.set_stroke, color, width, 1.0, run_time=runtime)

    def unoutline(self, cell:int|Cell, color=WHITE, width=4, runtime=0.5) -> ApplyMethod:
        cell:Rectangle = self.get_element(cell).body
        return ApplyMethod(cell.set_stroke, color, width, 1.0, run_time=runtime)
    
    def append(self,data,runtime=0.5,recenter=True) -> None:

        cell = Cell(value=data,cell_width=self.cell_width)
        last_cell:Cell = self.cells[-1] if self.cells else cell
        if self.cells:#If an array already exists
            right_side = last_cell.right
            right_vec = right_side / np.linalg.norm(right_side)
            cell.move_to(last_cell.right + right_vec * (last_cell.body_width / 2)) #Spawns next to last_cell   
        
        self.add(cell)
        self.cells.append(cell)
        self.create(cells=[cell])
        
        self.length = len(self.cells)
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
        for i in range(index - 1,-1,-1):
            cell:Cell = self.cells[i]
            prev:Cell = self.cells[i + 1]
            anims.append(slide_to(cell=cell,target_pos=prev.get_center()))
       
            
        self.play(*anims,runtime=runtime)    
        self.cells.pop(index)
        self.length = len(self.cells)
        return popped_cell.value
    
    def insert(self,data,index:int|Cell,runtime=0.5) -> None:

        self.append(data)
        self.play(self.shift_cell(from_idx=len(self.cells) - 1,to_idx=index))
        
    
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
        self.cells[idx_2] = cell_1
        self.cells[idx_1] = cell_2
        # Return simultaneous motion
        # return AnimationGroup(move_1, move_2, lag_ratio=0.2)
        return Succession(move_1, move_2, runtime=0.5)
    



    def create(self,cells:list[Cell]|int=None,runtime=0.5) -> AnimationGroup:
        """Creates the Cell object or index passed, defaults to creating the entire array"""
        if cells is None:
            cells:list[Cell] = self.cells

        #AnimationGroup in here controls cell vs text behaviour
        runtime = max(0.5,runtime) #Stuff gets ugly if less than 0.5
        cell_objs = [AnimationGroup(Create(cell.body),Write(cell.text),lag_ratio=runtime) for cell in cells]
        
        return AnimationGroup( #Control cells relative to other cells
            *cell_objs,
            lag_ratio=0.1,
            runtime=runtime
        )

        
        
    



            