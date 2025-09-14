from manim import *
from Structures.arrays import VisualArray
from helpers import render_scene
class ArrayScene(Scene):
    def construct(self):
        array = VisualArray([1,2,3,4],cell_width = 0.5)
        self.play(array.animate_creation())
        self.wait(1)
if __name__ == "__main__":
    render_scene(ArrayScene,file=__file__,quality="medium")
