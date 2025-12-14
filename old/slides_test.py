from manim import *  
from manim_slides import Slide
from Components.runtime import AlgoSlide,AlgoScene
from Components.render_scene import render_scene
from Structures.arrays import VisualArray

class YesSir(AlgoSlide):
    def construct(self):
        with self.animation_context():
            array = VisualArray([1,2,3,4],scene=self)
            self.play(array.create())
            self.next_slide()
            for i in range(2):
                self.play(array.highlight(i))
                self.play(array.unhighlight(i))
                self.next_slide()
if __name__ == "__main__":
    render_scene(YesSir,file=__file__,quality="medium",preview=True)