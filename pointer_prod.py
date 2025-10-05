from manim import *
from Structures.arrays import VisualArray
from Structures.pointer import Pointer
from helpers import render_scene

class PointerTest(Scene):
    def construct(self):
        array = VisualArray([1,2,3,4],scene=self)
        i = Pointer(0,master=array,scene=self,label="This is a label",direction=UP)
        array.play(array.create(),i.create_arrow())
        # i.play(i.create_arrow())
        # self.wait(1)
        self.wait(1)

if __name__ == "__main__":
    render_scene(PointerTest,file=__file__,quality="medium")