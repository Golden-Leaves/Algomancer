from manim import *
from Structures.hash_tables import VisualHashTable
from Components.logging import DebugLogger
from Components.render_scene import render_scene
from Components.runtime import AlgoScene


class HashTableScene(AlgoScene):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.logger = DebugLogger(__name__)
        
    def construct(self):
        with self.animation_context():
            hash_table = VisualHashTable(data={12:123,"hi":15},scene=self)
            hash_table.play(hash_table.create())
            self.logger.log_stucture_state(hash_table, label="After hash table creation", level="INFO")
            hash_table.play(hash_table.highlight(element="hi"))
            hash_table.play(hash_table.unhighlight(element="hi"))

        self.wait(1)
        self.interactive_embed()

if __name__ == "__main__":
    render_scene(HashTableScene,file=__file__,quality="medium",renderer="opengl")
