from manim import *
import subprocess
from pathlib import Path
import os
QUALITY_MAP = {
    "low": "l",      # -ql
    "medium": "m",   # -qm
    "high": "h",     # -qh
    "4k": "k",       # -qk
}

def render_scene(scenes,file, quality="low", preview=True,image=False,renderer="cairo"):
    """
    Run this "manim -pql scene.py AnimatedSquareToCircle" command as if in a CLI, so you can run inside .py file\n
    file   : Pass file(with two underscores on both sides) to this\n
    scenes : Scene class or list of Scene classes\n
    quality: "low","medium","high","4k"\n
    preview: add -p flag\n
    image  : add -s flag (last frame only)
    """
    file = os.path.basename(os.path.abspath(file))
    if not isinstance(scenes, list):
        scenes = [scenes]

    flag_quality = f"-q{QUALITY_MAP[quality]}"
    flag_preview = "-p" if preview else ""
    flag_image = "-s" if image else ""
    flag_renderer = f"--renderer={renderer}" if renderer else ""

    outputs = []
    for scene in scenes:
        cmd = [
            "manim",
            flag_preview,
            flag_quality,
            flag_image,
            flag_renderer,
            str(Path(file)),
            scene.__name__,  # Scene class name
        ]
        # Filter out empty strings
        cmd = [c for c in cmd if c]
        print("Running:", " ".join(cmd))
        subprocess.run(cmd, check=True)

        outputs.append(scene.__name__)

    return outputs