from manim import *
import subprocess
from pathlib import Path
import os
from typing import TYPE_CHECKING
from Components.config import DEFAULT_CONFIG as CFG
from Components.logging import DebugLogger
from Components.runtime import AlgoScene,AlgoSlide
QUALITY_MAP = {
    "low": "l",      # -ql
    "medium": "m",   # -qm
    "high": "h",     # -qh
    "4k": "k",       # -qk
}


def render_scene(
    scenes: list[AlgoScene | AlgoSlide] | AlgoScene,
    file: str | Path,
    *,
    quality: str | None = None,
    preview: bool | None = None,
    image: bool | None = None,
    renderer: str | None = None,
    write_to_file: bool | None = None,
    fps: int | None = None,
    slides: bool = True,
    force:bool = True,
) -> list[str]:
    """Render one or more scenes via the Manim CLI.

    Parameters
    ----------
    scenes : list[AlgoScene | AlgoSlide] | AlgoScene
        Scene subclass (or list of subclasses) to render.
    file : str | Path
        File path (usually ``__file__``) that owns the scene class.
    quality : str | None, optional
        Output quality flag. Defaults to "medium" when omitted.
    preview : bool | None, optional
        Open the preview window (``-p``). Defaults to True.
    image : bool | None, optional
        Render only the last frame (``-s``). Defaults to False.
    renderer : str | None, optional
        Manim renderer backend. Defaults to "opengl".
    write_to_file : bool | None, optional
        Force movie file output. For OpenGL this adds ``--write_to_movie``. Defaults to False.
    fps : int | None, optional
        Frames per second (``--fps``). Defaults to 30.
    slides : bool | None, optional
        Whether to force manim-slides mode. When ``None``, logic will decide later.

    Returns
    -------
    list[str]
        Names of rendered scenes in order.
    """
    logger = DebugLogger(logger_name=__name__, output=True)
    cfg = CFG 
    quality = (quality or cfg.render.quality).lower()
    if quality not in QUALITY_MAP:
        raise ValueError(f"Unsupported quality '{quality}'. Expected one of {tuple(QUALITY_MAP)}")

    preview = True if preview is None else preview
    image = False if image is None else image
    renderer = (renderer or cfg.render.renderer_str).lower()
    write_to_file = False if write_to_file is None else write_to_file
    fps = fps or cfg.playback.frame_rate
    logger.debug("Is slides True?: %s",slides)
    file = os.path.basename(os.path.abspath(file))
    if not isinstance(scenes, list):
        scenes = [scenes]
        
    def write_scenes(scenes: list[AlgoScene | AlgoSlide], cmd: list[str]) -> list[str]:
        """Appends each scene's class name to `cmd` and runs it. When in slides mode,
        exits early if a matching slides JSON already exists to avoid re-rendering.
        """
        outputs = []
        for scene in scenes: #rendering
            logger.debug("Slides path: %s",os.path.join("slides",scene.__name__,".json"))
            slides_exist = os.path.exists(os.path.join("slides",f"{scene.__name__}.json")) #Slides path
            if slides and slides_exist and not force: 
                return
            cmd.append(scene.__name__)
            print("Running:", " ".join(cmd))
            subprocess.run(cmd, check=True)
            outputs.append(scene.__name__)
        return outputs
    
    def build_cmd(slides: bool, quality: str, preview: bool, image: bool, renderer: str, write_to_file: bool, fps: int, file: str | Path) -> list[str]:
        """Compose the base manim/manim-slides command (without scene name).

        Picks the binary from `slides`, applies quality/preview/image/renderer/fps
        flags, and returns argv ready for `subprocess.run`.
        """
        flag_bin = "manim" if not slides else "manim-slides"
        flag_quality = f"-q{QUALITY_MAP[quality]}" 
        flag_preview = "-p" if (preview and not slides) else ""
        flag_image = "-s" if image else ""
        flag_renderer = f"--renderer={renderer}" if renderer else ""
        flag_write_to_movie = "--write_to_movie" if renderer == "opengl" and write_to_file else ""#OpenGL does not automatically write a file
        logger.debug("Write to movie?: %s",flag_write_to_movie)
        flag_file_path = str(Path(file).resolve())
        flag_fps = f"--fps={fps}"
        
        cmd = [
                        flag_bin,
                        "render" if slides else "",
                        flag_preview,
                        flag_quality,
                        flag_image,
                        flag_renderer,
                        flag_write_to_movie,
                        flag_fps,
                        flag_file_path,
                    ]
        return [c for c in cmd if c]
                
    def present_slides(scenes: list[AlgoScene | AlgoSlide]) -> None:
        """Present validated slide scenes via manim-slides.

        Ensures all scenes subclass `AlgoSlide`, then runs `manim-slides present`
        for each scene name.
        """
        invalid = [s for s in scenes if not issubclass(s, AlgoSlide)]
        if invalid:
            names = ", ".join(s.__name__ for s in invalid)
            raise TypeError(f"Slides mode requires AlgoSlide subclasses only. Invalid: {names}")
        scene_names = [scene.__name__ for scene in scenes]
        for scene_name in scene_names:
            cmd = [
                "manim-slides",
                "present",
                scene_name
            ]
            cmd = [c for c in cmd if c]
            print("Running:", " ".join(cmd))
            subprocess.run(cmd, check=True)
        return

    
    cmd = build_cmd(slides,quality,preview,image,renderer,write_to_file,fps,file)
    outputs = write_scenes(scenes=scenes,cmd=cmd)
    if slides and preview:
        present_slides(scenes=scenes)
    return outputs
            

   
