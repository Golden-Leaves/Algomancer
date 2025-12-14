from manim import *
from Components.runtime import AlgoScene
from Components.logging import DebugLogger
from Components.render_scene import render_scene
from Structures.arrays import VisualArray
from Structures.pointers import Pointer
class CarFleet(AlgoScene):
    def __init__(self, renderer=None, camera_class=None, always_update_mobjects=False, random_seed=None, skip_animations=False):
        super().__init__(renderer, camera_class, always_update_mobjects, random_seed, skip_animations)
        self.logger = DebugLogger(logger_name=__name__, output=True)
    def carFleet(self, target: int, position: list[int], speed: list[int]) -> int:
        cars = VisualArray(sorted(list(zip(position,speed)),reverse=True), label="cars", scene=self, start_pos=DOWN*0.5) 
        self.play(cars.create())
        times = VisualArray([1.0],label="times",scene=self,start_pos=UP*0.5)
        
        self.play(times.create())
        c = Pointer(value=1,master=cars,color=PURPLE)
        self.play(c.create())
        while c < len(cars):
            time = (target - cars[c][0]) / cars[c][1]
            if time > times[-1]:
                times.append(time)
            c += 1
        return len(times)
    def construct(self):
        with self.animation_context():
            self.carFleet(12,[10,8,0,5,3],[2,4,1,1,3])

        self.wait(1)
        self.interactive_embed()

if __name__ == "__main__":
    render_scene(CarFleet, file=__file__, quality="high", renderer="opengl", fps=30, write_to_file=False,slides=False)