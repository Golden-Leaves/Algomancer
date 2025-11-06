from manim import *
import subprocess
from pathlib import Path
import os

from Components.config import DEFAULT_CONFIG as CFG

QUALITY_MAP = {
    "low": "l",      # -ql
    "medium": "m",   # -qm
    "high": "h",     # -qh
    "4k": "k",       # -qk
}


def render_scene(
    scenes,
    file,
    *,
    quality: str | None = None,
    preview: bool | None = None,
    image: bool | None = None,
    renderer: str | None = None,
    write_to_file: bool | None = None,
    fps: int | None = None,
):
    """Render one or more scenes via the Manim CLI.

    Parameters
    ----------
    scenes : type[Scene] | list[type[Scene]]
        Scene subclass (or list of subclasses) to render.
    file : str | Path
        File path (usually ``__file__``) that owns the scene class.
    quality : {"low", "medium", "high", "4k"} | None, optional
        Output quality flag. Falls back to ``CFG.render.quality`` when omitted.
    preview : bool | None, optional
        Open the preview window (``-p``). Defaults to ``True`` when not provided.
    image : bool | None, optional
        Render only the last frame (``-s``). Defaults to ``False`` when not provided.
    renderer : {"opengl", "cairo"} | None, optional
        Manim renderer backend. Defaults to ``CFG.render.renderer``.
    write_to_file : bool | None, optional
        Force movie file output. For OpenGL this adds ``--write_to_movie``. Defaults to ``False``.
    fps : int | None, optional
        Frames per second (``--fps``). Defaults to ``CFG.playback.frame_rate``.

    Returns
    -------
    list[str]
        Names of rendered scenes in order.
    """

    cfg = CFG
    quality = (quality or cfg.render.quality).lower()
    if quality not in QUALITY_MAP:
        raise ValueError(f"Unsupported quality '{quality}'. Expected one of {tuple(QUALITY_MAP)}")

    preview = True if preview is None else preview
    image = False if image is None else image
    renderer = (renderer or cfg.render.renderer).lower()
    write_to_file = False if write_to_file is None else write_to_file
    fps = fps or cfg.playback.frame_rate

    file = os.path.basename(os.path.abspath(file))
    if not isinstance(scenes, list):
        scenes = [scenes]

    flag_quality = f"-q{QUALITY_MAP[quality]}"
    flag_preview = "-p" if preview else ""
    flag_image = "-s" if image else ""
    flag_renderer = f"--renderer={renderer}" if renderer else ""
    #OpenGL does not automatically write a file
    flag_write_to_movie = "--write_to_movie" if renderer == "opengl" and write_to_file else ""
    flag_fps = f"--fps={fps}"

    outputs = []
    for scene in scenes:
        cmd = [
            "manim",
            flag_preview,
            flag_quality,
            flag_image,
            flag_renderer,
            flag_write_to_movie,
            flag_fps,
            str(Path(file)),
            scene.__name__,  # Scene class name
        ]
        cmd = [c for c in cmd if c]
        print("Running:", " ".join(cmd))
        subprocess.run(cmd, check=True)

        outputs.append(scene.__name__)

    return outputs
