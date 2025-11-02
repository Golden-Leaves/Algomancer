from manim import *
from Structures.hash_tables import VisualHashTable
from Components.logging import setup_logging
from Components.render_scene import render_scene
from Components.runtime import AlgoScene


class HashTableScene(AlgoScene):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.logger = setup_logging("algomancer.hash_table_prod")
        
    def construct(self):
        with self.animation_context():
            hash_table = VisualHashTable(data={12:123,"hi":15},scene=self)
            hash_table.play(hash_table.create())
            hash_table.log_state(label="After hash table creation",level="INFO")
            hash_table.play(hash_table.highlight(element=1))
            hash_table.play(hash_table.unhighlight(element=1))

        self.wait(1)
        self.interactive_embed()

if __name__ == "__main__":
    render_scene(HashTableScene,file=__file__,quality="medium",renderer="opengl")
