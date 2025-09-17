from manim import *
from Structures.arrays import VisualArray
from helpers import render_scene
class ArrayScene(Scene):
    def construct(self):
        array = VisualArray([1,2,3,4],scene=self,cell_width = 0.5)
        self.play(array.animate_creation())
        # array.play(array.swap(0,2),array.swap(3,2))
        array.bubble_sort()
        self.wait(1)
if __name__ == "__main__":
    render_scene(ArrayScene,file=__file__,quality="medium")
