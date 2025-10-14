from manim import *
from Structures.arrays import VisualArray
from Structures.pointers import Pointer,PointerRange
from Algorithms.sorting import bubble_sort,insertion_sort
from Algorithms.searching import linear_search
from Utils.runtime import AlgoScene
from Tests import test_arrays as ta
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
    def two_sum(self,nums:VisualArray,target:int):
        for i in PointerRange(len(nums),master=nums,label="i"):
            print("I iterable",i,type(i))
            for j in PointerRange(i + 1,len(nums),master=nums,label="j"):
                if nums[i] + nums[j] == target:
                    return [i,j]
        
                    
    def construct(self):
        with self.animation_context():
            array = VisualArray([1,2,5,4],scene=self)
            ta.test_create(array=array)
            # ptr_i = Pointer(0,master=array,label="i")
            # ptr_j = Pointer(len(array) - 1,master=array,label="j")
            # array.play(ptr_i.create(),ptr_j.create())
            # ta.test_full_with_pointers(array=array,ptr_a=ptr_i,ptr_b=ptr_j)
            result = self.two_sum(nums=array,target="7")
            print(result)
            
        
       
        # array.play(array.create(),array.highlight(cell=1),array.set_value(index=1,value=12))
        # # array.play(array.set_value(index=1,value=12))
        # array.play(array.swap(1,2))
        # array.play(array.compare(index_1=1,index_2=3))
        # text = Text(str(len(array))).to_corner(UR)
        # self.play(Write(text))
        
        
        self.wait(1)
        
        
        
     
        
if __name__ == "__main__":
    render_scene(ArrayScene,file=__file__,quality="medium")
