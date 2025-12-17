from Structures.base import VisualElementNode
from abc import ABC,abstractmethod
from vispy.visuals.transforms import STTransform
from vispy.visuals.filters import Alpha
#Add apply_on_children() to apply effect on all children when we implement VisualStructureNode
class Animation(ABC):
    def __init__(self,target:VisualElementNode,duration:float=1.0,**kwargs):
        """
        Initializes an Animation with the given target and duration.

        Parameters
        ----------
        target : VisualElementNode
            The target of the animation.
        duration : float, optional
            The duration of the animation in seconds. Defaults to 1.0.
        **kwargs
            Optional keyword arguments to pass to the subclass constructor.

        Attributes
        ----------
        duration : float
            The duration of the animation in seconds.
        target : VisualElementNode
            The target of the animation.
        _start_time : float
            The start time of the animation in seconds from the scene's elapsed time.
        """
        self.duration = float(duration) 
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
        """
        Initializes a MoveTo with the given target and end position.

        Parameters
        ----------
        target : VisualElementNode
            The target of the animation.
        end_pos : tuple
            The end position of the animation.
        **kwargs
            Optional keyword arguments to pass to the superclass constructor.

        Attributes
        -------
        end_pos : tuple
            The end position of the animation.
        start_pos : tuple
            The start position of the animation.
        """
        super().__init__(target,**kwargs)
        self.end_pos = end_pos
        self.start_pos = target.pos
    def _apply(self,t:float):
        x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * t
        y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * t
        self.target.transform.translate = (x,y)        
        
class Wait(Animation):
    pass
     
class FadeIn(Animation):
    
    def __init__(self, target: VisualElementNode, **kwargs) -> None:
        """
        Initializes a FadeIn with the given target.

        Parameters
        ----------
        target : VisualElementNode
            The target of the animation.

        Returns
        -------
        None
        """
        super().__init__(target, **kwargs)
        if not hasattr(target, "_alpha_filter"):
            a: Alpha = Alpha(1.0)
            target.body.attach(a)
            if hasattr(target,"text"): target.text.attach(a)
            target._alpha_filter = a
        self.alpha: float = target._alpha_filter.alpha
    def _apply(self,t:float):
        self.target._alpha_filter.alpha = self.alpha * t

class FadeOut(Animation):
    def __init__(self, target: VisualElementNode, **kwargs) -> None:
        """
        Initializes a FadeOut with the given target.
        
        Parameters
        ----------
        target : VisualElementNode
            The target of the animation.

        Returns
        -------
        None
        """
        super().__init__(target, **kwargs)
        if not hasattr(target, "_alpha_filter"):
            a: Alpha = Alpha(1.0)
            target.body.attach(a)
            if hasattr(target,"text"): target.text.attach(a)
            target._alpha_filter = a
        self.alpha = target._alpha_filter.alpha
    def _apply(self,t:float):
        self.target._alpha_filter.alpha = self.alpha * (1-t)

