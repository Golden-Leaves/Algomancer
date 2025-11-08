from __future__ import annotations

"""
Renderer-specific strategy definitions without inheritance.
"""

from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class OpenGLStrategy:
    name: str = "opengl"

    def get_fill_opacity(self) -> float:
        #Why 1.0 for OpenGL? The OpenGL renderer has some weird rendering bug where the text dims on each highlight/indicate
        return 0.5 

    def get_stroke_opacity(self) -> float:
        return 1.0

    def default_stroke_width(self, level: str = "normal") -> float:
        return 4.5 if level == "normal" else 6.5

    def capabilities(self) -> Dict[str, Any]:
        return {
            "supports_shaders": True,
            "write_to_movie_default": False,
        }


@dataclass(frozen=True)
class CairoStrategy:
    name: str = "cairo"

    def get_fill_opacity(self) -> float:
        return 0.5# 0.5

    def get_stroke_opacity(self) -> float:
        return 1.0

    def default_stroke_width(self, level: str = "normal") -> float:
        return 4.0 if level == "normal" else 5.5

    def capabilities(self) -> Dict[str, Any]:
        return {
            "supports_shaders": False,
            "write_to_movie_default": True,
        }


__all__ = [
    "OpenGLStrategy",
    "CairoStrategy",
]
