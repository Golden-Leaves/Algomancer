from manim import *
from Structures.linked_lists import VisualLinkedList
from Algorithms.sorting import bubble_sort,insertion_sort
from Algorithms.searching import linear_search
from helpers import render_scene
import numpy as np
import random

class LinkedListScene(Scene):
    def construct(self):
        ll = VisualLinkedList([1,2,3,4],scene=self)
        ll.play(ll.create())
        self.wait(0.5)
        ll.play(ll.append(1),ll.append(2),ll.append(43))
        
        self.wait(1)
if __name__ == "__main__":
    render_scene(LinkedListScene,file=__file__,quality="medium")