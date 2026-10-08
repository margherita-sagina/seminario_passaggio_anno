"""A presentation-ready schematic replacement of n by Lambda, drawn with Manim.

Render with the project's environment:
  .venv/bin/python tritium_to_hypertritium.py
"""
from pathlib import Path
import numpy as np
import manimpango
from manim import *

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "outputs" / "tritium_to_hypertritium"
CREAM = "#FFFCF5"
DARK = "#322C21"
TEAL = "#3C7F72"
GOLD = "#FBB131"
ORANGE = "#D74722"
FONT = "Yanone Kaffeesatz"

manimpango.register_font(str(ROOT / "assets/fonts/YanoneKaffeesatz-VariableFont_wght.ttf"))


def rough_ring(radius, seed, color, width, offset=ORIGIN, opacity=1):
    rng = np.random.default_rng(seed)
    theta = np.linspace(0, TAU, 190)
    # Small, correlated deviations preserve the sketch's slightly imperfect rim.
    radial = radius + 0.010 * np.sin(3 * theta + seed) + 0.009 * np.sin(7 * theta)
    radial += rng.normal(0, 0.003, theta.size)
    points = np.column_stack((radial * np.cos(theta), radial * np.sin(theta), np.zeros_like(theta)))
    path = VMobject(stroke_color=color, stroke_width=width, stroke_opacity=opacity)
    path.set_points_smoothly(points).shift(offset)
    return path


def particle(label, color, seed):
    radius = 0.85
    body = Circle(radius=radius, stroke_width=0, fill_color=color, fill_opacity=1)
    # The offset colour rim and dark pencil contour mirror the supplied artwork.
    halo = rough_ring(radius + 0.038, seed, color, 4, 0.046 * RIGHT + 0.060 * UP).set_fill(color, opacity=1)
    outline = rough_ring(radius - 0.015, seed + 1, DARK, 2.0, 0.028 * LEFT + 0.035 * DOWN, 0.86)
    rng = np.random.default_rng(seed)
    flecks = VGroup()
    for _ in range(115):
        angle = rng.uniform(0, TAU)
        radial = rng.uniform(radius + 0.017, radius + 0.075)
        pos = np.array([radial * np.cos(angle), radial * np.sin(angle), 0]) + [0.046, 0.060, 0]
        flecks.add(Line(pos, pos + rng.uniform(.005, .025) * np.array([-np.sin(angle), np.cos(angle), 0]),
                        stroke_color=color, stroke_width=rng.uniform(.6, 1.9), stroke_opacity=.65))
    # A restrained broken cream line suggests the original brush texture.
    highlights = VGroup()
    for start, length in [(0.24, .24), (1.03, .29), (1.48, .42), (3.23, .17), (4.02, .47)]:
        highlights.add(Arc(radius=radius + .026, start_angle=start, angle=length,
                          stroke_color=CREAM, stroke_width=.9, stroke_opacity=.72))
    if label == "Λ":
        glyph = Text("Λ", font="Times New Roman", slant=ITALIC, weight=BOLD, color=CREAM, font_size=78)
        glyph.scale_to_fit_height(1.02).shift(.04 * DOWN)
    else:
        glyph = Text(label, font=FONT, weight=BOLD, color=CREAM, font_size=91)
        glyph.scale_to_fit_height(1.04).shift(.005 * DOWN)
    return VGroup(halo, flecks, body, highlights, outline, glyph)


def caption(hyper=False):
    h = Text("H", font="Times New Roman", color=DARK, font_size=58).scale_to_fit_height(.78)
    three = Text("3", font="Times New Roman", color=DARK, font_size=38).scale_to_fit_height(.51)
    three.next_to(h, LEFT, buff=.015).shift(.40 * UP)
    isotope = VGroup(h, three)
    if hyper:
        lam = Text("Λ", font="Times New Roman", color=DARK, font_size=38).scale_to_fit_height(.51)
        lam.next_to(h, LEFT, buff=.025).shift(.30 * DOWN)
        isotope.add(lam)
    reference = Text("tritium", font=FONT, weight=BOLD, color=DARK, font_size=57)
    name = Text("hypertritium" if hyper else "tritium", font=FONT, weight=BOLD,
                color=DARK, font_size=57).scale(.77 / reference.height)
    name.next_to(h, RIGHT, buff=.21).align_to(h, DOWN)
    if hyper:
        name.shift(.15 * DOWN)  # The y descender sits below the shared text baseline.
    group = VGroup(isotope, name)
    group.move_to([0, -1.95, 0])
    return group


class TritiumToHypertritium(Scene):
    def construct(self):
        self.camera.background_color = ManimColor(CREAM)
        left_n = particle("n", GOLD, 3).move_to([-.98, 1.13, 0])
        right_position = np.array([.40, .40, 0])
        right_n = particle("n", GOLD, 11).move_to(right_position)
        proton = particle("p", TEAL, 19).move_to([.36, 1.98, 0])
        initial_caption = caption()
        final_caption = caption(True)
        hyperon = particle("Λ", ORANGE, 29).move_to([5.5, -0.25, 0])

        # Fixed spectator particles keep their positions throughout the replacement.
        self.add(left_n, right_n, proton, initial_caption)
        self.wait(1.6)
        departure = CubicBezier(right_position, [1.3, .25, 0], [3.4, 1.1, 0], [5.5, 1.65, 0])
        self.play(MoveAlongPath(right_n, departure), run_time=1.65, rate_func=smooth)
        self.remove(right_n)
        self.wait(.35)
        self.add(hyperon)
        # Draw the proton above the incoming hyperon, as in both supplied endpoints.
        self.bring_to_front(proton)
        arrival = CubicBezier([5.5, -.25, 0], [3.5, -.65, 0], [1.45, -.10, 0], right_position)
        self.play(MoveAlongPath(hyperon, arrival), run_time=1.9, rate_func=smooth)
        self.play(FadeOut(initial_caption), FadeIn(final_caption), run_time=.65)
        self.wait(2.35)


if __name__ == "__main__":
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with tempconfig({"pixel_width": 1440, "pixel_height": 1440,
                     "frame_width": 8, "frame_height": 8, "frame_rate": 30,
                     "background_color": CREAM, "media_dir": str(OUTPUT / "render"),
                     "output_file": "tritium_to_hypertritium", "disable_caching": True,
                     "write_to_movie": True, "verbosity": "WARNING"}):
        scene = TritiumToHypertritium()
        scene.render()
        import shutil
        shutil.copy2(scene.renderer.file_writer.movie_file_path, OUTPUT / "tritium_to_hypertritium.mp4")
