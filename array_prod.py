from manim import *
from Structures.arrays import VisualArray
from Algorithms.sorting import bubble_sort,insertion_sort
from Algorithms.searching import linear_search
from helpers import render_scene
import numpy as np
import random
class ArrayScene(Scene):
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
        array = VisualArray(["a","b","c"],scene=self,cell_width = 1)
        array.create()
        cell = linear_search(array=array,target="c")
        array.play(array.shift_cell(from_idx=array.index(cell),to_idx=0))
        self.wait(0.5)
        array.play(array.outline(cell),array.unoutline(cell))
        self.wait(0.5)
        
     
        
if __name__ == "__main__":
    render_scene(ArrayScene,file=__file__,quality="medium")
