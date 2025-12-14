from __future__ import annotations
from manim import *
import numpy as np
from typing import Any
from Structures.arrays import Cell
from Structures.base import VisualStructure,VisualElement
from Components.animations import LazyAnimation, hop_element, slide_element
from Components.geometry import get_offset_position
from Components.logging import DebugLogger
from Components.runtime import is_animating
class Entry(VisualElement):
    """
    Composite visual element representing one key/value pair in the hash table.

    Parameters
    ----------
    master : VisualStructure | None
        Owning structure (typically the `VisualHashTable`) responsible for playback/logging.
    kv_pair : tuple[Any, Any]
        `(key, value)` payload used to initialize the entry's cells.
    label : str | None
        Optional label propagated to the underlying `VisualElement`.
    entry_height : int, optional
        Height for both key and value cells (before scaling).
    entry_width : int, optional
        Total width of the entry; key consumes 25%, value 75%.
    **kwargs :
        Forwarded to the base `VisualElement` constructor (e.g., positioning).
    """
    def __init__(self, master:VisualHashTable = None, kv_pair:tuple[Any,Any] = None,label = None, bucket:int = None,
                text_color:ManimColor=WHITE,text_size:float = 1.0,
                entry_height:int=1,entry_width:int=4,**kwargs):
        from Structures.base import _COMPARE_GUARD
        if kv_pair is None or not isinstance(kv_pair,tuple):
            raise ValueError("kv_pair must be a (key,value) tuple")
        self.bucket = bucket if bucket else master._hash_key(key=kv_pair[0])
        self.entry_height = entry_height
        self.entry_width = entry_width
        self.value_cell:Cell = Cell(value=kv_pair[1],master=master,cell_width=entry_width*0.75,cell_height=entry_height
                                    ,text_color=text_color,text_size=text_size)
        self.key_cell:Cell = Cell(value=kv_pair[0],master=master,cell_width=entry_width*0.25,cell_height=entry_height
                                  ,text_color=text_color,text_size=text_size)
        self.value_cell.move_to(RIGHT * entry_width*0.25 / 2) #Move center to the right edge of key_cell
        self.key_cell.move_to(LEFT * entry_width*0.75 / 2) #We escape the encompassing value_cell
        token = _COMPARE_GUARD.set(True)
        try:
            body = VGroup(self.key_cell,self.value_cell)
        finally:
            _COMPARE_GUARD.set(token)
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

    def set_value(self,value:Any,runtime:float=0.5):
        """Update the value cell for the entry"""
        return self.value_cell.set_value(value=value,runtime=runtime,
                                        text_color=self.text_color,text_size=self.text_size)
    def move_to(self,target_position:np.ndarray,runtime:float=0.5) -> tuple[ApplyMethod,ApplyMethod]:
        """Moves the entry to the desired position.

        Parameters
        ----------
        target_position : np.ndarray
            Desired position for the center of the entry.
        runtime : float, optional
            Duration of the animation.

        Notes
        -----
        - The key cell and value cell will be moved to the desired position.
        - The key cell will be centered at the left edge of the value cell.
        """
        key_target_position = [target_position[0] + (LEFT[0] * self.entry_width*0.25 / 2),target_position[1],target_position[2]]
        value_target_position = [target_position[0] + (RIGHT[0] * self.entry_width*0.75 / 2),target_position[1],target_position[2]]
        key_anim = ApplyMethod(self.key_cell.move_to,key_target_position,run_time=runtime)
        value_anim = ApplyMethod(self.value_cell.move_to,value_target_position,run_time=runtime)
        return key_anim,value_anim

