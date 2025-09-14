from manim import *
import numpy as np
import math
class VisualArray(VGroup):
    def __init__(self,data,cell_width=2,text_color=WHITE,**kwargs):
        super().__init__(**kwargs)
        self.cells = []
        self.cell_texts = []
        
        for idx,text in enumerate(data):
            cell = Square(side_length=cell_width)
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
            
    def move_cell(self,index:int,target_pos,lift=0,runtime=1,bezier=False):
        """Moves specified cell to desired position"""
        cell:Square= self.cells[index]
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
        

        hop_pos = start + shift_vec * (cell.side_length + lift) #Makes it go up by side_length
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
        return self.cells[index].animate.set_fill(color=color, opacity=opacity)
    def unhighlight(self, index:int):
        return self.cells[index].animate.set_fill(opacity=0)
    
    def swap(self,idx_1,idx_2,color=YELLOW):
        #TODO:  Make move cell highlight on move
        cell_1:Square = self.cells[idx_1]
        cell_2:Square = self.cells[idx_2]
        self.cells[idx_2] = cell_1
        self.cells[idx_1] = cell_2
        
        cell_1_move = Succession(
            ApplyMethod(self.highlight,idx_1,color),
            self.move_cell(idx_1,target_pos=cell_2.get_center()),
            ApplyMethod(self.unhighlight,idx_1),
            lag_ratio=0.5
            )
        cell_2_move = Succession(
            ApplyMethod(self.highlight,idx_2,color),
            self.move_cell(idx_2,target_pos=cell_1.get_center()),
            ApplyMethod(self.unhighlight,idx_2),
            lag_ratio=0.5
            )
        
        return AnimationGroup(cell_1_move,cell_2_move,lag_ratio=0.5)   
    
    def test_shift(self,index=0):
        cell:Square = self.cells[index].move_to(ORIGIN)
        self.add(cell)

        # animate upward shift only
        return cell.animate.shift(UP * 2)
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