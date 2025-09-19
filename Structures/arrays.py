from manim import *
import numpy as np
import math

class LazyAnimation:
    """Wrapper for a function that builds an Animation lazily.
    Anything that modifies self.cells will use this\n
    This is used to allow multiple animations to be passed to play(), since this prevents them from being evaluated
    """
    def __init__(self, builder):
        self.builder = builder
    def build(self) -> Animation:
        anim = self.builder()
        return anim
    
class Cell(VGroup):
    def __init__(self, value, cell_width=2, text_color=WHITE):
        super().__init__()
        self.cell_width = cell_width
        self.value = value  # value (used in sorting)
        self.square = Square(side_length=cell_width)
        self.square.set_fill(color=RED, opacity=0)
        # Create the text inside
        text_scale = 0.45 * cell_width / MathTex("0").height #45% of cell height
        self.text = MathTex(str(value)).set_color(text_color).scale(text_scale)
        self.text.move_to(self.square.get_center())
        self.text.add_updater(lambda m: m.move_to(self.square.get_center()))
        
        self.add(self.square, self.text)
    
class VisualArray(VGroup):
    def __init__(self,data,scene,cell_width=2,text_color=WHITE,**kwargs):
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
        
        self.pos = kwargs.pop("pos",None) #Center of the array
        if self.pos is None:
            x = kwargs.get("x",ORIGIN[0])
            y = kwargs.get("y",ORIGIN[1])
            z = kwargs.get("z",ORIGIN[2])
            self.pos = np.array([x,y,z])
        else:
            self.pos = np.array(self.pos)
            
        super().__init__(**kwargs)
        self.cell_width = cell_width
        self.text_color = text_color
        self.cells:list[Cell] = []
        self.length = 0
            
        self.scene = scene
        if data:
            for idx,text in enumerate(data):
                # text_scale = 0.45 * cell_width / MathTex("0").height    #30% of cell_height
                # cell_text = MathTex(str(text)).set_color(text_color).move_to(cell.get_center()).scale(text_scale)
                # cell_text.add_updater(lambda x, c = cell: x.move_to(c.get_center()))
                
                cell = Cell(value=text,cell_width=cell_width,text_color=text_color)
                if idx == 0:
                    cell.move_to(ORIGIN)
                else:
                    cell.next_to(self.cells[idx - 1],RIGHT,buff=0)
                    
                
                
                self.cells.append(cell)

                self.add(cell)
                self.move_to(self.pos) #Moves the center of the array to the origin
        self.length = len(self.cells)
            
    def play(self, *anims, **kwargs):
        """Recursive play: handles single or multiple animations
        Can accept either an array or multiple animations
        """
        if not self.scene:
            raise RuntimeError("No Scene bound. Pass scene=... when creating VisualArray.")
        for anim in anims:
            #Checks if it's a builder animation or just plain animation
            anim = anim.build() if isinstance(anim,LazyAnimation) else anim
            print(anim)
            if not isinstance(anim,Animation):
                raise TypeError(f"Unexpected {type(anim)} passed to play()")
            self.scene.play(anim, **kwargs)
   
            
    def get_cell(self, cell_or_index):
        """Error handling opps"""
    # Case 1: int → lookup in self.cells
        if isinstance(cell_or_index, int):
            try:
                return self.cells[cell_or_index]
            except IndexError:
                raise IndexError(
                    f"Invalid index {cell_or_index}. "
                    f"Valid range is 0 to {len(self.cells) - 1}."
                )

        # Case 2: already a Square 
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
    def shift_cell(self,from_idx:int,to_idx:int) -> LazyAnimation:
        """
        Move the cell at from_idx to to_idx,
        shifting all cells in between accordingly.
        """
        def build():
            #move_cell components
            def hop_up( cell:int|Cell, lift=0.5, runtime=0.3):
                cell = self.get_cell(cell)
                start = cell.get_center()
                shift_vec = (cell.get_top() - cell.get_center()) / np.linalg.norm(cell.get_top() - cell.get_center())
                hop_pos = start + shift_vec * (cell.square.side_length + lift)
                return ApplyMethod(cell.move_to, hop_pos, run_time=runtime)

            def slide_to(cell:int|Cell, target_pos, runtime=0.5):
                cell:Cell = self.get_cell(cell)
                cell_pos = cell.get_center()
                
                target_pos = np.array([target_pos[0],cell_pos[1],cell_pos[2]])
                return ApplyMethod(cell.move_to, target_pos, run_time=runtime)

            def drop_down(cell:int|Cell, target_pos, runtime=0.3):
                cell = self.get_cell(cell)
                return ApplyMethod(cell.move_to, target_pos, run_time=runtime)
            
            anims = []
            step = -1 if from_idx > to_idx else 1 #If from_idx is larger than to_idx then shift right else shift left
            
            destination = self.cells[to_idx].get_center()
            key:Cell = self.cells[from_idx]
            anims.append(hop_up(cell=key))
            for i in range(from_idx + step,to_idx + step,step):
                cell:Cell = self.cells[i]
                prev:Cell = self.cells[i - step]
                anims.append(slide_to(cell=cell,target_pos=prev.get_center()))
                
            anims.append(slide_to(cell=key,target_pos=destination))
            anims.append(drop_down(cell=key,target_pos=destination))
            finalize:Wait = Wait(0)
            finish_animation = finalize.finish
            def new_finish(): #Monkeypatches the .finish method of the current Wait instance
                finish_animation()
                shifted_cell = self.cells.pop(from_idx)
                self.cells.insert(to_idx,shifted_cell)
                
            finalize.finish = new_finish      
            return Succession(*anims,finalize)
        return LazyAnimation(builder=build)
    
            
            
            

    def move_cell(self,cell:int|Square,target_pos,lift=0,runtime=1,bezier=False) -> Succession:
        """Moves specified cell to desired position"""
        cell:Cell = self.get_cell(cell)
            
        start = cell.get_center()
        top_side = cell.get_top() - cell.get_center() 
        right_side = cell.get_right() - cell.get_center()
        bottom_side = cell.get_bottom() - cell.get_center()
        shift_vec = top_side / np.linalg.norm(top_side) #Top vector
        
            
        if bezier:
            ctrl1 = start + shift_vec * lift
            ctrl2 = target_pos + shift_vec * lift
            arc_path = CubicBezier(start,ctrl1,ctrl2,target_pos) #The cell lifts then moves in an arc to the desired location
            return MoveAlongPath(cell,arc_path,runtime=runtime)
        

        hop_pos = start + shift_vec * (cell.square.side_length + lift) #Makes it go up by side_length
        #Post-hop
        x_shift = np.array([target_pos[0],hop_pos[1],0])
        y_shift = target_pos
        # cell_shift = (cell.animate.move_to(hop_pos).move_to(x_shift).move_to(y_shift)
        #               .set_run_time(0.5))
        #ApplyMethod treats each as a standalone animation, so Sucession works
        cell_shift = Succession(
            ApplyMethod(cell.move_to, hop_pos),
            ApplyMethod(cell.move_to, x_shift),
            ApplyMethod(cell.move_to, y_shift),
            run_time=2
        )
        return cell_shift
        
    def highlight(self, cell:int|Cell, color=YELLOW, opacity=0.5, runtime=0.3) -> ApplyMethod:
        cell: Square = self.get_cell(cell).square
        return ApplyMethod(cell.set_fill, color, opacity, run_time=runtime)

    def unhighlight(self, cell:int|Cell, runtime=0.3) -> ApplyMethod:
        cell: Square = self.get_cell(cell).square
        return ApplyMethod(cell.set_fill, 0, run_time=runtime)
    
    def append(self,data,runtime=0.5,recenter=True) -> None:

        cell = Cell(value=data,cell_width=self.cell_width)
        last_cell:Cell = self.cells[-1] if self.cells else cell
        if self.cells:#If an array already exists
            right_side = last_cell.get_right()
            right_vec = right_side / np.linalg.norm(right_side)
            cell.move_to(last_cell.get_right() + right_vec * (last_cell.cell_width / 2)) #Spawns next to last_cell   
        
        self.add(cell)
        self.cells.append(cell)
        self.create_cells(cells=[cell])
        
        self.length = len(self.cells)
        if recenter: 
            self.move_to(self.pos)
            
    def pop(self,index:int|Cell,runtime=0.5) -> any:
        
        def slide_to(cell:int|Cell, target_pos, runtime=0.5):
                cell:Cell = self.get_cell(cell)
                cell_pos = cell.get_center()
                
                target_pos = np.array([target_pos[0],cell_pos[1],cell_pos[2]])
                return ApplyMethod(cell.move_to, target_pos, run_time=runtime)
        
        popped_cell:Cell = self.get_cell(index)
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
        
        
        
    def swap(self,idx_1:int,idx_2:int,color=YELLOW,runtime=0.5):
        """Swaps two cells in an array"""
        def build(): #Builds a reference so play can reconstruct
            cell_1:Cell = self.get_cell(idx_1)
            cell_2:Cell = self.get_cell(idx_2)
            pos_1 = cell_1.get_center()
            pos_2 = cell_2.get_center()
            
            cell_1_move = self.move_cell(cell_1, target_pos=pos_2)
            cell_2_move = self.move_cell(cell_2, target_pos=pos_1)
            group = AnimationGroup(cell_1_move,cell_2_move,lag_ratio=runtime)
            finalize:Wait = Wait(0)
            finish_animation = finalize.finish
            #https://docs.manim.community/en/stable/reference/manim.animation.composition.Succession.html#manim.animation.composition.Succession.finish
            def new_finish(): #Monkeypatches the .finish method of the current Wait instance
                finish_animation()
                self.cells[idx_2] = cell_1
                self.cells[idx_1] = cell_2
            finalize.finish = new_finish
            
            #The animation runs first before the array gets mutated
            return Succession(group,finalize) 
        return LazyAnimation(builder=build)

    def create(self,runtime=0.5):
        if self.cells:
            #AnimationGroup in here controls cell vs text behaviour
            runtime = max(0.5,runtime) #Stuff gets ugly if less than 0.5
            cell_objs = [AnimationGroup(Create(cell.square),Write(cell.text),lag_ratio=runtime) for cell in self.cells]
            
            self.play(AnimationGroup( #Control cells relative to other cells
                *cell_objs,
                lag_ratio=0.1,
                runtime=runtime
            ))
    def create_cells(self,cells:list[Cell],runtime=0.5):
        runtime = max(0.5,runtime)
        cell_objs = [AnimationGroup(Create(cell.square),Write(cell.text),lag_ratio=runtime) for cell in cells]
        
        self.play(AnimationGroup( 
            *cell_objs,
            lag_ratio=0.1,
            runtime=runtime
        ))
        
        
    



            