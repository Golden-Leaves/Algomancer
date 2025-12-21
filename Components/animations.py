from __future__ import annotations
from Structures.base import VisualElementNode,VisualStructureNode
from abc import ABC,abstractmethod
from vispy.visuals.filters import Alpha
from Components.constants import *
from Components.logging import DebugLogger
from collections import deque
from typing import Callable
#Add apply_on_children() to apply effect on all children when we implement VisualStructureNode
class Animation(ABC):
    def __init__(self, target: VisualElementNode|VisualStructureNode, duration: float = 1.0, start_offset: float = 0.0, **kwargs):
        """
        Initializes an Animation with the given target and duration.

        Parameters
        ----------
        target : VisualElementNode|VisualStructureNode
            The target of the animation.
        duration : float, optional
            The duration of the animation in seconds. Defaults to 1.0.
        start_offset : float, optional
            The start offset of the animation in seconds. Defaults to 0.0.
        **kwargs
            Optional keyword arguments to pass to the subclass constructor.

        Attributes
        ----------
        _duration : float
            The duration of the animation in seconds.
        _target : VisualElementNode|VisualStructureNode
            The target of the animation.
        _start_time : float
            The start time of the animation in seconds from the scene's elapsed time.
        _start_offset : float
            The start offset of the animation in seconds.
        """
        self.duration = max(1e-6,max(0.0,duration))
        self.target = target
        self._start_time = None
        self.start_offset = start_offset
        self.done = False
        self._on_finish: list[Callable] = []
    def add_on_finish(self,callback) -> Animation:
        """
        Registers a callback to call when the animation is finished.

        Parameters
        ----------
        callback : Callable
            The callback to call when the animation is finished.
        """
        self._on_finish.append(callback)
        return self
    def _finish(self):
        """
        Called when the animation is finished. If the animation is already finished, does nothing.
        Otherwise, sets the animation as finished and calls all the callbacks registered with `add_on_finish`.
        """

        if self.done:
            return
        self.done = True
        for callback in self._on_finish:
            callback()
    def __repr__(self) -> str:
        cls = self.__class__.__name__
        tgt_type = getattr(self.target, "__class__", type(self.target)).__name__
        return f"<{cls} duration={self.duration:.2f}s done={self.done} target={tgt_type}>"
    def tick(self,elapsed_time:float) -> float:
        """Advances animation by computing progress t from elapsed_time, apply the animation at t, and return t."""
        if self._start_time is None:
            self._start_time = elapsed_time + self.start_offset
        elapsed = elapsed_time - self._start_time
        t = max(0.0,min(1.0,elapsed / self.duration)) #alpha(progress)
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
        self.animations = deque(list(animations))
        self.done = False  
        self.logger = DebugLogger(f"{self.__class__.__name__}",output=True)  
        self.duration = sum([animation.duration for animation in self.animations]) if self.animations else 0.0 
        self._on_finish: list[Callable] = []
    def add_on_finish(self,callback) -> Sequence:
        self._on_finish.append(callback)
        return self
    def _finish(self): 
        if self.done:
            return
        self.done = True
        for callback in self._on_finish:
            callback()
    def remove_current_animation(self) -> None:
         self.animations.popleft()
    def is_empty(self) -> bool:
        return len(self.animations) == 0
    def get_current_animation(self) -> Animation:
        return self.animations[0] #Add .finish() call to Aniamtion
    def tick(self,elapsed_time:float) -> float:
        """Calls current animation's tick method and returns its return value.
        If no animations exist, sets done to True
        """
        animation = self.get_current_animation()
        if isinstance(animation,Deferred):self.animations[0] = animation = animation.build()
        t = animation.tick(elapsed_time)
        if animation.done:
            animation._finish()
            self.remove_current_animation()
            if self.is_empty():
                self._finish()
                self.done = True
        return t 
class Parallel:
    def __init__(self,*animations:Animation,lag_ratio:float=0.0):
        self.animations = list(animations)
        self.lag_ratio = float(lag_ratio)
        self.done = False
        #Basically a scale
        self.group_duration = max([animation.duration for animation in self.animations]) #Group lasts as long as the longest animation
        self.compute_start_offsets(animations=animations,lag_ratio=lag_ratio,group_duration=self.group_duration)
        self.duration = max([(animation.duration + animation.start_offset) for animation in self.animations]) if self.animations else 0.0
        self._on_finish: list[Callable] = []
    def add_on_finish(self,callback) -> Parallel:
        self._on_finish.append(callback)
        return self
    def _finish(self):
        if self.done:
            return
        self.done = True
        for callback in self._on_finish:
            callback()
    def compute_start_offsets(self,animations:list[Animation],lag_ratio:float,group_duration:float) -> None:
        for i,anim in enumerate(animations):
            anim.start_offset = i * lag_ratio * group_duration
    def is_empty(self) -> bool:
        return len(self.animations) == 0
    def tick(self,elapsed_time:float) -> None:
        finished = []
        for i in range(len(self.animations)):
            animation = self.animations[i]
            if isinstance(animation,Deferred):self.animations[i] = animation = animation.build()
            t  = animation.tick(elapsed_time)
            if animation.done:
                animation._finish()
                finished.append(animation)  
        for finished_animation in finished:
            self.animations.remove(finished_animation)
        if self.is_empty():
            self._finish()
            self.done = True

    def __repr__(self) -> str:
        """Short debug view: <Parallel n=X lag=Y duration=Zs children=[A,B,...]>"""
        names = [getattr(a, "__class__", type(a)).__name__ for a in self.animations]
        if len(names) > 3:
            names = names[:3] + ["..."]
        return (
            f"<Parallel n={len(self.animations)} lag={self.lag_ratio:.2f} "
            f"duration={getattr(self, 'duration', 0.0):.2f}s children={names}>"
        )
