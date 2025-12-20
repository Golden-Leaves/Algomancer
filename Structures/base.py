from vispy import scene
from typing import Any,TYPE_CHECKING
from vispy.scene.visuals import Polygon
from vispy.visuals.transforms import STTransform   
from Components.utils import normalize_color
from Components.logging import DebugLogger
from Components.constants import *
from Components.execution_context import get_tracer
if TYPE_CHECKING:
    from Components.scene import AlgoScene
class VisualElementNode(scene.Node):
    def __init__(self, value: Any, pos: tuple[float, float] = (0,0), color: tuple[float, float, float, float] = BLUE_ALGO, border_width: int = 2, border_color: str = "white",
                text_size: int = 20,text_color: tuple[float, float, float, float] = WHITE,
                parent: scene.widgets.ViewBox = None, name: str = None, transforms: list[STTransform] = None,**kwargs) -> None:
        """
        Initializes a VisualElementNode with the given parameters.

        Parameters
        ----------
        value : Any
            The value of the node.
        pos : tuple[float, float]
            The position of the node. Defaults to (0,0).
        color : tuple[float, float, float, float]
            The color of the node. Defaults to `ALGO_BLUE`. Hexadecimal format is also acceptable
        border_width : int
            The width of the border of the node. Defaults to 2.
        border_color : str
            The color of the border of the node. Defaults to `WHITE`.
        parent : scene.Node
            The parent node of this node. Defaults to None.
        name : str
            The name of the node. Defaults to None.
        transforms : list[STTransform]
            The transforms to apply to the node. Defaults to None.

        Returns
        -------
        None
        """
        from Components.execution_context import get_scene
        self.scene = get_scene() if get_scene() else kwargs.pop("scene",None)
        if parent is None:
            parent = self.scene.root
        self.value = value
        super().__init__(parent, name, transforms)
        if self.scene is None:
            raise ValueError("scene cannot be None")
        self.transform = STTransform(scale=(1,1),translate=pos)   
        self.body: Polygon = None
        self._base_color = normalize_color(color)
        self.border_width = border_width
        self.border_color = border_color
        self.text_size = text_size
        self.text_color = text_color
        self.logger = DebugLogger(f"{self.__class__.__name__}",output=True) 
       
    @property
    def pos(self):
        import numpy as np
        return np.array(self.transform.map((0, 0)), dtype=float)
    def __index__(self):
        return int(self.value)
    def __int__(self):
        return int(self.value)
    def __str__(self):
        return str(self.value)
    def evaluate_operation(self,operation:str,other:Any,reversed:bool=False) -> Any:
        """
        Evaluates a given operation with the given value.

        Parameters
        ----------
        operation : str
            The operation to evaluate.
        other : Any
            The value to evaluate with.
        reversed : bool, optional
            Whether to reverse the operation. Defaults to False.

        Returns
        -------
        Any
            The result of the evaluation.
        """
        from Components.utils import get_operation
        if hasattr(other,"value"): other = other.value
        operation = get_operation(operation)
        if not reversed:
            result = operation(self.value,other)
        else:
            result = operation(other,self.value)
        return result
    
    def __add__(self, other):
        tracer = get_tracer()
        if tracer and not tracer.enabled:
            return super().__add__(other)
        self.evaluate_operation(operation="+",other=other)
    def __sub__(self, other):
        tracer = get_tracer()
        if tracer and not tracer.enabled:
            return super().__sub__(other)
        self.evaluate_operation(operation="-",other=other)
    def __mul__(self, other):
        tracer = get_tracer()
        if tracer and not tracer.enabled:
            return super().__mul__(other)
        self.evaluate_operation(operation="*",other=other)
    def __truediv__(self, other):
        tracer = get_tracer()
        if tracer and not tracer.enabled:
            return super().__truediv__(other)
        self.evaluate_operation(operation="/",other=other)
    
    def __floordiv__(self, other):
        tracer = get_tracer()
        if tracer and not tracer.enabled:
            return super().__floordiv__(other)
        self.evaluate_operation(operation="//",other=other)
        
    def __mod__(self, other):
        tracer = get_tracer()
        if tracer and not tracer.enabled:
            return super().__mod__(other)
        self.evaluate_operation(operation="%",other=other)
        
    def __radd__(self, other):
        tracer = get_tracer()
        if tracer and not tracer.enabled:
            return super().__radd__(other)
        self.evaluate_operation(operation="+",other=other,reversed=True)
    def __rsub__(self, other):
        tracer = get_tracer()
        if tracer and not tracer.enabled:
            return super().__rsub__(other)
        self.evaluate_operation(operation="-",other=other,reversed=True)
    def __rmul__(self, other):
        tracer = get_tracer()
        if tracer and not tracer.enabled:
            return super().__rmul__(other)
        self.evaluate_operation(operation="*",other=other,reversed=True)
    def __rtruediv__(self, other):
        tracer = get_tracer()
        if tracer and not tracer.enabled:
            return super().__rtruediv__(other)
        self.evaluate_operation(operation="/",other=other,reversed=True)
        
    def __rfloordiv__(self, other):
        tracer = get_tracer()
        if tracer and not tracer.enabled:
            return super().__rfloordiv__(other)
        self.evaluate_operation(operation="//",other=other,reversed=True)
        
    def __rmod__(self, other):
        tracer = get_tracer()
        if tracer and not tracer.enabled:
            return super().__rmod__(other)
        self.evaluate_operation(operation="%",other=other,reversed=True)
        
    def compare_values(self,operation:str,other:Any, reversed:bool=False):
        """
        Compares two values with a given operation and records an animation if both values are VisualElementNodes.

        Parameters
        ----------
        operation : str
            The operation to perform.
        other : Any
            The value to compare with.
        reversed : bool, optional
            Whether to reverse the operation. Defaults to False.

        Returns
        -------
        bool
            The result of the comparison.
        """
        from Components.animations import Indicate,Parallel
        result = self.evaluate_operation(operation=operation,other=other,reversed=reversed)
        tracer = get_tracer()
        if isinstance(other,VisualElementNode):
            
            color = GREEN if result else RED
            animation = Parallel(Indicate(self,color=color),Indicate(other,color=color))
            tracer.record_animation(animation=animation)
        return result
    
    def __lt__(self, other):
        tracer = get_tracer()
        if tracer and not tracer.enabled:
            return super().__lq__(other)
        return self.compare_values(operation="<",other=other)
    def _gt__(self, other):
        tracer = get_tracer()
        if tracer and not tracer.enabled:
            return super().__gt__(other)
        return self.compare_values(operation=">",other=other)
    def __le__(self, other):
        tracer = get_tracer()
        if tracer and not tracer.enabled:
            return super().__le__(other)
        return self.compare_values(operation="<=",other=other)
    def __ge__(self, other):
        tracer = get_tracer()
        if tracer and not tracer.enabled:
            return super().__ge__(other)
        return self.compare_values(operation=">=",other=other)
    def __eq__(self, other):
        if self is other:
            return True
        tracer = get_tracer()
        if tracer and not tracer.enabled:
            return super().__eq__(other)
        return self.compare_values(operation="==",other=other)
    def __ne__(self, other):
        if self is other: #This is here to prevent vispy's internals from exploding the program
            return False
        tracer = get_tracer()
        if tracer and not tracer.enabled:
            return super().__ne__(other)
        return self.compare_values(operation="!=",other=other)
    


