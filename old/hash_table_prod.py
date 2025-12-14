from manim import *
from Structures.hash_tables import VisualHashTable
from Components.logging import DebugLogger
from Components.render_scene import render_scene
from Components.runtime import AlgoScene
from Components.animations import slide_element

class HashTableScene(AlgoScene):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.logger = DebugLogger(__name__)
        
    def construct(self):
        with self.animation_context():
            hash_table = VisualHashTable(data={12:123,"hi":15},scene=self,text_size=1)
            hash_table.play(hash_table.create())
            # hash_table[12] = "new" 
            # hash_table[67] = "smth"
            # hash_table.move_to(RIGHT)
            self.play(slide_element(element=hash_table._get_entry("hi"),target_pos=LEFT,align="y"))
            
            # hash_table.pop(key="hi")
#TODO: Entry's psoition is flipped after move_to()
        self.wait(1)
        self.interactive_embed()

if __name__ == "__main__":
    render_scene(HashTableScene,file=__file__,quality="medium",renderer="opengl",slides=False)
