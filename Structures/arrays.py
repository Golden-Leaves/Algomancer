from manim import *
import numpy as np
import math

class LazyAnimation:
    """Wrapper for a function that builds an Animation lazily."""
    def __init__(self, builder):
        self.builder = builder
    def build(self) -> Animation:
        anim = self.builder()
        if not isinstance(anim, Animation):
            raise TypeError(f"Builder returned {type(anim)}, expected Animation.")
        return anim
    
class Cell(VGroup):
    def __init__(self, value, cell_width=2, text_color=WHITE):
        super().__init__()

        self.value = value  # value (used in sorting)
        self.square = Square(side_length=cell_width)
        
        # Create the text inside
        text_scale = 0.45 * cell_width / MathTex("0").height #45% of cell height
        self.text = MathTex(str(value)).set_color(text_color).scale(text_scale)
        self.text.move_to(self.square.get_center())
        self.text.add_updater(lambda m: m.move_to(self.square.get_center()))
        
        self.add(self.square, self.text)
    
class VisualArray(VGroup):
    def __init__(self,data,scene,cell_width=2,text_color=WHITE,**kwargs):
        super().__init__(**kwargs)
        self.cells = []
        self.cell_texts = []
        self.scene = scene
        for idx,text in enumerate(data):
            cell = Cell(value=text,cell_width=cell_width,text_color=text_color)
            if idx == 0:
                cell.move_to(ORIGIN)
            else:
                cell.next_to(self.cells[idx - 1],RIGHT,buff=0)
                
            text_scale = 0.45 * cell_width / MathTex("0").height    #30% of cell_height
            cell_text = MathTex(str(text)).set_color(text_color).move_to(cell.get_center()).scale(text_scale)

            cell_text.add_updater(lambda x, c = cell: x.move_to(c.get_center()))
            
            self.cells.append(cell)
            self.cell_texts.append(cell_text)
            self.add(cell)
            
    def play(self, *anims, **kwargs):
        """Recursive play: handles single or multiple animations
        Can accept either an array or multiple animations
        """
        if not self.scene:
            raise RuntimeError("No Scene bound. Pass scene=... when creating VisualArray.")
        for anim in anims:
            #Checks if it's a builder animation or just plain animation
            anim = anim.build() if isinstance(anim,LazyAnimation) else anim
                
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
    def move_cell(self,cell:int|Square,target_pos,lift=0,runtime=1,bezier=False):
        """Moves specified cell to desired position"""
        cell:Cell = self.get_cell(cell)
            
        start = cell.get_center()
        top_side = cell.get_top() - cell.get_center() 
        right_side = cell.get_right() - cell.get_center()
        bottom_side = cell.get_bottom() - cell.get_center()
        shift_vec = top_side / np.linalg.norm(top_side)
        
            
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
        
    def highlight(self, index:int, color=YELLOW, opacity=0.5):
        cell:Square = self.get_cell(index)
        return cell.animate.set_fill(color=color, opacity=opacity)
    def unhighlight(self, index:int):
        cell:Square = self.get_cell(index)
        return cell.animate.set_fill(opacity=0)
    
    def swap(self,idx_1:int,idx_2:int,color=YELLOW,runtime=0.5):
        """Swaps two cells in an array"""
        def build(): #Builds a reference so play can reconstruct
            #TODO:  Make move cell highlight on move
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
    
    def animate_creation(self,runtime=0.5):
        #AnimationGroup in here controls cell vs text behaviour
        # cell_objs = [AnimationGroup(Create(cell),Write(text),lag_ratio=lag) for (cell,text) in zip(self.cells,self.cell_texts)]
        runtime = max(0.5,runtime)
        cell_objs = [AnimationGroup(Create(cell),Write(text),lag_ratio=0.5) for (cell,text) in zip(self.cells,self.cell_texts)]
        return AnimationGroup( #Control cells relative to other cells
            *cell_objs,
            lag_ratio=0.1,
            runtime=runtime
        )
        
        
    def bubble_sort(self):
       """Sorts the array and animate using bubble sort"""
       n = len(self.cells)
       for i in range(n):
           for j in range(n - i - 1):
               cell_1:Cell = self.cells[j]
               cell_2:Cell = self.cells[j+1]
               if cell_1.value > cell_2.value:
                cell_1 = self.cells[j]
                cell_2 = self.cells[j+1]
                self.play(self.highlight(j),self.highlight(j+1))
                self.play(self.swap(j,j+1))
                self.play(self.unhighlight(j),self.unhighlight(j+1))