from vispy import scene
from vispy.scene.visuals import Ellipse,Text,Rectangle
from vispy.visuals.transforms import MatrixTransform,STTransform
class Node(scene.Node):
    def __init__(self, value,pos=(0,0),parent=None,fill_color=(0.15, 0.55, 0.95, 1.0), 
                 radius=0.5,border_width=2,border_color="white",text_color="white",**kwargs):
        super().__init__(parent=parent,**kwargs)
        self.value = value
        self.body = Ellipse(radius=0.5,center=(0,0),border_width=border_width,border_color=border_color,
                                                 color=fill_color, parent=self)
        self.text = Text(str(value),pos=(0,0),anchor_x='center',anchor_y='center',font_size=20
                         ,color=text_color,parent=self) 
        self.transform = STTransform(translate=pos)
        
    
    def move_to(self, pos):
        
        self.transform.translate = pos
        
    def set_value(self, new_value):
        self.value = new_value
        self.text.text = str(new_value)

class Cell(scene.Node):
    def __init__(self, value,pos=(0,0),parent = None,width=1,height=1,
                 fill_color=(0.15, 0.55, 0.95, 1.0),border_width=2,border_color="white",text_color="white",**kwargs):
        super().__init__(parent,**kwargs)
        self.value = value
        self.body = Rectangle(center=(0,0),width=width, height=height,border_width=border_width,border_color=border_color,
                                                 color=fill_color, parent=self)
        self.text = Text(str(value),pos=(0,0),anchor_x='center',anchor_y='center',font_size=20
                         ,color=text_color,parent=self) 
        self.transform = STTransform(translate=pos)
    
    def move_to(self, pos):
        self.transform.translate = pos
        
    def set_value(self, new_value):
        self.value = new_value
        self.text.text = str(new_value)