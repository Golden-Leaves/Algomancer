from manim import *
from Structures.arrays import VisualArray
from Structures.pointers import Pointer,PointerRange
from Algorithms.searching import linear_search
from Components.runtime import AlgoScene,AlgoSlide
from Tests import test_arrays as ta
from Components.logging import DebugLogger
from Components.render_scene import render_scene
class ArrayScene(AlgoSlide):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.logger = DebugLogger(logger_name=__name__, output=True)
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
                    self.play(array.swap(j,j+1))
            self.play(array.outline(element=array[len(array) - 1 - i]))
                    
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
    def isValid(self, s: VisualArray) -> bool:
        pairs = {
        '(': ')',
        '[': ']',
        '{': '}'}
        
        stack = VisualArray([],scene=self,label="stack",pos=DOWN+LEFT)
        self.play(stack.create())
        for char in s:
            if char in pairs:
                stack.append(char,recenter=False)
            else:
                if not stack or pairs[stack.pop()] != char:
                    return False
        return len(stack) == 0  
        
    def construct(self):
        with self.animation_context():
            # array = VisualArray([],scene=self)
            # ptr_a = Pointer(value=1,master=array,label="a")
            # ptr_b = Pointer(value=0,master=array,label="b")
            # self.play(array.create())
            # array.append("str")
            s = VisualArray("(([]))",scene=self,label="string",start_pos=UP+LEFT)
            self.play(s.create())

            # # s.append(data=1,recenter=False)
            # self.logger.log_stucture_state(structure=s,label="before move_to")
            # s.move_to(ORIGIN)
           
            # self.logger.log_stucture_state(structure=s,label="after move_to")
            # self.wait(1)
            # s.move_to(UP)
            # # s.append(data=1)
            
            self.isValid(s=s)
            

        
    
            
            # array[3] += 3
            # array[2] > array[1]
            # self.bubble_sort(array=array)
            
            

        self.wait(1)
        self.interactive_embed()
    
        
        
        
        
if __name__ == "__main__":
    render_scene(ArrayScene,file=__file__,quality="medium",renderer="opengl",fps=30,write_to_file=True)