class VisualHashTable(VisualStructure):
    """
    Visual representation of a dictionary that lays out entries by hashed bucket.
    """
    def __init__(self,data:dict,scene,element_width=4,element_height=1,label=None,**kwargs):
        """Parameters
        ----------
        data : dict
            Initial key/value pairs to realize in the table.
        scene : AlgoScene
            Scene responsible for rendering and animation playback.
        element_width : float, optional
            Width allocated to each entry.
        element_height : float, optional
            Height allocated to each entry.
        label : str | None, optional
            Optional label used in logs and overlays.
        **kwargs :
            Additional positioning arguments forwarded to `VisualStructure`.
        """
        self.logger = DebugLogger(logger_name=__name__, output=False)
        super().__init__(scene,label,**kwargs)
        self._raw_data = data
        self._bucket_count = max(1,len(data)) #Division by 0...
        self.element_width = element_width
        self.element_height = element_height
        self.entries:dict[Any,Entry] = {} #Normal keys, self.elements stores by buckets(hashed key)
        self._instantiated = False
        
    def __len__(self):
        return len(self.entries)
    
    def _rehash(self,new_bucket_count:int) -> None:
        """
        Rehashes all entries into a new set of buckets.

        Parameters
        ----------
        new_bucket_count : int
            The new number of buckets to rehash the entries into.
        """
        items = list(self.entries.items())
        self.elements = [None] * new_bucket_count
        self._bucket_count = new_bucket_count
        self.entries = {}
        for key,value in items:
            bucket = self._hash_key(key=key)
            value.bucket = bucket
            self.elements[bucket] = value
            self.entries[key] = value
        return
    
    def sort_entries_top_to_bottom(self, entries: list[Entry] = None) -> list[Entry]:
        """
        Sorts entries in descending order of their y-coordinate(top first).

        Parameters
        ----------
        entries : list[Entry], optional
            List of Entry objects to sort. Defaults to self.elements.

        Returns
        -------
        list[Entry]
            The sorted list of Entry objects.
        """
        if entries is None:
            entries = self.elements
        elements = [entry for entry in entries if entry]
        return list(sorted(elements, key=lambda element: element.get_center()[1]))
    
    def _hash_key(self, key: Any) -> int:
        """
        Hashes a key into a bucket index.\n
        Used for deterministic placement of entries in `self.elements`.

        Parameters
        ----------
        key : Any
            The key to hash.

        Returns
        -------
        int
            The bucket index associated with the key.
        """
        if isinstance(key, int):
            raw = key
        else:
            raw = sum(ord(char) for char in str(key))
        return raw % self._bucket_count

    def _get_entry(self, key: Any) -> Entry:
        """
        Retrieve the Entry associated with ``key`` while enforcing hash-table specific errors.

        Parameters
        ----------
        key : Any
            The key to retrieve the associated Entry for.

        Returns
        -------
        Entry
            The Entry associated with the key.

        Raises
        ------
        KeyError
            If the key is not present or the bucket's visuals are out of sync.
        """
        if isinstance(key,Entry):
            return key
        self.logger.debug("Key: %s", key)
        self.logger.debug("Key type: %s", type(key))
        bucket = self._hash_key(key)
        entry = self.entries.get(key, None)
        try:
            slot = self.get_element(bucket)
        except (IndexError, TypeError, ValueError) as exc:
            raise KeyError(f"HashTable bucket lookup failed for key {key!r}") from exc
        self.logger.debug("Entry and slot: %s; %s", entry, slot)
        if entry is None or slot is None:
            raise KeyError(f"Key {key!r} not present in hash table.")
        return entry
    
    def _highlight_entry(self,entry:Entry,color:ManimColor=YELLOW,opacity:float=0.5,runtime:float=0.5) -> tuple[ApplyMethod,ApplyMethod]:
        key_cell = super().highlight(element=entry.key_cell,color=color,opacity=opacity,runtime=runtime)
        value_cell = super().highlight(element=entry.value_cell,color=color,opacity=opacity,runtime=runtime)
        return (key_cell,value_cell)
    
    def _unhighlight_entry(self,entry:Entry,runtime:float=0.5) -> tuple[ApplyMethod,ApplyMethod]:
        key_cell = super().unhighlight(element=entry.key_cell,runtime=runtime)
        value_cell = super().unhighlight(element=entry.value_cell,runtime=runtime)
        return (key_cell,value_cell)
    
    def highlight(self, element:VisualElement|Any, color=YELLOW, opacity=0.5, runtime=0.4) -> ApplyMethod|tuple[ApplyMethod,ApplyMethod]:
        self.logger.debug("Element after _get_entry(): %s", element)
        self.logger.debug("Element type: %s", type(element))
        element = self._get_entry(key=element)
        if isinstance(element,Entry):
            return self._highlight_entry(entry=element,color=color,opacity=opacity,runtime=runtime)
        return super().highlight(element=element, color=color, opacity=opacity, runtime=runtime)
    
    def unhighlight(self, element, runtime=0.3) -> ApplyMethod|tuple[ApplyMethod,ApplyMethod]:
        element = self._get_entry(key=element)
        if isinstance(element,Entry):
            return self._unhighlight_entry(entry=element,runtime=runtime)
        return super().unhighlight(element=element, runtime=runtime)
    
    
    def __getitem__(self, key):
        entry = self._get_entry(key=key)
        if self.scene and is_animating() and not self.scene.in_play:
            self.play(self.highlight(element=entry,runtime=0.4))
            self.play(self.unhighlight(element=entry,runtime=0.3))
        return entry.value
    
    def __setitem__(self, key, value):
        try:
            entry = self._get_entry(key=key)
        except KeyError as e:
            self.add_entry(key=key,value=value)
            return
        self.play(entry.set_value(value=value))
        
    def move_to(self, target_position: np.ndarray, runtime: float = 0.5) -> None:
        """
        Moves all entries in the table to the desired position.

        Parameters
        ----------
        target_position : np.ndarray
            The desired position for the center of the table.
        runtime : float, optional
            Duration of the animation. Defaults to 0.5.

        Returns
        -------
        None
        """
        
        from Structures.base import _COMPARE_GUARD
        token = _COMPARE_GUARD.set(True)
        try:
            center_shift = (len(self.elements) - 1) / 2
            anims = []
            entries = self.sort_entries_top_to_bottom()
            self.logger.debug("Sorted Entries: %s",entries)
            for i,entry in enumerate(entries):
                entry_target_position = [target_position[0],target_position[1] + (i - center_shift),target_position[2]] 
                entry_shift = entry.move_to(target_position=entry_target_position,runtime=runtime)
                anims.append(entry_shift)
            self.play(anims,sequential=False)
        finally:
            _COMPARE_GUARD.set(token)
        
    def pop(self,key:Any|Entry,default=None,runtime=0.5) -> Any:
        keys = list(self.entries)
        mid = len(keys) // 2
        anims = []
        try:
            popped_entry = self._get_entry(key=key)
        except KeyError as e:
            if default is not None:
                return default
            raise e
        self.play(FadeOut(popped_entry))
        bucket = self._hash_key(key=key)
        
        popped_cell_index = keys.index(popped_entry.key)
        if popped_cell_index <= mid: #Shift upwards
            for idx in range(popped_cell_index - 1,-1,-1):
                from_key:Entry = self._get_entry(keys[idx])
                to_key:Entry = self._get_entry(keys[idx + 1])
                anims.append(slide_element(element=from_key,target_pos=to_key.get_center(),align="y"))
        else: #Shift downwards
            for idx in range(popped_cell_index + 1,len(keys)):
                from_key:Entry = self._get_entry(keys[idx])
                to_key:Entry = self._get_entry(keys[idx - 1])
                anims.append(slide_element(element=from_key,target_pos=to_key.get_center(),align="y"))
        
        if self.scene and is_animating() and not self.scene.in_play:
            self.play(*anims,runtime=runtime)    
            
        self.elements[bucket] = None
        self.entries.pop(popped_entry.key)
        self.remove(popped_entry)
        self.logger.debug("self.elements after pop(): %s",self.elements )
        return popped_entry.value
        
    
    def set_value(self, key: Any, value: Any) -> LazyAnimation:
        """Update the value cell for ``key`` and animate the change when possible."""

        def build():
            entry = self._get_entry(key)
            transform = entry.set_value(value=value)

            self.logger.debug("hash_table.set_value key=%s value=%s", key, entry.value)
            return transform

        return LazyAnimation(builder=build)
    
    
        
    
    
    
    def add_entry(self, key: Any, value: Any, recenter: bool = False) -> None:
        """Adds an entry to the hash table.

        Parameters
        ----------
        key : Any
            The key for the entry.
        value : Any
            The value for the entry.
        recenter : bool, optional
            Whether to recenter the hash table after adding the entry.

        Returns
        -------
        None
        """
        if not self._instantiated:
            self.create()
        before_move = self.get_center()
        key = key.value if isinstance(key,VisualElement) else key
        value = value.value if isinstance(value,VisualElement) else value
        bucket = self._hash_key(key=key)
        self._rehash(new_bucket_count=self._bucket_count + 1)
        
        entry = Entry(master=self,kv_pair=(key,value),scene=self.scene,bucket=bucket,entry_width=self.element_width,entry_height=self.element_height,
                      text_color=self.text_color,text_size=self.text_size)
        last_entry = self.elements[-1] if self.elements else entry
        if self.elements:
            entry_position = get_offset_position(element=last_entry,direction=DOWN,buff=0.5)
        else:
            entry_position = self.pos
        super(VisualElement,entry).move_to(entry_position)
        self.add(entry)
        self.entries[key] = entry
        self.elements[bucket] = entry
        self.play(self.create(entries=[entry]))
        self.logger.debug("self.elements after add_entry(): %s",self.elements)
        if recenter:
            self.move_to(before_move)
        return
        
    
    def create(self, entries: list[Entry] = None, runtime: float = 0.5) -> AnimationGroup:
        """
        Creates and returns animations for entries
        Parameters
        ----------
        entries : list[Entry], optional
            A list of Entry objects to populate the hash table with.
        runtime : float, optional
            The duration of the instantiation animation in seconds.

        Returns
        -------
        AnimationGroup
            The animation group containing the instantiation animation.
        """
        def instantiate(raw_data: dict[Any, Any],position: np.ndarray) -> None:
            """
            Instantiates the VisualHashTable from raw data.
            """
            self.elements =  [None] * self._bucket_count #Prefill stuff first so the hashed key does not go out-of-bounds
            anchor = np.array(self.get_center())
            if not np.allclose(anchor, 0):
                self.pos = anchor
            for key, data in raw_data.items():
                bucket = self._hash_key(key=key)
                entry = Entry(
                    master=self,
                    kv_pair=(key, data),
                    bucket=bucket,
                    label=self.label,
                    text_color=self.text_color,
                    text_size=self.text_size,
                    entry_width=self.element_width,
                    entry_height=self.element_height
                )
                self.entries[key] = entry
                self.elements[bucket] = entry
                self.add(entry)
                

            element_height = float(self.element_height)
            center_shift = (len(self.elements) - 1) / 2
            for idx, entry in enumerate(self.elements):
                offset = (idx - center_shift) * element_height #Distribute cells evenly based on a center point
                super(VisualElement,entry).move_to(position + DOWN * offset)
                
            first_entry = next(iter(self.entries.values()), None)
            if first_entry is not None:
                self.align_to(first_entry, LEFT)
            super(VisualStructure,self).move_to(self.pos)
            self._instantiated = True
            
        if not self._instantiated:
            instantiate(raw_data=self._raw_data,position=self.pos)
    
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
