from manim import *
from Structures.linked_lists import VisualLinkedList
from Algorithms.sorting import bubble_sort,insertion_sort
from Algorithms.searching import linear_search
from helpers import render_scene
import numpy as np
import random

class LinkedListScene(Scene):
    ll = VisualLinkedList([1,2,3,4])

if __name__ == "__main__":
    render_scene(LinkedListScene,file=__file__,quality="medium")