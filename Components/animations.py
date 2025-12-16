from abc import ABC,abstractmethod
class Animation(ABC):
    def __init__(self,duration:float,target:object,**kwargs):
        self.duration = duration 
        self.target = target
        
    def apply(self,t:float):
        t = max(0.0,min(1.0,t))
        self._apply(t)
    @classmethod
    @abstractmethod
    def _apply(self):
        pass

class MoveTo(Animation):
    def __init__(self,duration:float,target:object,**kwargs):
        super().__init__(duration,target,**kwargs)