import time
from Components.animations import Animation
class Timeline:
    def __init__(self):
        self.active: list[Animation] = []
        self.elapsed_time:float = 0.0
    def play(self,animation:Animation | list[Animation]):
        animations = animation if isinstance(animation, list) else [animation]
        for animation in animations:
            animation._start_time = self.elapsed_time
            self.active.append(animation)   
        
    def update(self,dt:float):
        self.elapsed_time += dt
        finished = []
        for animation in self.active:
            elapsed = self.elapsed_time - animation._start_time
            t = elapsed / animation.duration #alpha(progress)
            animation.apply(t)
            if t >= 1.0:
                finished.append(animation)
        for finished_animation in finished:
            self.active.remove(finished_animation)
            
            