from manim import *
from Structures.arrays import VisualArray
from Structures.pointer import Pointer
from Algorithms.sorting import bubble_sort,insertion_sort
from Algorithms.searching import linear_search
from Utils.runtime import AlgoScene
from helpers import render_scene
import numpy as np
import random
class ArrayScene(AlgoScene):
    def generate_board(self,array:np.ndarray):
        pass
    def bubble_sort(self,array: VisualArray):
        """Sorts the array and animates using bubble sort.
        Expects a VisualArray instance with a bound scene.
        """
        n = len(array.cells)
        for i in range(n):
            for j in range(n - i - 1):
                cell_1 = array.cells[j]
                cell_2 = array.cells[j + 1]

                if cell_1.value > cell_2.value:
                    # Highlight compared cells
                    array.play(array.highlight(j), array.highlight(j + 1), runtime=0.2)

                    # Perform the swap
                    array.play(array.swap(j, j + 1))

                    # Remove highlight
                    array.play(array.unhighlight(j), array.unhighlight(j + 1), runtime=0.2)
                    
    def construct(self):

        with self.animation_context():
            array = VisualArray([1,2,5,22,4,3],scene=self)
            array.play(array.create())
            array[1] += 1
            i = Pointer(0,master=array,label="i")
            array.play(i.create())
            i += 1
            

        
        
        
       
        # array.play(array.create(),array.highlight(cell=1),array.set_value(index=1,value=12))
        # # array.play(array.set_value(index=1,value=12))
        # array.play(array.swap(1,2))
        # array.play(array.compare(index_1=1,index_2=3))
        # text = Text(str(len(array))).to_corner(UR)
        # self.play(Write(text))
        
        
        self.wait(1)
        
        
        
     
        
if __name__ == "__main__":
    render_scene(ArrayScene,file=__file__,quality="medium")
