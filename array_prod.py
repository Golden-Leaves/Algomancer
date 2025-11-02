from manim import *
from Structures.arrays import VisualArray
from Structures.pointers import Pointer,PointerRange
from Algorithms.searching import linear_search
from Components.runtime import AlgoScene
from Tests import test_arrays as ta
from Components.logging import setup_logging
from Components.render_scene import render_scene
import numpy as np

class ArrayScene(AlgoScene):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.logger = setup_logging(logger_name="algoamancer.array_prod",output=True)
    def generate_board(self,array:np.ndarray):
        pass
    # def bubble_sort(self,array: VisualArray):
    #     """Sorts the array and animates using bubble sort.
    #     Expects a VisualArray instance with a bound scene.
    #     """
    #     n = len(array.cells)
    #     for i in range(n):
    #         for j in range(n - i - 1):
    #             cell_1 = array.cells[j]
    #             cell_2 = array.cells[j + 1]

    #             if cell_1.value > cell_2.value:
    #                 # Highlight compared cells
    #                 array.play(array.highlight(j), array.highlight(j + 1), runtime=0.2)

    #                 # Perform the swap
    #                 array.play(array.swap(j, j + 1))

    #                 # Remove highlight
    #                 array.play(array.unhighlight(j), array.unhighlight(j + 1), runtime=0.2)
    def bubble_sort(self,array:VisualArray):
        for i in PointerRange(len(array),master=array,label="i"):
            for j in PointerRange(len(array) - 1 - i,master=array,label="j",color=PURPLE):
                if array[j] > array[j+1]:
                    temp = array[j]
                    array[j] = array[j+1]
                    array[j+1] = temp
            array.play(array.outline(element=len(array) - i))
                    
        return array
                    
            
                    
    def two_sum(self,nums:VisualArray,target:int):
        for i in PointerRange(len(nums),master=nums,label="i"):
            for j in PointerRange(i + 1,len(nums),master=nums,label="j"):
                if (nums[i] + nums[j]) == target:
                    return [i,j]
                
    def threeSum(self,nums: VisualArray):
        # nums.sort()
        triplets = []

        for idx,k in enumerate(nums):
            if k > 0:
                break #No more negatives
            if idx and nums[idx] == nums[idx - 1]:
                continue      

            i = Pointer(idx + 1,master=nums,label="i",color=RED)
            j = Pointer(len(nums) - 1,master=nums,label="j")
            nums.play(i.create(),j.create())
            while i < j:
                self.logger.debug("Pointers i=%s, j=%s", i, j)
                three_sum = nums[i] + nums[j] + k
                if three_sum > 0:
                    j -=1
                elif three_sum < 0:
                    i += 1
                else:
                    triplets.append([nums[i],nums[j],k])
                    i += 1
                    j -= 1
                    while i < j and nums[i] == nums[i-1]:
                        i += 1
            nums.play(nums.outline(element=idx))
            i.destroy()
            j.destroy()

        return triplets
                    
    def construct(self):
        with self.animation_context():
            array = VisualArray([-2,0,1,1,2],scene=self)
            ptr_a = Pointer(value=1,master=array,label="a")
            ptr_b = Pointer(value=0,master=array,label="b")
            array.play(array.create())
            self.bubble_sort(array)
            print(array)

            # element = array.get_element(1)
            # array.log_state(label="After array creation",level="INFO",elements=[element])
            # array.play(array.indicate(element=element))
            # array.log_state(label="After first indicate",level="INFO",elements=[element])
            
            # array.play(array.highlight(element=1))
            # array.log_state(label="After first highlight",level="INFO",elements=[array.get_element(1)])
            # array.play(array.unhighlight(element=1))
            # array.log_state(label="After first unhighlight",level="INFO",elements=[array.get_element(1)])
           
            # result = self.threeSum(nums=array)
            # self.logger.info("threeSum result: %s", result)
            # ta.test_full_with_pointers(array=array,ptr_a=ptr_a,ptr_b=ptr_b)
           
        self.wait(1)
        self.interactive_embed()
    
        
        
     
        
if __name__ == "__main__":
    render_scene(ArrayScene,file=__file__,quality="medium",renderer="opengl",fps=30)
