from vispy import scene,app
from vispy.util.event import Event
from Components.timeline import Timeline
from Components.logging import DebugLogger
from Components.animations import Animation
class AlgoScene:
    def __init__(self) -> None:
        """
        Initializes an AlgoScene instance.
        Responsible for rendering visual
        elements and handling user input.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.logger: DebugLogger = DebugLogger(f"{self.__class__.__name__}",output=True)
        self.canvas: scene.SceneCanvas = scene.SceneCanvas(keys='interactive',show=True,size=(800,600),title="Algomancer")
        self.view: scene.widgets.ViewBox = self.canvas.central_widget.add_view()
        self.view.camera = scene.cameras.PanZoomCamera(aspect=1)
        self.view.camera.set_range(x=(-5,5),y=(-5,5))
        self.timeline: Timeline = Timeline()
        self._timer: app.Timer = app.Timer(interval=0,connect=self._on_tick,start=True)
        self.root: scene.Node = self.view.scene
        
    def play(self,track:Animation | list[Animation]):
        """
        Play the given animation(s) in the scene.
        Note that animation play is paralell by default, unless you use `Sequence`.
        
        Parameters
        ----------
        animation : Animation | list[Animation]
            The animation(s) to play. Can be a single Animation or a list of Animations.

        Returns
        -------
        None
        """
        tracks = track if isinstance(track, list) else [track]
        for animation in tracks:
            self.timeline.add_animation(animation)
    def _on_tick(self,event:Event):
        self.timeline.update(event.dt)
        self.canvas.update()
        