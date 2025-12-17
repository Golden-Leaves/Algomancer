from vispy import scene
from typing import Any,TYPE_CHECKING
from vispy.scene.visuals import Polygon
from vispy.visuals.transforms import STTransform   
if TYPE_CHECKING:
    from Components.scene import AlgoScene
class VisualElementNode(scene.Node):
    def __init__(self, value: Any, scene: "AlgoScene", pos: tuple[float, float] = (0,0), color: tuple[float, float, float, float] = (0.15, 0.55, 0.95, 1.0), border_width: int = 2, border_color: str = "white",
                 parent: scene.widgets.ViewBox = None, name: str = None, transforms: list[STTransform] = None) -> None:
        """
        Initializes a VisualElementNode with the given parameters.

        Parameters
        ----------
        value : Any
            The value of the node.
        pos : tuple[float, float]
            The position of the node. Defaults to (0,0).
        color : tuple[float, float, float, float]
            The color of the node. Defaults to (0.15, 0.55, 0.95, 1.0).
        border_width : int
            The width of the border of the node. Defaults to 2.
        border_color : str
            The color of the border of the node. Defaults to "white".
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
        if parent is None:
            parent = scene.root
        super().__init__(parent, name, transforms)
        if scene is None:
            raise ValueError("scene cannot be None")
        self.scene = scene
        self.body: Polygon = None
        self.value = value
        self._pos = pos
        self.color = color
        self.border_width = border_width
        self.border_color = border_color
    @property
    def pos(self):
        return self._pos
    
    @pos.setter
    def pos(self,pos):
        self._pos = pos
        