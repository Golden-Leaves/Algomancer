from manim import *
import numpy as np
from typing import Any
from Structures.arrays import Cell
from Structures.base import VisualStructure,VisualElement
from Utils.logging_config import setup_logging

class Entry(VisualElement):
    def __init__(self, master = None, kv_pair:tuple[any,any] = None, label = None,
                 entry_height:int=1,entry_width:int=4,**kwargs):
        if kv_pair is None or not isinstance(kv_pair,tuple):
            raise ValueError("kv_pair must be a (key,value) tuple")
        
        self.entry_height = entry_height
        self.entry_width = entry_width
        self.key = kv_pair[0]
        self.value = kv_pair[1]
        self.value_cell:Cell = Cell(value=kv_pair[1],master=master,cell_width=entry_width*0.75,cell_height=entry_height)
        self.key_cell:Cell = Cell(value=kv_pair[0],master=master,cell_width=entry_width*0.25,cell_height=entry_height)
        self.value_cell.move_to(RIGHT * entry_width*0.25 / 2) #Move center to the right edge of key_cell
        self.key_cell.move_to(LEFT * entry_width*0.75 / 2) #We escape the encompassing value_cell
        body = VGroup(self.key_cell,self.value_cell)
        super().__init__(body, master, kv_pair, label, **kwargs)
    
class VisualHashTable(VisualStructure):
    def __init__(self,data:dict,scene,element_width=4,element_height=1,text_color=WHITE,label=None,**kwargs):
        self.logger = setup_logging(logger_name="algomancer.hash_tables",output=False)
        super().__init__(scene,label,**kwargs)
        self._raw_data = data
        self._bucket_count = max(1,len(data)) #Division by 0...
        self.text_color = text_color
        self.element_width = element_width
        self.element_height = element_height
        self.text_color = WHITE
        self.entries:dict[any,Entry] = {} 
        self._instantialized = False
    def __len__(self):
        return len(self.entries)
    
    def _hash_key(self,key):
        if isinstance(key,int):
            raw = key
        else:
            raw = sum(ord(char) for char in str(key))
        return raw % self._bucket_count

    def _get_entry(self, key: Any) -> Entry:
        """
        Retrieve the Entry associated with ``key`` while enforcing hash-table specific errors.

        Raises
        ------
        KeyError
            If the key is not present or the bucket's visuals are out of sync.
        """
        bucket = self._hash_key(key)
        entry = self.entries.get(key, None)
        try:
            slot = self.get_element(bucket)
        except (IndexError, TypeError, ValueError) as exc:
            raise KeyError(f"HashTable bucket lookup failed for key {key!r}") from exc

        if entry is None or slot is None:
            raise KeyError(f"Key {key!r} not present in hash table.")

        if slot is not entry:
            raise KeyError(
                f"Key {key!r} mapped to bucket {bucket} but visuals are out of sync."
            )

        return entry
    def __getitem__(self, key):
        element = 
    def _highlight_entry(self,element:any|VisualElement,color:ManimColor=YELLOW,opacity:float = 0.5):
        """Sequentially highlights the entry's key cell then value cell(custom highlight sequence)"""
        anims = []
        element:Entry = self.get_element(element)
        anims.append(super().highlight(element=element.key_cell,color=color,opacity=opacity,runtime=0.3))
        anims.append(super().unhighlight(element=element.key_cell,color=color,opacity=opacity,runtime=0.2))
        anims.append(super().highlight(element=element.value_cell,color=color,opacity=opacity,runtime=0.3))
        anims.append(super().unhighlight(element=element.value_cell,color=color,opacity=opacity,runtime=0.2))
        return Succession(*anims)
    
    
    def create(self,entries:list[Entry]=None,runtime:float=0.5):
        if not self._instantialized:  #instantiate cell geometry without animation
            self.elements =  [None] * self._bucket_count #Prefill stuff first so the hashed key does not go out-of-bounds
            anchor = np.array(self.get_center())
            if not np.allclose(anchor, 0):
                self.pos = anchor
            for key,data in self._raw_data.items():
                entry = Entry(master=self,kv_pair=(key,data),label=self.label)
                hashed_key = self._hash_key(key=key)
                self.entries[key] = entry
                self.elements[hashed_key] = entry
                self.add(entry)
    
            self.move_to(self.pos)
            self.set_opacity(0)
            self._instantialized = True
        
        if not self.scene:
            return None
        
        self.pos = np.array(self.get_center())
        self.set_opacity(1)
        runtime = max(0.5,runtime)
        if entries is None:
            entries = self.entries.values()
        if not entries:
            return Wait(1e-6)
    
        entry_anims = [AnimationGroup(entry.key_cell.create(),entry.value_cell.create()) for entry in entries]
        return AnimationGroup(
            *entry_anims,
            lag_ratio=0.1,
            runtime=runtime
        )
