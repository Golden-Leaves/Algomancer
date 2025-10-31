from manim import *
import numpy as np
from typing import Any
from Structures.arrays import Cell
from Structures.base import VisualStructure,VisualElement
from Utils.logging_config import setup_logging
from Utils.runtime import is_animating
from Utils.utils import LazyAnimation,hop_element,slide_element
class Entry(VisualElement):
    def __init__(self, master = None, kv_pair:tuple[Any,Any] = None,hash=None, label = None,
                 entry_height:int=1,entry_width:int=4,**kwargs):
        if kv_pair is None or not isinstance(kv_pair,tuple):
            raise ValueError("kv_pair must be a (key,value) tuple")
        
        self.entry_height = entry_height
        self.entry_width = entry_width
        self.value_cell:Cell = Cell(value=kv_pair[1],master=master,cell_width=entry_width*0.75,cell_height=entry_height)
        self.key_cell:Cell = Cell(value=kv_pair[0],master=master,cell_width=entry_width*0.25,cell_height=entry_height)
        self.value_cell.move_to(RIGHT * entry_width*0.25 / 2) #Move center to the right edge of key_cell
        self.key_cell.move_to(LEFT * entry_width*0.75 / 2) #We escape the encompassing value_cell
        body = VGroup(self.key_cell,self.value_cell)
        body.move_to(ORIGIN) #Moves the body back to origin since the movement shifts it
        super().__init__(body, master, kv_pair, label, **kwargs)
        
        
    @property
    def value(self):
        return self.value_cell.value
    @value.setter
    def value(self,new_value):
        self.value_cell.value = new_value
        
    @property
    def key(self):
        return self.key_cell.value
    @key.setter
    def key(self,new_key):
        self.key_cell.value = new_key

    def set_value(self,value:Any,color:ManimColor,runtime:float=0.5):
        return self.value_cell.set_value(value=value,color=color)
    
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
        self.entries:dict[Any,Entry] = {} 
        self._instantialized = False
    def __len__(self):
        return len(self.entries)
    # @classmethod
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
        entry = self._get_entry(key=key)
        if self.scene and is_animating() and not self.scene.in_play:
            self.play(self._highlight_entry(element=key))
        return entry
    def __setitem__(self, key, value):
        entry = self._get_entry(key=key)
        self.play(entry.set_value(value=value))
        if self.scene and is_animating() and not self.scene.in_play:
            self.play(self._highlight_entry(element=key))
            
    def pop(self,key:Any|Entry,default=None,runtime=0.5) -> Any:
        keys = list(self.entries)
        mid = len(keys) // 2
        previous_entries = []
        anims = []
        popped_entry = None
        
        for _key in keys:
            try:
                entry = self._get_entry(key=_key)
                if _key == key or entry is key: #Found entry
                    bucket = self._hash_key(key=key)
                    popped_entry = entry
                    anims.append(FadeOut(entry))
                    break
                previous_entries.append(entry)
            except KeyError as e:
                if default is not None:
                    return default
                raise e
            
        popped_cell_index = keys.index(popped_entry.key)
        if popped_cell_index <= mid:
            for idx in range(popped_cell_index - 1,-1,-1):
                from_key:Entry = self._get_entry(keys[idx])
                to_key:Entry = self._get_entry(keys[idx + 1])
                anims.append(slide_element(element=from_key,target_pos=to_key.center))
        else:
            for idx in range(popped_cell_index + 1,len(keys)):
                from_key:Entry = self._get_entry(keys[idx])
                to_key:Entry = self._get_entry(keys[idx - 1])
                anims.append(slide_element(element=from_key,target_pos=to_key.center))
        
        if self.scene and is_animating() and not self.scene.in_play:
            self.play(*anims,runtime=runtime)    
            
        self.elements[bucket] = None
        self.entries.pop(popped_entry.key)
        self.remove(popped_entry)
        self.logger.debug("array.pop index=%s -> len=%d", key, len(self.elements))
        return popped_entry.value
        
    
    def set_value(self, key: Any, value: Any) -> LazyAnimation:
        """Update the value cell for ``key`` and animate the change when possible."""

        def build():
            entry = self._get_entry(key)
            transform = entry.value_cell.set_value(value, color=self.text_color)
            entry.value = entry.value_cell.value

            self.logger.debug("hash_table.set_value key=%s value=%s", key, entry.value)

            if self.scene and is_animating() and self.scene.in_play:
                return Succession(self._highlight_entry(key), transform)
            return transform

        return LazyAnimation(builder=build)
    
        
    
    
    def _highlight_entry(self, element: Any | Entry, color: ManimColor = YELLOW, opacity: float = 0.5):
        """Sequentially highlight key then value cells for the targeted entry."""
        entry = element if isinstance(element, Entry) else self._get_entry(element)
        anims = [
            super().highlight(element=entry.key_cell, color=color, opacity=opacity, runtime=0.3),
            super().unhighlight(element=entry.key_cell, color=color, opacity=opacity, runtime=0.2),
            super().highlight(element=entry.value_cell, color=color, opacity=opacity, runtime=0.3),
            super().unhighlight(element=entry.value_cell, color=color, opacity=opacity, runtime=0.2),
        ]
        return Succession(*anims)
    
    
    def create(self,entries:list[Entry]=None,runtime:float=0.5):
        if not self._instantialized:  #instantiate cell geometry without animation
            self.elements =  [None] * self._bucket_count #Prefill stuff first so the hashed key does not go out-of-bounds
            anchor = np.array(self.get_center())
            if not np.allclose(anchor, 0):
                self.pos = anchor
            for key,data in self._raw_data.items():
                hashed_key = self._hash_key(key=key)
                entry = Entry(master=self,kv_pair=(key,data),hash=hashed_key,label=self.label)
                self.entries[key] = entry
                self.elements[hashed_key] = entry
                self.add(entry)
                
            self.arrange(DOWN,buff=0.6) #Magic number
            first_entry = next(iter(self.entries.values()), None)
            if first_entry is not None:
                self.align_to(first_entry, LEFT)
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
