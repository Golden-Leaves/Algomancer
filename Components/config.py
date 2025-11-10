from __future__ import annotations

"""
Static configuration defaults for Algomancer.

Other parts of the codebase
can import the dataclasses below and either use them as-is or clone them
with overrides before wiring dependencies.
"""

from dataclasses import dataclass, field, replace
from typing import Any, Dict


@dataclass(frozen=True)
class RenderSettings:
    """Renderer/window parameters."""
    from manim.renderer.opengl_renderer import OpenGLRenderer
    from manim.renderer.cairo_renderer import CairoRenderer
    pixel_width: int = 1920
    pixel_height: int = 1080
    window_scale: float = 0.75  # 0–1, multiplies pixel dims to get window size
    quality: str = "medium"  # low | medium | high | 4k
    renderer_str: str = "opengl"  # or "cairo"
    renderer: OpenGLRenderer | CairoRenderer = OpenGLRenderer # or CairoRenderer
    samples: int = 1  # MSAA samples


@dataclass(frozen=True)
class PlaybackSettings:
    """Playback/controller defaults."""

    frame_rate: int = 30
    dt_mode: str = "fixed"  # "fixed" or "adaptive"



@dataclass(frozen=True)
class LoggingSettings:
    """Logging defaults."""

    level: str = "INFO"
    console: bool = True
    file_path: str = "DEBUG/algomancer.log"


@dataclass(frozen=True)
class AppConfig:
    """Container for all configuration domains."""

    render: RenderSettings = RenderSettings()
    playback: PlaybackSettings = PlaybackSettings()
    logging: LoggingSettings = LoggingSettings()
    metadata: Dict[str, Any] = field(default_factory=dict)

    def with_overrides( #We froze the dataclasses
        self,
        *,
        render: RenderSettings | None = None,
        playback: PlaybackSettings | None = None,
        logging: LoggingSettings | None = None,
        metadata: Dict[str, Any] | None = None,
    ) -> "AppConfig":
        """Return a new AppConfig with the provided replacements.

        Small use case:
        - Bump FPS for a single scene and attach a run tag without
          mutating global defaults:

          >>> from Components.config import DEFAULT_CONFIG, PlaybackSettings
          >>> cfg = DEFAULT_CONFIG.with_overrides(
          ...     playback=PlaybackSettings(frame_rate=60),
          ...     metadata={"scene": "ArrayScene", "run_id": "demo-01"},
          ... )
        """

        new_metadata = dict(self.metadata)
        if metadata:
            new_metadata.update(metadata)

        return AppConfig(
            render=render or self.render,
            playback=playback or self.playback,
            logging=logging or self.logging,
            metadata=new_metadata,
        )


DEFAULT_CONFIG = AppConfig()

__all__ = [
    "RenderSettings",
    "PlaybackSettings",
    "LoggingSettings",
    "AppConfig",
    "DEFAULT_CONFIG",
]
