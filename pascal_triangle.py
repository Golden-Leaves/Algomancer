from manim import *
from math import comb
from Structures.arrays import VisualArray
from Utils.render_scene import render_scene
from Utils.runtime import AlgoScene
from Utils.logging_config import setup_logging


class PascalTriangle(AlgoScene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = setup_logging("algomancer.pascal_triangle")
        self.logger.setLevel("DEBUG")

    def build_pyramid(self, rows: int):
        self.logger.info("Building Pascal triangle with %s rows", rows)
        arrays :list[VisualArray]= []
        for n in range(1, rows + 1):
            row = VisualArray([comb(n, k) for k in range(n + 1)], scene=self)
            if not arrays:
                vertical_offset = UP * ((rows - 1) * row.element_height)
                row.shift(vertical_offset)
            arrays.append(row)
            self.logger.debug("Initial row %s center %s", n, row.get_center())

            
            
        row_height = arrays[0].element_height
        pyramid = VGroup(*arrays).arrange(DOWN, buff=row_height * 0.68)
        for idx, row in enumerate(arrays, start=1):
            self.logger.debug(
                "Positioned row %s center %s height %s", idx, row.get_center(), row.height
            )
        return pyramid

    def construct(self):
        rows = 3
        with self.animation_context():
            pyramid = self.build_pyramid(rows=rows)
            for idx, row in enumerate(pyramid, start=1):
                self.logger.debug("Creating row %s center before create %s", idx, row.get_center())
                row.play(row.create())
                self.logger.debug("Row %s center after create %s", idx, row.get_center())
        self.wait(1)
        self.interactive_embed()


if __name__ == "__main__":
    render_scene(PascalTriangle, file=__file__, quality="high", renderer="opengl")
