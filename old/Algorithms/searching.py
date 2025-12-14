from Structures.arrays import VisualArray,Cell
from typing import Any


def linear_search(array:VisualArray,target:Any) -> Cell|int:
    
    for i in range(array.length):
        cell:Cell = array[i]
        array.play(array.highlight(cell),array.unhighlight(cell))
        
        if cell.value == target:
            return cell
        

    return -1
        
        
