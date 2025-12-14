from __future__ import annotations
import os
from typing import Any, TYPE_CHECKING
import json
import numpy as np
if TYPE_CHECKING:
    from manim import Mobject,np
    from Structures.base import VisualElement, VisualStructure
    from Components.runtime import AlgoScene


        
def get_mobject_state(mobj: Mobject | None, depth: int = 1) -> dict[str, Any]:
    """Return a snapshot of a Manim mobject's visual attributes."""
    if mobj is None:
        return {}
    submobjects: list[Any] = []
    if depth > 0: #recursively traverses submobjects to get their state
        for child in getattr(mobj, "submobjects", []):
            submobjects.append(get_mobject_state(child, depth=depth - 1))
    else:
        submobjects = [type(child).__name__ for child in getattr(mobj, "submobjects", [])]
        
    state: dict[str, Any] = {
        "type": type(mobj).__name__,
        "z_index": getattr(mobj, "z_index", None),
        "submobjects": submobjects,
    }
    if hasattr(mobj, "get_center"): state["center"] = np.array2string(mobj.get_center(), precision=3)
    if hasattr(mobj, "get_x"):
        state["x"], state["y"], state["z"] = (
            round(float(mobj.get_x()), 3),
            round(float(mobj.get_y()), 3),
            round(float(mobj.get_z()), 3),
        )
    if hasattr(mobj, "get_width"):
        state["width"], state["height"] = (
            round(float(mobj.get_width()), 3),
            round(float(mobj.get_height()), 3),
        )
    if hasattr(mobj, "get_fill_color"): state["fill_color"] = mobj.get_fill_color().to_hex()
    if hasattr(mobj, "get_fill_opacity"): state["fill_opacity"] = float(mobj.get_fill_opacity())
    if hasattr(mobj, "get_stroke_color"): state["stroke_color"] = mobj.get_stroke_color().to_hex()
    if hasattr(mobj, "get_stroke_width"): state["stroke_width"] = float(mobj.get_stroke_width())
    if hasattr(mobj, "get_stroke_opacity"):
        state["stroke_opacity"] = float(mobj.get_stroke_opacity())
    if hasattr(mobj, "get_opacity"): state["opacity"] = float(mobj.get_opacity())
    return state

def snapshot_element(element: "VisualElement", depth: int = 1) -> dict[str, Any]:
    """Return a JSON-safe snapshot for a single visual element."""
    master = getattr(element, "master", None)
    index = None
    elements = getattr(master, "elements", None)
    if elements:
        for idx, candidate in enumerate(elements):
            if candidate is element:
                index = idx
                break

    body = getattr(element, "body", None)
    text = getattr(element, "text", None)

    return {
        "index": index,
        "value": getattr(element, "value", None),
        "z_index": getattr(element, "z_index", None),
        "body": get_mobject_state(body, depth=depth),
        "text": get_mobject_state(text, depth=depth) if text is not None else {},
    }

def snapshot_structure(structure: "VisualStructure", depth: int = 1) -> dict[str, Any]:
    """Return a snapshot for a structure and all of its elements."""
    elements = getattr(structure, "elements", []) or []
    label = getattr(structure, "label", "") or ""
    return {
        "label": label,
        "type": type(structure).__name__,
        "z_index": getattr(structure, "z_index", None),
        "element_count": len(elements),
        "elements": [snapshot_element(element, depth=depth) for element in elements],
    }

# def write_snapshot(self,snapshot:dict):
#     with open("DEBUG/snapshots.jsonl","a",encoding="utf-8") as f:
#         f.write(json.dumps(snapshot,indent=2) + "\n")

# def read_snapshots(self):
#     with open("DEBUG/snapshots.jsonl","a",encoding="utf-8") as f:
#         lines = f.readlines()
#         for line in lines:
#             if line.strip():
#                 json.loads(line)