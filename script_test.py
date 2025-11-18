from manim import *
from Components.runtime import AlgoScene
from Components.logging import DebugLogger
from Components.render_scene import render_scene
from Structures.arrays import VisualArray
class SceneName(AlgoScene):
    def __init__(self, renderer=None, camera_class=None, always_update_mobjects=False, random_seed=None, skip_animations=False):
        super().__init__(renderer, camera_class, always_update_mobjects, random_seed, skip_animations)
        self.logger = DebugLogger(logger_name=__name__, output=True)

    def construct(self):
        with self.animation_context():
            array = VisualArray(["1","+"],scene=self)
            self.play(array.create())
            ops = ["+","-"]

        self.wait(1)
        self.interactive_embed()

if __name__ == "__main__":
    render_scene(SceneName, file=__file__, quality="medium", renderer="opengl", fps=30, write_to_file=False)