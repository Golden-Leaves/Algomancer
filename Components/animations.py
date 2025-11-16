from __future__ import annotations

import numpy as np
from manim import Animation, ApplyMethod, DOWN, LEFT, RIGHT, UP
from typing import Sequence, TYPE_CHECKING

if TYPE_CHECKING:
    from Structures.base import VisualElement


class LazyAnimation:
    """Wrapper for a function that builds an Animation lazily.

    Allows call sites to defer expensive animation creation until `play()` runs. Avoids
    pre-computing animations (e.g. `set_value`) before the scene exists.
    """
    

    def __init__(self, builder):
        self.builder = builder

    def build(self) -> Animation:
        anim = self.builder()
        return anim
    def begin(self):
        from manim import config
        self.dt = 1 / config.frame_rate
        self.time = 0.0
        self.state = "playing"


def hop_element(
    element: "VisualElement",
    *,
    lift: float = 0.5,
    runtime: float = 0.3,
    direction: np.ndarray = UP,
) -> Animation:
    """Return a hop animation for a visual element."""
    start = element.center
    if direction is UP:
        raw_vec = element.top - start
    elif direction is DOWN:
        raw_vec = element.bottom - start
    elif direction is LEFT:
        raw_vec = element.left - start
    elif direction is RIGHT:
        raw_vec = element.right - start
    else:
        raw_vec = np.asarray(direction, dtype=float)
    norm = np.linalg.norm(raw_vec)
    if norm == 0:
        raise ValueError("Cannot compute hop direction for zero-length vector.")
    shift_vec = raw_vec / norm
    hop_pos = start + shift_vec * (element.body_height + lift)
    return ApplyMethod(element.move_to, hop_pos, run_time=runtime)


def slide_element(
    element: "VisualElement",
    *,
    target_pos: Sequence[float] | np.ndarray,
    runtime: float = 0.5,
    align: str = "x",
) -> Animation:
    """Return a slide animation while preserving vertical alignment."""
    current = element.center
    goal = np.asarray(target_pos, dtype=float)
    if align == "x":  # Preserve the current y/z coordinates.
        planar_goal = np.array([goal[0], current[1], current[2]])
    elif align == "y":
        planar_goal = np.array([current[0], goal[1], current[2]])
    elif align == "z":
        planar_goal = np.array([current[0], current[1], goal[2]])
    else:
        raise ValueError(f"Unsupported alignment axis: {align}")
    return ApplyMethod(element.move_to, planar_goal, run_time=runtime)
