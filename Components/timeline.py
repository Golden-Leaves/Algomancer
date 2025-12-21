import time
from Components.animations import Animation,Parallel,Sequence
from collections import deque
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
        from Components.logging import DebugLogger
        self.active: deque[Animation|Sequence] = deque()
        self.elapsed_time:float = 0.0
        self.logger = DebugLogger(f"{self.__class__.__name__}",output=True)
        
    def add_track(self,track:Animation):
        """
        Adds a track to the timeline.
        
        Parameters
        ----------
        track : Animation
            The track to add to the timeline.
        """
        self.active.append(track)   
    
    def get_current_track(self) -> Animation|Sequence|Parallel|None:
        return self.active[0] if len(self.active) > 0 else None
        
    def pop_current_track(self) -> Animation|Sequence|Parallel|None:
        return self.active.popleft()
    
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
        self.elapsed_time += dt
        track = self.get_current_track()       
        t:float = track.tick(elapsed_time=self.elapsed_time)
        if track.done:
            self.pop_current_track()
            
                
        
            
            