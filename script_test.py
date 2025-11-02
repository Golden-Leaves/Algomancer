from manim import *
from Components.render_scene import render_scene
from Components.runtime import AlgoScene
from Structures.arrays import VisualArray


class DragArrayScene(AlgoScene):
    def construct(self):
        array = VisualArray([1, 2, 3, 4], scene=self,border=0)
        array.move_to(ORIGIN)
        array.play(array.create())
        array1 = VisualArray([2,3,5],scene=self,pos=DL)
        array1.play(array1.create())
        self.array = array
        self.interactive_embed()


if __name__ == "__main__":
    render_scene(
        DragArrayScene,
        file=__file__,
        quality="medium",
        renderer="opengl",
        preview=True,
    )
