from Structures.base import VisualElementNode
from abc import ABC,abstractmethod
from vispy.visuals.transforms import STTransform
from vispy.visuals.filters import Alpha
from Components.constants import *
from Components.logging import DebugLogger
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
        self.done = False

    def __repr__(self) -> str:
        cls = self.__class__.__name__
        tgt_type = getattr(self.target, "__class__", type(self.target)).__name__
        return f"<{cls} duration={self.duration:.2f}s done={self.done} target={tgt_type}>"
    def tick(self,elapsed_time:float) -> float:
        """Advances animation by computing progress t from elapsed_time, apply the animation at t, and return t."""
        if self._start_time is None:
            self._start_time = elapsed_time
        elapsed = elapsed_time - self._start_time
        t = elapsed / self.duration #alpha(progress)
        self.apply(t)
        if t >= 1.0:
            self.done = True
        return t      

    def apply(self,t:float):
        t = max(0.0,min(1.0,t))
        self._apply(t)
    @classmethod
    @abstractmethod
    def _apply(self):
        pass
class Sequence:
    def __init__(self,*animations:Animation):
        """
        Initializes a Sequence with the given animations.
        Animations in a sequence will be played *sequentially*.
        
        Parameters
        ----------
        *animations : Animation
            The animations to add to the sequence.

        Attributes
        ----------
        animations : list[Animation]
            The list of animations in the sequence.
        done : bool
            Whether the sequence is done or not.
        logger : DebugLogger
            A logger for debugging purposes.
        """
        self.animations = list(animations)
        self.done = False  
        self.logger = DebugLogger(f"{self.__class__.__name__}",output=True)  
    def remove_current_animation(self) -> None:
         self.animations.pop(0)
    def is_empty(self) -> bool:
        return len(self.animations) == 0
    def get_current_animation(self) -> Animation:
        return self.animations[0]
    def tick(self,elapsed_time:float) -> float:
        """Calls current animation's tick method and returns its return value.
        If no animations exist, sets done to True
        """
        animation = self.get_current_animation()
        t = animation.tick(elapsed_time)
        if animation.done:
            self.remove_current_animation()
            if self.is_empty():
                self.done = True
        return t
    
    
class MoveTo(Animation):
    def __init__(self,target:VisualElementNode,pos:tuple,**kwargs):
        """
        Initializes a MoveTo with the given target and end position.

        Parameters
        ----------
        target : VisualElementNode
            The target of the animation.
        pos : tuple
            The end position of the animation.
        **kwargs
            Optional keyword arguments to pass to the superclass constructor.

        Attributes
        -------
        pos : tuple
            The end position of the animation.
        start_pos : tuple
            The start position of the animation.
        """
        super().__init__(target,**kwargs)
        self.pos = pos
        self._start_pos = None
    def _apply(self,t:float):
        if self._start_pos is None:
            p = self.target.transform.translate
            if p is None:
                p = (0,0)
            self._start_pos = tuple(p)
        x = self._start_pos[0] + (self.pos[0] - self._start_pos[0]) * t
        y = self._start_pos[1] + (self.pos[1] - self._start_pos[1]) * t
        self.target.transform.translate = (x,y)
      
class Wait(Animation):
    def __init__(self,**kwargs):
        super().__init__(target=None,**kwargs)
    def _apply(self,t:float):
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
        
class Scale(Animation):
    def __init__(self, target:VisualElementNode, scale:float=1.0, **kwargs):
        super().__init__(target,**kwargs)
        self.scale = scale
        self._start_scale = None
    def _apply(self,t:float):
        if self._start_scale is None:
            s = self.target.transform.scale
            if s is None:
                s = (1.0,1.0)
            self._start_scale = tuple(s)
            
        sx = self._start_scale[0] + (self.scale - self._start_scale[0]) * t
        sy = self._start_scale[1] + (self.scale - self._start_scale[1]) * t
        self.target.transform.scale = (sx,sy)
    
class Highlight(Animation): #Update this to keep start_color as well
    def __init__(self, target:VisualElementNode,color=YELLOW,**kwargs):
        from Components.utils import normalize_color
        super().__init__(target, **kwargs)
        self.color = normalize_color(color)
        self._start_color = None
    def _apply(self,t:float):
        from vispy.color import ColorArray
        from Components.utils import normalize_color
        if self._start_color is None:
            c: ColorArray = self.target.body.color
            self._start_color = normalize_color(c.rgba)
            
            
        r = self._start_color[0] + (self.color[0] - self._start_color[0]) * t
        g = self._start_color[1] + (self.color[1] - self._start_color[1]) * t
        b = self._start_color[2] + (self.color[2] - self._start_color[2]) * t
        a = self._start_color[3] + (self.color[3] - self._start_color[3]) * t
        target_color = (r,g,b,a)
        self.target.body.color = target_color
        
class Unhighlight(Animation):
    def __init__(self, target,**kwargs):
        super().__init__(target,**kwargs)
    def _apply(self,t:float):
        from vispy.color import ColorArray
        from Components.utils import normalize_color
        target_body_color = normalize_color(self.target.body.color.rgba)
        r = target_body_color[0] + (self.target._base_color[0] - target_body_color[0]) * t
        g = target_body_color[1] + (self.target._base_color[1] - target_body_color[1]) * t
        b = target_body_color[2] + (self.target._base_color[2] - target_body_color[2]) * t
        a = target_body_color[3] + (self.target._base_color[3] - target_body_color[3]) * t
        target_color = (r,g,b,a)
        self.target.body.color = target_color
    
