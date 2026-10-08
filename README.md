# Hyperon–nucleon research seminar

The editable, animated presentation is in [manim/seminar.py](manim/seminar.py).
It contains 22 Manim Slides scenes drawn as diagrams and data plots. The
warm paper background and teal, rust, orange, and gold accents come from the
previous seminar. The quark flow, pion exchange, and contact diagrams are
editable Manim vectors inspired by the hand-drawn figures on numbered slide 5
of the PDF. The animation code does not embed PDF slide images.

## Build and present

Activate the existing `space` Conda environment and work from the `manim`
directory:

```bash
conda activate space
cd manim
python deck.py all
python deck.py present
```

`all` renders the slides at the resolution and frame rate in `manim.cfg`,
exports checkpoint PNGs, and packages an offline browser player at
`manim/outputs/seminar.html`. The first render can take several minutes.
`present` opens that player. Advance at each checkpoint with Space or
the right arrow; use N for speaker notes and F for full screen.

The `space` environment currently lacks Qt bindings, so the native Manim
Slides player is unavailable there. If you install PySide6 or PyQt5 in that
environment, `python deck.py present --native` launches it instead.

For a quick visual check:

```bash
python deck.py render --draft
python deck.py pngs
```

For one scene, use `python deck.py render --draft --scene S13LO`, followed
by `python deck.py pngs --scene S13LO`. The PNGs and per-scene contact sheets
are in `manim/outputs/pngs`. Render without `--draft` before presenting
the final deck. `python deck.py html` rebuilds the browser player from
already rendered slides and PNGs.

The original uploaded files are:
- seminario passaggio anno is the preliminary version of the slides, maybe they should be made a bit more appealing and suitable for physicists from different research areas (they were already showed to experimentalists in nuclear physics and they said they were easy to understand)
- seminario primo anno is an extract from the first year seminar, includes only neutron stars formation and a detailed explanation of the hyperon puzzle, I would like to include some content of it into the preliminary version of the slides, because it contains some effective images (ie neutron star compared to Pisa)
- thesis is the file containing a summary of the work done so far during the phd (ideally it contains everything that should be explained in the slides, but some details on the fitting procedure can probably be skipped)