class VisualStructureNode(scene.Node):
    def __init__(self,pos:tuple[float,float]=(0,0), height:int=1,width:int=1,text_color=WHITE,text_size:int=20, body_color=BLUE_ALGO,
                parent = None, name = None, transforms = None,**kwargs):
        from Components.utils import normalize_color
        from Components.execution_context import get_scene
        self.scene = get_scene() if get_scene() else kwargs.pop("scene",None)
        if parent is None:
            parent = self.scene.root
        super().__init__(parent, name, transforms)   
        if self.scene is None:
            raise RuntimeError("Structure created outside of context.")
        self.transform = STTransform(scale=(1,1),translate=pos)          
        self.body: Polygon = None
        self.height = height
        self.width = width
        self.text_color = text_color
        self.text_size = text_size
        self.body_color = self._base_color = normalize_color(body_color)
    
    @property
    def pos(self):
        import numpy as np
        return np.array(self.transform.map((0, 0)), dtype=float)
    
    def get_elements(self):
        from Structures.base import VisualElementNode
        return [element for element in self.children if isinstance(element,VisualElementNode)]
    def get_element(self, index:int):
        from Structures.base import VisualElementNode
        return [element for element in self.children if isinstance(element,VisualElementNode)][index]
    def get_index(self, element:VisualElementNode):
        from Structures.base import VisualElementNode
        return [element for element in self.children if isinstance(element,VisualElementNode)].index(element)
    def compute_layout_offset(self) -> dict[VisualElementNode, tuple[float, float]]:
        """
        Computes the offset of each element in the layout from the center of the structure.

        Returns
        -------
        dict[VisualElementNode, tuple[float, float]]
            A dictionary where the keys are the elements and the values are tuples representing the offset from the center.
        """
        pass   