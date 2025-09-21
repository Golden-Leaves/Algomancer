from Structures.arrays import VisualArray,Cell
from manim import *
def bubble_sort(array:VisualArray):
    """Sorts the array with Bubble Sort, animating each step."""
    n = len(array.cells)
    for i in range(n):
        for j in range(n - i - 1):
            cell_1:Cell = array.cells[j]
            cell_2:Cell = array.cells[j + 1]
            if cell_1.value > cell_2.value:
                array.play(
                    array.highlight(j),
                    array.highlight(j + 1),
                    runtime=0.2
                )
                array.play(array.swap(j, j + 1))
                array.play(
                    array.unhighlight(j),
                    array.unhighlight(j + 1),
                    runtime=0.2
                )

def insertion_sort(array:VisualArray):
    """Sorts the array with Insertion Sort, animating each step."""
    n = len(array.cells)
    for i in range(n):
        key = array.cells[i]
        array.play(array.highlight(key))
        j = i - 1

        while j >= 0 and array.cells[j].value > key.value:
            j_cell = array.cells[j]
            array.play(array.highlight(j_cell, color=RED, runtime=0.5))
            j -= 1
            array.play(array.unhighlight(j_cell))

        if j + 1 != i:  # only shift if new position is different
            array.play(array.shift_cell(from_idx=i, to_idx=j + 1))

        array.play(array.unhighlight(key))
        array.play(array.outline(key))
