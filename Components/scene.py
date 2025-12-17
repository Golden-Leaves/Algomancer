from vispy import scene,app
from vispy.util.event import Event
from Components.timeline import Timeline
from Components.logging import DebugLogger
from Components.animations import Animation
class AlgoScene:
    def __init__(self):
        self.logger = DebugLogger(f"{self.__class__.__name__}",output=True)
        self.canvas = scene.SceneCanvas(keys='interactive',show=True,size=(800,600))
        self.view = self.canvas.central_widget.add_view()
        self.view.camera = scene.cameras.PanZoomCamera(aspect=1)
        self.view.camera.set_range(x=(-5,5),y=(-5,5))
        self.timeline = Timeline()
        self._timer = app.Timer(interval=0,connect=self._on_tick,start=True)
        self.root = self.view.scene
        
    def play(self,animation:Animation | list[Animation]):
        self.timeline.play(animation)
    def _on_tick(self,event:Event):
        self.timeline.update(event.dt)
        self.canvas.update()
        