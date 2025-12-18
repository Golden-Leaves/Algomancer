import time
from Components.animations import Animation
class Timeline:
    def __init__(self):
        """
        Initializes a Timeline instance.

        The Timeline is responsible for managing active animations and
        updating their state based on the elapsed time.

        Attributes
        ----------
        active : list[Animation] | list[Sequence]
            The list of active animations or sequences.
        elapsed_time : float
            The total elapsed time in seconds since the Timeline was initialized.
        """
        from Components.animations import Sequence
        self.active: list[Animation|Sequence] = []
        self.elapsed_time:float = 0.0
        
    def add_animation(self,animation:Animation):
        """
        Adds an animation to the timeline.
        
        Parameters
        ----------
        animation : Animation
            The animation to add to the timeline.
        """
        self.active.append(animation)   
        
    def update(self,dt:float):
        """
        Updates the timeline by the given delta time.

        Parameters
        ----------
        dt : float
            The delta time in seconds.

        Returns
        -------
        None
        """
        from Components.animations import Sequence
        self.elapsed_time += dt
        finished = []
        
        for track in self.active:                        
            t:float = track.tick(elapsed_time=self.elapsed_time)
            if track.done:
                finished.append(track)
                
        for finished_animation in finished:
            self.active.remove(finished_animation)
            
            