from Structures.base import VisualElementNode
from abc import ABC,abstractmethod
from vispy.visuals.transforms import STTransform
class Animation(ABC):
    def __init__(self,target:VisualElementNode,duration:float=1.0,**kwargs):
        self.duration = duration 
        self.target = target
        self._start_time:float = None
        
    def apply(self,t:float):
        t = max(0.0,min(1.0,t))
        self._apply(t)
    @classmethod
    @abstractmethod
    def _apply(self):
        pass

class MoveTo(Animation):
    def __init__(self,target:VisualElementNode,end_pos:tuple,**kwargs):
        super().__init__(target,**kwargs)
        self.end_pos = end_pos
        self.start_pos = target.pos
    def _apply(self,t:float):
        dx = (self.end_pos[0] - self.start_pos[0]) * t
        dy = (self.end_pos[1] - self.start_pos[1]) * t
        x = self.start_pos[0] + dx
        y = self.start_pos[1] + dy
        self.target.transform.translate = (x,y)        
     
        
        