class Deferred:
    def __init__(self, builder: Callable, **kwargs) -> None:
        self.builder = builder
    def build(self) -> Animation|Sequence|Parallel:
        return self.builder()
        
class MoveTo(Animation):
    def __init__(self,target:VisualElementNode|VisualStructureNode,pos:tuple,**kwargs):
        """
        Initializes a MoveTo with the given target and end position.

        Parameters
        ----------
        target : VisualElementNode|VisualStructureNode
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
            # p = self.target.pos
            if p is None:
                p = (0,0)
            self._start_pos = tuple(p)
        x = self._start_pos[0] + (self.pos[0] - self._start_pos[0]) * t
        y = self._start_pos[1] + (self.pos[1] - self._start_pos[1]) * t
        self.target.transform.translate = (x,y)
      
class Wait(Animation):
    def __init__(self,duration:float=1.0,**kwargs):
        super().__init__(target=None,duration=float(duration),**kwargs)
    def _apply(self,t:float):
        pass
     
class FadeIn(Animation):
    
    def __init__(self, target: VisualElementNode|VisualStructureNode, **kwargs) -> None:
        """
        Initializes a FadeIn with the given target.

        Parameters
        ----------
        target : VisualElementNode|VisualStructureNode
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
    def __init__(self, target: VisualElementNode|VisualStructureNode, **kwargs) -> None:
        """
        Initializes a FadeOut with the given target.
        
        Parameters
        ----------
        target : VisualElementNode|VisualStructureNode
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
    def __init__(self, target:VisualElementNode|VisualStructureNode, scale:float=1.0, **kwargs):
        super().__init__(target,**kwargs)
        self.scale = float(scale)
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
    def __init__(self, target:VisualElementNode|VisualStructureNode,color=YELLOW,**kwargs):
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
        from Components.utils import normalize_color
        target_body_color = normalize_color(self.target.body.color.rgba)
        r = target_body_color[0] + (self.target._base_color[0] - target_body_color[0]) * t
        g = target_body_color[1] + (self.target._base_color[1] - target_body_color[1]) * t
        b = target_body_color[2] + (self.target._base_color[2] - target_body_color[2]) * t
        a = target_body_color[3] + (self.target._base_color[3] - target_body_color[3]) * t
        target_color = (r,g,b,a)
        self.target.body.color = target_color
    
class Indicate(Animation):
    def __init__(self, target,color=YELLOW,scale:float=1.5, **kwargs):
        super().__init__(target,duration=1.5, **kwargs)
        from Components.utils import normalize_color
        self.color = normalize_color(color)
        self._start_color = None
        self.scale = float(scale)
        self._start_scale = None
    def _apply(self,t:float):
        from Components.utils import normalize_color
        if t <= 0.5:
            if self._start_color is None:
                c = self.target.body.color
                self._start_color = normalize_color(c.rgba)
            if self._start_scale is None:
                s = self.target.transform.scale
                if s is None:
                    s = (1.0,1.0)
                self._start_scale = tuple(s)
                
            r = self._start_color[0] + (self.color[0] - self._start_color[0]) * t * 2
            g = self._start_color[1] + (self.color[1] - self._start_color[1]) * t * 2
            b = self._start_color[2] + (self.color[2] - self._start_color[2]) * t * 2
            a = self._start_color[3] + (self.color[3] - self._start_color[3]) * t * 2
            target_color = (r,g,b,a)
            self.target.body.color = target_color
            
            sx = self._start_scale[0] + (self.scale - self._start_scale[0]) * t
            sy = self._start_scale[1] + (self.scale - self._start_scale[1]) * t
            self.target.transform.scale = (sx,sy)
        else:
            r = self.color[0] + (self._start_color[0] - self.color[0]) * (t-0.5) * 2
            g = self.color[1] + (self._start_color[1] - self.color[1]) * (t-0.5) * 2
            b = self.color[2] + (self._start_color[2] - self.color[2]) * (t-0.5) * 2            
            a = self.color[3] + (self._start_color[3] - self.color[3]) * (t-0.5) * 2
            target_color = (r,g,b,a)
            self.target.body.color = target_color
            
            sx = self.scale + (self._start_scale[0] - self.scale) * (t-0.5) * 2
            sy = self.scale + (self._start_scale[1] - self.scale) * (t-0.5) * 2
            self.target.transform.scale = (sx,sy)
