from manim import *
from Structures.arrays import VisualArray
from Algorithms.sorting import bubble_sort,insertion_sort
from Algorithms.searching import linear_search
from helpers import render_scene
import numpy as np
import random

class HashTableScene(Scene):
    pass

if __name__ == "__main__":
    render_scene(HashTableScene,file=__file__,quality="medium")