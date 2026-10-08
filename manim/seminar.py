"""An animated, diagram-first research seminar.

Render scenes in SCENES order. Each class is a self-contained Manim Slides
scene, and every checkpoint is a presenter-controlled pause.
"""
from pathlib import Path
import csv
import numpy as np
import manimpango
from manim import *
from manim_slides import Slide

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
for font_file in sorted((ASSETS / "fonts").glob("*.ttf")):
    manimpango.register_font(str(font_file))

# The warm paper and accents follow the supplied seminar. The diagrams below
# are vector redrawings; no PDF slide or raster crop is used in the scenes.
BG = "#FFFCF5"
PANEL = "#F5F3EA"
EDGE = "#C7CBC1"
WHITE = "#3D4545"
MUTED = "#626C6B"
TEAL = "#3C7F72"
AMBER = "#B97810"
GOLD = "#F8B037"
CORAL = "#D24923"
RUST = "#992800"
BLUE = "#2389C4"
GREEN = "#14A65B"
FONT = "Open Sans SemiCondensed"
TITLE_FONT = "Yanone Kaffeesatz"


def text(s, size=30, color=WHITE, bold=False):
    return Text(s, font=TITLE_FONT if bold else FONT, font_size=size,
                color=color, weight=BOLD if bold else NORMAL)


def at(mob, x, y):
    return mob.move_to([x, y, 0])


def left(mob, x, y):
    return mob.move_to([x + mob.width / 2, y, 0])


def cap(mob, width):
    if mob.width > width:
        mob.scale_to_fit_width(width)
    return mob


def line(a, b, color=EDGE, width=2):
    return Line(a, b, color=color, stroke_width=width)


def badge(label, color=TEAL, radius=.48):
    echo = Circle(radius*1.04, color=color, stroke_width=.8).shift(LEFT*.035+DOWN*.02)
    disc = Circle(radius, color=color, stroke_width=2.5,
                  fill_color=color, fill_opacity=.13)
    return VGroup(echo, disc, text(label, max(19, 30*radius/.48), color, True))


def baryon(name, radius=.68):
    """An editable version of the author's quark-filled baryon sketch."""
    color = {"Λ": GOLD, "p": CORAL, "n": GREEN, "N": CORAL}.get(name, TEAL)
    quarks = {"Λ": "uds", "p": "uud", "n": "udd", "N": "uud"}.get(name, "uud")
    body = Circle(radius, color=color, stroke_width=2.4,
                  fill_color=color, fill_opacity=.23)
    echo = Arc(radius=radius*1.04, start_angle=.17, angle=TAU*.91,
               color=WHITE, stroke_width=.9).shift(LEFT*.04+DOWN*.025)
    spots = [(-.24,.20),(.24,.20),(0,-.22)]
    dots = VGroup()
    for q,(x,y) in zip(quarks,spots):
        qc = {"u":"#19BCD1","d":"#64D933","s":"#F37B55"}[q]
        pos=np.array([x*radius/.68,y*radius/.68,0])
        dot=Circle(radius*.19,color=WHITE,stroke_width=1,
                   fill_color=qc,fill_opacity=1).move_to(pos)
        letter=text(q,max(12,20*radius/.68),WHITE,True).move_to(pos)
        dots.add(dot,letter)
    return VGroup(echo,body,dots)


def wavy_line(start, end, color=CORAL, amplitude=.09, waves=5):
    """A smooth propagator path with controlled, repeatable bends."""
    a,b=np.array(start,dtype=float),np.array(end,dtype=float)
    d=b-a
    normal=np.array([-d[1],d[0],0])/np.linalg.norm(d)
    pts=[a+d*t+normal*(amplitude*np.sin(TAU*waves*t))
         for t in np.linspace(0,1,81)]
    return VMobject(color=color,stroke_width=3).set_points_smoothly(pts)


def contact_diagram(derivative=False, color=TEAL):
    """Four external baryon legs meeting at a contact vertex."""
    ends=[(-1.12,1.03),(1.12,1.03),(-1.12,-1.03),(1.12,-1.03)]
    group=VGroup()
    for x,y in ends:
        mid=np.array([.10*np.sign(x),.08*np.sign(y),0])
        group.add(CubicBezier([x,y,0],[x*.69,y*.66,0],
                              [x*.29,y*.25,0],mid,
                              color=WHITE,stroke_width=3.2))
    vertex=Square(.25,color=color,stroke_width=2.3,
                  fill_color=color,fill_opacity=1) if derivative else Dot(radius=.105,color=color)
    group.add(vertex)
    for x,y in ends:
        group.add(Dot([x,y,0],radius=.11,
                      color=GREEN if x*y>0 else BLUE))
    if derivative:
        for x,y in ends:
            group.add(Dot([x*.60,y*.57,0],radius=.045,color=CORAL))
    return group


def pion_exchange_diagram():
    """Two baryon lines coupled through an explicit virtual pion."""
    group=VGroup()
    for side in (-1,1):
        for top in (-1,1):
            x,y=side*1.18,top*1.07
            end=[side*.72,0,0]
            group.add(CubicBezier([x,y,0],[side*1.01,top*.72,0],
                                  [side*.79,top*.29,0],end,
                                  color=WHITE,stroke_width=3.2))
            group.add(Dot([x,y,0],radius=.12,
                          color=GREEN if side*top>0 else BLUE))
        group.add(Dot([side*.72,0,0],radius=.075,color=WHITE))
    group.add(wavy_line([-.72,0,0],[.72,0,0],CORAL,.09,4))
    group.add(Dot([0,0,0],radius=.115,color=GOLD))
    group.add(at(text("π",23,CORAL,True),0,.35))
    return group


def quark_exchange_diagram():
    """A schematic quark-level tangle, echoing the hand-drawn flow lines."""
    flows=VGroup(
        CubicBezier([-1.15,.85,0],[-.68,.22,0],[.66,-.22,0],[1.15,-.85,0],
                    color=WHITE,stroke_width=2.5),
        CubicBezier([1.15,.85,0],[.66,.22,0],[-.68,-.22,0],[-1.15,-.85,0],
                    color=WHITE,stroke_width=2.5),
        CubicBezier([-.95,.85,0],[-.45,.12,0],[.45,-.12,0],[.95,-.85,0],
                    color=CORAL,stroke_width=2.5),
        CubicBezier([.95,.85,0],[.45,.12,0],[-.45,-.12,0],[-.95,-.85,0],
                    color=TEAL,stroke_width=2.5))
    nodes=VGroup(*[at(baryon(s,.29),x,y) for x,y,s in
                   [(-1.2,1.13,"n"),(1.2,1.13,"p"),
                    (-1.2,-1.13,"p"),(1.2,-1.13,"n")]])
    virtual=VGroup(Dot([0,.25,0],radius=.075,color=GOLD),
                   Dot([0,-.25,0],radius=.075,color=GOLD),
                   wavy_line([0,.18,0],[0,-.18,0],CORAL,.045,2),
                   at(text("q",16,CORAL,True),.24,.23),
                   at(text("q̄",16,TEAL,True),-.24,-.23))
    return VGroup(flows,virtual,nodes)


def block(label, value, color=TEAL, width=4.1):
    shell = RoundedRectangle(corner_radius=.18, width=width, height=1.55,
                             color=EDGE, stroke_width=1.5, fill_color=PANEL,
                             fill_opacity=1)
    return VGroup(shell, at(text(label, 23, MUTED), 0, .35),
                  at(cap(text(value, 37, color, True), width-.35), 0, -.22))


def data(order, radius):
    name = f"{order.lower()}_r0{radius:.1f}".replace(".", "p") + ".csv"
    with (ASSETS / name).open() as file:
        rows = [(float(r["ecm_mev"]), float(r["cross_section_mb"]))
                for r in csv.DictReader(file) if r["observable"] == "cross_section"]
    return sorted(dict(rows).items())


def measurements():
    rows = []
    for raw in (ASSETS / "experimental_cross_section.dat").read_text().splitlines():
        if raw and not raw.startswith("#"):
            rows.append(tuple(float(x) for x in raw.split()[:6]))
    return rows


def plot(xmax=80, ymax=280, width=9.4):
    ax = Axes(x_range=[0, xmax, 20 if xmax >= 80 else 5],
              y_range=[0, ymax, 50], x_length=width, y_length=4.2,
              tips=False, axis_config={"color":MUTED, "stroke_width":1.5,
                                       "include_numbers":True, "font_size":22})
    at(ax, -1.8, -.2)
    xlab = text("Ecm  [MeV]", 22, MUTED).next_to(ax.x_axis, DOWN, buff=.26)
    ylab = text("σ  [mb]", 22, MUTED).next_to(ax.y_axis, UP, buff=.18)
    return ax, VGroup(ax, xlab, ylab)


def points(ax, xmax):
    group = VGroup()
    for _, _, energy, _, sigma, error in measurements():
        if energy > xmax or sigma > 280:
            continue
        p = ax.c2p(energy, sigma)
        group.add(line(ax.c2p(energy, max(0, sigma-error)),
                       ax.c2p(energy, min(280, sigma+error)), MUTED, 1),
                  Dot(p, radius=.035, color=WHITE))
    return group


def curve(ax, order, radius, xmax, color):
    values = [(x, y) for x, y in data(order, radius)
              if x <= xmax and 0 <= y <= 280]
    return VMobject(color=color, stroke_width=3.5).set_points_as_corners(
        [ax.c2p(x, y) for x, y in values])


class SeminarSlide(Slide):
    number = 0
    title = ""
    section = ""
    minutes = 1
    # Backward navigation jumps to the previous checkpoint. Reversing every
    # video segment is expensive at 1080p and can stall long data plots.
    skip_reversing = True

    def setup(self):
        super().setup()
        self.camera.background_color = ManimColor(BG)

    def heading(self):
        eyebrow = left(text(self.section.upper(), 22, TEAL, True), -7.1, 4.08)
        title = left(cap(text(self.title, 47, WHITE, True), 13.1), -7.1, 3.47)
        rule = line([-7.1, 2.99, 0], [7.1, 2.99, 0], EDGE, 1.5)
        accents = VGroup(*[
            line([-7.1+i*.62,2.99,0],[-6.52+i*.62,2.99,0],c,6)
            for i,c in enumerate([TEAL,RUST,CORAL,GOLD])])
        footer_rule=line([-7.1,-4.0,0],[7.1,-4.0,0],EDGE,1)
        footer = left(text("MARGHERITA SAGINA  ·  UNIVERSITY OF PISA", 17, MUTED),
                      -7.1, -4.25)
        count = at(text(f"{self.number:02d} / 22", 20, RUST), 6.55, -4.24)
        self.add(eyebrow, title, rule, accents, footer_rule, footer, count)

    def reveal(self, *mobjects, run_time=.8):
        self.play(LaggedStart(*[FadeIn(m, shift=UP*.13) for m in mobjects],
                              lag_ratio=.16), run_time=run_time)

    def checkpoint(self, note=""):
        self.wait(.15)
        self.next_slide(notes=f"{self.title}\n{note}")

    def end(self):
        self.wait(.25)

    def takeaway(self, message, color=TEAL):
        mob = at(cap(text(message, 33, color, True), 13.7), 0, -3.32)
        self.play(FadeIn(mob, shift=UP*.15), run_time=.7)
        return mob


class S01Aim(SeminarSlide):
    number=1; title="The hyperon–nucleon interaction"; section="Research seminar"; minutes=.5
    def construct(self):
        self.heading()
        question = left(text("How well do scattering data determine the ΛN force?", 34, WHITE),
                        -6.5, 1.9)
        sub = left(text("A local contact interaction up to next-to-leading order", 27, MUTED),
                   -6.5, 1.2)
        self.reveal(question, sub)
        a, b = at(baryon("Λ", 1.0), -2.35, -.75), at(baryon("p", 1.0), 2.35, -.75)
        interaction = wavy_line(a.get_right()+RIGHT*.13,b.get_left()+LEFT*.13,
                                CORAL,.08,4)
        self.play(FadeIn(a),FadeIn(b))
        self.play(Create(interaction),run_time=1.1)
        self.reveal(at(text("Λ  ·  uds",25,AMBER),-2.35,-2.1),
                    at(text("N  ·  shown as p",25,CORAL),2.35,-2.1))
        self.checkpoint("Central question: infer a useful hyperon–nucleon interaction from sparse scattering data.")
        self.reveal(at(text("SCATTERING  →  FIT  →  FEW-BODY PREDICTIONS", 26, AMBER, True), 0, -2.65))
        self.end()


class S02Applications(SeminarSlide):
    number=2; title="Why this interaction matters"; section="Motivation"; minutes=.8
    def construct(self):
        self.heading()
        star = Circle(1.45, color=TEAL, stroke_width=3, fill_color=TEAL, fill_opacity=.11)
        at(star, -3.8, -.15)
        dots = VGroup(*[Dot([-4.75+(i%4)*.6, .75-(i//4)*.58, 0],
                            radius=.09, color=AMBER if i in (2, 9) else TEAL)
                        for i in range(12)])
        tri = VGroup(line([2.55,.85,0],[5.45,.85,0],TEAL,3),
                     line([2.55,.85,0],[4,-1.35,0],AMBER,3),
                     line([5.45,.85,0],[4,-1.35,0],AMBER,3))
        trio = VGroup(at(badge("p",CORAL,.35),2.55,.85),
                      at(badge("n",TEAL,.35),5.45,.85),
                      at(badge("Λ",AMBER,.35),4,-1.35))
        self.play(Create(star), LaggedStart(*[FadeIn(d) for d in dots],lag_ratio=.06))
        self.reveal(at(text("NEUTRON-STAR MATTER", 25, TEAL, True), -3.8, -2.12))
        self.checkpoint("Hyperons may affect the composition and equation of state of dense matter. The star is schematic.")
        self.play(Create(tri), FadeIn(trio))
        self.reveal(at(text("LIGHT HYPERNUCLEI", 25, AMBER, True), 4, -2.12))
        self.takeaway("One interaction, two scales")
        self.end()


class S03Levels(SeminarSlide):
    number=3; title="A new baryon species becomes possible"; section="Dense matter"; minutes=1.4
    def construct(self):
        self.heading()
        ys=[-1.9,-1.32,-.74,-.16,.42,1]
        levels=VGroup(*[line([-5.7,y,0],[-1.25,y,0],TEAL,2) for y in ys])
        hyper=VGroup(*[line([1.1,y,0],[5.55,y,0],AMBER,2) for y in ys[3:]])
        self.play(Create(levels), Create(hyper))
        self.reveal(at(text("neutron states",25,TEAL),-3.5,1.88),
                    at(text("Λ states",25,AMBER),3.35,1.88))
        neutrons=VGroup(*[Dot([-5.15+(i%4)*1.05,ys[i//4],0],radius=.085,color=TEAL)
                          for i in range(16)])
        self.play(LaggedStart(*[FadeIn(d) for d in neutrons],lag_ratio=.045))
        self.checkpoint("The energy levels are schematic. Increasing density raises the neutron chemical potential.")
        moving=neutrons[-4:]
        self.play(*[d.animate.move_to([1.7+j*1.05,ys[3],0]).set_color(AMBER)
                    for j,d in enumerate(moving)],run_time=1.4)
        self.takeaway("Threshold and composition depend on the interaction")
        self.end()


class S04EOS(SeminarSlide):
    number=4; title="The hyperon puzzle"; section="Dense matter"; minutes=1.3
    def construct(self):
        self.heading()
        ax=Axes(x_range=[0,1,1],y_range=[0,1,1],x_length=8,y_length=4.4,
                tips=False,axis_config={"color":MUTED,"include_ticks":False})
        at(ax,-2.2,-.18)
        stiff=ax.plot(lambda x:.8*x**1.4,x_range=[.04,1],color=TEAL,stroke_width=4)
        soft=ax.plot(lambda x:.8*x**1.4 if x<.48 else .8*.48**1.4+.34*(x-.48),
                     x_range=[.04,1],color=CORAL,stroke_width=4)
        self.play(Create(ax), Create(stiff))
        self.reveal(at(text("energy density",22,MUTED),-2.2,-2.62),
                    at(text("pressure",22,MUTED).rotate(PI/2),-6.48,-.15))
        self.reveal(at(text("nucleonic",24,TEAL),.4,1.7))
        self.checkpoint("Qualitative pressure versus energy-density curves; these are not calculated equations of state.")
        self.play(Create(soft))
        self.reveal(at(text("with hyperons",24,CORAL),.6,.35),
                    left(text("Softer pressure response\ncan lower the maximum mass",29,WHITE),2.5,1.1))
        self.takeaway("The force is needed before dense-matter predictions")
        self.end()


class S05Features(SeminarSlide):
    number=5; title="What a local interaction means"; section="The model"; minutes=.8
    def construct(self):
        self.heading()
        a,b=at(baryon("Λ",.68),-4.35,.35),at(baryon("p",.68),-1.25,.35)
        distance=DoubleArrow(a.get_right()+RIGHT*.12,b.get_left()+LEFT*.12,
                             buff=0,color=CORAL,stroke_width=2.5)
        self.play(FadeIn(a),FadeIn(b),GrowArrow(distance))
        self.reveal(at(text("relative distance  r",27,WHITE),-2.8,1.35),
                    at(text("uds",23,AMBER),-4.35,-.78),
                    at(text("uud",23,CORAL),-1.25,-.78))
        self.checkpoint("The interaction is represented in relative coordinate space.")
        formula=at(MathTex(r"V_{\Lambda N}(r)=\sum_i C_i\,O_i(r)",
                           font_size=50,color=WHITE),2.8,.35)
        self.play(Write(formula))
        self.reveal(at(block("OPERATORS","spin · derivatives",CORAL,5),2.8,-1.65),
                    at(block("COEFFICIENTS","fit to data",TEAL,5),-3.1,-1.65))
        self.takeaway("Short-range physics lives in fitted coefficients")
        self.end()


class S06EFT(SeminarSlide):
    number=6; title="Change the resolution, change the description"; section="Effective field theory"; minutes=1.2
    def construct(self):
        self.heading()
        xcoords=[-4.72,0,4.72]
        labels=[("QCD","NN example · quark flow",CORAL),
                ("CHIRAL EFT","NN example · pion exchange",AMBER),
                ("CONTACT EFT","local contact vertex",TEAL)]
        diagrams=[at(quark_exchange_diagram().scale(1.27),-4.72,-.27),
                  at(pion_exchange_diagram().scale(1.27),0,-.27),
                  at(contact_diagram(False,TEAL).scale(1.27),4.72,-.27)]
        titles=[at(text(name,31,color,True),x,2.15)
                for x,(name,_,color) in zip(xcoords,labels)]
        details=[at(text(detail,23,MUTED),x,-2.4)
                 for x,(_,detail,_) in zip(xcoords,labels)]
        dividers=VGroup(DashedLine([-2.36,2.42,0],[-2.36,-2.64,0],
                                   color=EDGE,dash_length=.14),
                        DashedLine([2.36,2.42,0],[2.36,-2.64,0],
                                   color=EDGE,dash_length=.14))
        self.add(dividers)
        resolution=wavy_line([-6.78,1.71,0],[6.78,1.71,0],CORAL,.028,3)
        end_tip=at(Triangle(fill_color=CORAL,fill_opacity=1,stroke_width=0)
                   .scale(.12).rotate(-PI/2),6.82,1.71)
        self.play(Create(resolution),FadeIn(end_tip),run_time=.85)
        self.play(FadeIn(titles[0]),FadeIn(details[0]),Create(diagrams[0][0]),
                  FadeIn(diagrams[0][1:]),run_time=1.45)
        self.checkpoint("Schematic quark-level dynamics, inspired by the original hand-drawn NN exchange diagram.")
        self.play(FadeIn(titles[1]),FadeIn(details[1]),Create(diagrams[1]),
                  run_time=1.2)
        self.checkpoint("At chiral resolution an explicit virtual pion can mediate the interaction. These are schematic NN examples.")
        contact_rest=VGroup(*[part for i,part in enumerate(diagrams[2]) if i!=4])
        self.play(FadeIn(titles[2]),FadeIn(details[2]),
                  TransformFromCopy(diagrams[1][-3],diagrams[2][4]),
                  Create(contact_rest),run_time=1.35)
        focus=SurroundingRectangle(VGroup(titles[2],diagrams[2],details[2]),
                                   buff=.21,color=TEAL,stroke_width=2,
                                   corner_radius=.22)
        self.play(Create(focus))
        self.takeaway("Unresolved meson physics enters contact terms")
        self.end()


class S07Potential(SeminarSlide):
    number=7; title="Build the ΛN potential order by order"; section="Effective field theory"; minutes=1.4
    def construct(self):
        self.heading()
        lo=at(text("LO  ·  2 coefficients",31,AMBER,True),-3.55,2.02)
        nlo=at(text("NLO  ·  +5 coefficients",31,TEAL,True),3.55,2.02)
        lo_d=at(contact_diagram(False,AMBER).scale(1.23),-3.55,.45)
        nlo_d=at(contact_diagram(True,TEAL).scale(1.23),3.55,.45)
        eq=MathTex(r"V_{\rm LO}=\left[C_S+C_T(\boldsymbol\sigma_\Lambda\!\cdot\!\boldsymbol\sigma_N)\right]F(r)",
                   font_size=38,color=WHITE)
        at(cap(eq,12.7),0,-1.5)
        self.reveal(lo)
        self.play(Create(lo_d))
        self.play(Write(eq))
        self.checkpoint("LO contains central and spin–spin contact operators.")
        self.reveal(nlo)
        self.play(TransformFromCopy(lo_d,nlo_d),run_time=1.2)
        self.play(ReplacementTransform(eq,at(MathTex(
            r"V_{\rm total}=V_{\rm LO}+V_{\rm NLO}",font_size=51,color=WHITE),0,-1.5)))
        self.reveal(at(text("gradients  ·  spin–orbit  ·  tensor structures",27,MUTED),0,-2.35))
        self.takeaway("Seven coefficients are fitted at NLO")
        self.end()


class S08Regulator(SeminarSlide):
    number=8; title="A regulator sets the contact range"; section="Effective field theory"; minutes=1.1
    def construct(self):
        self.heading()
        ax=Axes(x_range=[0,4,1],y_range=[0,1.15,.25],x_length=9,y_length=4.4,
                tips=False,axis_config={"color":MUTED,"include_numbers":True,"font_size":21})
        at(ax,-1.55,-.25)
        self.play(Create(ax))
        radii=[.7,1,1.5,2]
        colors=[CORAL,AMBER,TEAL,BLUE]
        for r,c in zip(radii,colors):
            g=ax.plot(lambda x:np.exp(-(x/r)**2),x_range=[0,4],color=c,stroke_width=3)
            self.play(Create(g),FadeIn(at(text(f"R₀ = {r:g} fm",23,c),5.35,1.6-(radii.index(r))*.75)))
            if r==1:self.checkpoint("Smaller regulator radii make the local contact sharper. Curves are normalized here to compare their shapes.")
        self.takeaway("Regulator variation tests model sensitivity")
        self.end()


class S09Scattering(SeminarSlide):
    number=9; title="Scattering probes the force"; section="Observables"; minutes=1
    def construct(self):
        self.heading()
        target=at(baryon("p",.52),1,.05)
        projectile=at(baryon("Λ",.45),-5.45,.05)
        incoming=Arrow([-4.8,.05,0],[-.05,.05,0],buff=0,color=TEAL,stroke_width=4)
        outgoing=Arrow([1.7,.32,0],[5.5,1.8,0],buff=0,color=AMBER,stroke_width=4)
        self.play(FadeIn(projectile),FadeIn(target),GrowArrow(incoming))
        self.reveal(at(text("incident Λ",24,AMBER),-4.2,-.65),
                    at(text("proton target",24,CORAL),1,-.75))
        self.checkpoint("A Λ beam scatters from a proton target. The diagram is schematic.")
        self.play(GrowArrow(outgoing))
        arc=Arc(radius=1.1,start_angle=0,angle=.4,color=WHITE).move_arc_center_to([1,.05,0])
        self.play(Create(arc))
        self.reveal(at(text("angle θ",28,WHITE),3,.75),
                    at(text("measure the outgoing distribution",28,MUTED),0,-1.75))
        self.takeaway("Data constrain the interaction coefficients")
        self.end()


class S10Observables(SeminarSlide):
    number=10; title="Two views of the same scattering physics"; section="Observables"; minutes=1
    def construct(self):
        self.heading()
        cards=[at(block("LOW ENERGY","scattering lengths",AMBER,6),-3.4,.5),
               at(block("FINITE ENERGY","cross sections",TEAL,6),3.4,.5)]
        self.reveal(cards[0])
        self.checkpoint("Scattering lengths summarize near-threshold S-wave behavior.")
        self.reveal(cards[1])
        self.play(Create(Arrow([-1.2,.5,0],[1.2,.5,0],buff=.25,color=MUTED)))
        self.takeaway("Use both to test the fitted potential")
        self.end()


class S11ChiSquare(SeminarSlide):
    number=11; title="Fit the coefficients to data"; section="Fitting"; minutes=1
    def construct(self):
        self.heading()
        eq=at(MathTex(r"\chi^2=\sum_i\left(\frac{O_i^{\rm calc}-O_i^{\rm data}}{\Delta O_i}\right)^2",
                      font_size=50,color=WHITE),0,1.3)
        self.play(Write(eq))
        self.checkpoint("Residuals are weighted by the quoted experimental uncertainty.")
        sample=VGroup()
        for i,(h,c) in enumerate(zip([1.2,.5,-.35,.7,-.55,.32],[TEAL,CORAL,TEAL,AMBER,CORAL,TEAL])):
            x=-4.5+i*1.8
            sample.add(line([x,-.75,0],[x,-.75+h,0],c,11))
        self.play(LaggedStart(*[Create(bar) for bar in sample],lag_ratio=.1))
        self.reveal(at(text("many starting points  →  multiple solutions",30,MUTED),0,-2.4))
        self.end()


class S12FitSetup(SeminarSlide):
    number=12; title="Two fit windows"; section="Fitting"; minutes=1
    def construct(self):
        self.heading()
        lo=at(block("LO  ·  2 PARAMETERS","Ecm ≤ 15 MeV",AMBER,5.6),-3.45,.5)
        nlo=at(block("NLO  ·  7 PARAMETERS","Ecm ≤ 80 MeV",TEAL,5.6),3.45,.5)
        self.reveal(lo)
        self.checkpoint("LO is constrained in a narrow energy window.")
        self.reveal(nlo)
        arrow=Arrow([-1.5,-1.25,0],[1.5,-1.25,0],buff=0,color=MUTED)
        self.play(GrowArrow(arrow))
        self.takeaway("Comparisons must keep the different fit windows visible")
        self.end()


class S13LO(SeminarSlide):
    number=13; title="LO: a narrow fit window"; section="Results"; minutes=1.1
    def construct(self):
        self.heading()
        ax,decor=plot(20,width=10)
        self.play(Create(decor),FadeIn(points(ax,20)))
        self.checkpoint("Experimental points and supplied LO calculation outputs. The fit extends to 15 MeV.")
        for i,(r,c) in enumerate(zip([1,1.5,2,2.5],[CORAL,AMBER,TEAL,BLUE])):
            self.play(Create(curve(ax,"LO",r,20,c)),FadeIn(at(text(f"R₀ {r:g} fm",22,c),5.4,1.8-i*.68)))
        self.takeaway("Regulator choice changes the LO curve")
        self.end()


class S14NLO(SeminarSlide):
    number=14; title="NLO: fit across a wider range"; section="Results"; minutes=1.1
    def construct(self):
        self.heading()
        ax,decor=plot(80,width=10)
        self.play(Create(decor),FadeIn(points(ax,80)))
        self.checkpoint("Experimental points and supplied NLO calculation outputs. The fit extends to 80 MeV.")
        for i,(r,c) in enumerate(zip([1,1.5,2],[CORAL,AMBER,TEAL])):
            self.play(Create(curve(ax,"NLO",r,80,c)),FadeIn(at(text(f"R₀ {r:g} fm",22,c),5.4,1.7-i*.75)))
        self.takeaway("Additional operators follow more of the measured curve")
        self.end()


class S15Cutoff(SeminarSlide):
    number=15; title="How stable is the singlet scattering length?"; section="Results"; minutes=1.2
    def construct(self):
        self.heading()
        radii=[.7,1,1.5,2]
        lo=[-2.630,-3.271,-3.044,-3.853]
        nlo=[-2.845,-2.873,-2.703,-2.736]
        ax=Axes(x_range=[.5,2.2,.5],y_range=[-4.2,-2.3,.5],x_length=9,y_length=4.3,
                tips=False,axis_config={"color":MUTED,"include_numbers":True,"font_size":21})
        at(ax,-1.45,-.15)
        ax.x_axis.set_opacity(0)
        baseline=line(ax.c2p(.5,-4.2),ax.c2p(2.2,-4.2),MUTED,1.5)
        ticks=VGroup()
        for radius in [1,1.5,2]:
            p=ax.c2p(radius,-4.2)
            ticks.add(line(p+UP*.06,p+DOWN*.06,MUTED,1),
                      at(text(f"{radius:g}",19,MUTED),p[0],p[1]-.25))
        self.play(Create(ax),Create(baseline),FadeIn(ticks))
        lp=VMobject(color=CORAL,stroke_width=3).set_points_as_corners(
            [ax.c2p(r,v) for r,v in zip(radii,lo)])
        np_=VMobject(color=TEAL,stroke_width=3).set_points_as_corners(
            [ax.c2p(r,v) for r,v in zip(radii,nlo)])
        self.play(Create(lp),FadeIn(at(text("LO representative",23,CORAL),5.15,1.5)))
        self.checkpoint("Singlet scattering lengths from thesis Table 2.15. LO points are selected representatives.")
        self.play(Create(np_),FadeIn(at(text("NLO cluster mean",23,TEAL),5.15,.6)))
        self.reveal(at(text("aₛ [fm] versus R₀ [fm]",23,MUTED),-1.4,-2.55))
        self.takeaway("NLO shows less regulator spread in this observable")
        self.end()


class S16Predictions(SeminarSlide):
    number=16; title="What happens beyond the fit?"; section="Results"; minutes=1.2
    def construct(self):
        self.heading()
        ax,decor=plot(220,width=9.5)
        self.play(Create(decor),FadeIn(points(ax,220)))
        self.checkpoint("The data and supplied curves extend beyond the fitted energy windows.")
        for order,r,c in [("LO",1.5,CORAL),("NLO",1.5,TEAL)]:
            self.play(Create(curve(ax,order,r,220,c)))
        self.reveal(at(text("LO  ≤15 MeV",22,CORAL),5.5,1.7),
                    at(text("NLO  ≤80 MeV",22,TEAL),5.5,.95))
        self.takeaway("Extrapolation requires caution")
        self.end()


class S17Families(SeminarSlide):
    number=17; title="Good fits can hide different forces"; section="Results"; minutes=1
    def construct(self):
        self.heading()
        def family(x, name, quality, values, color):
            shell=RoundedRectangle(corner_radius=.2,width=6,height=3.45,
                                   color=EDGE,fill_color=PANEL,fill_opacity=1)
            group=VGroup(shell,
                         at(text(name,31,color,True),0,1.22),
                         at(text(f"χ²ν = {quality}",25,MUTED),0,.57),
                         at(text(f"Cₛ = {values[0]}     Cₜ = {values[1]}",28,WHITE),0,-.26),
                         at(text(f"C₃ = {values[2]}",27,color),0,-.93))
            return at(group,x,.25)
        first=family(-3.35,"FAMILY 1","1.021",("−6.338","4.175","−1.116"),AMBER)
        second=family(3.35,"FAMILY 2","1.112",("−15.551","−4.113","10.802"),TEAL)
        self.reveal(first)
        self.checkpoint("Representative NLO fits from thesis Table 2.16 at R₀ = 1.5 fm. Cₛ and Cₜ are in fm²; C₃ is in fm⁴.")
        self.reveal(second)
        self.reveal(at(text("Selected coefficients  ·  same fit data",23,MUTED),0,-2.3))
        self.takeaway("Binding observables can help distinguish families")
        self.end()


class S18Hypertriton(SeminarSlide):
    number=18; title="The hypertriton: a three-body test"; section="Few-body physics"; minutes=.8
    def construct(self):
        self.heading()
        coords=[[-3.9,.85,0],[-1.1,.85,0],[-2.5,-1.5,0]]
        nn=CubicBezier(coords[0],[-3.2,1.15,0],[-1.8,1.15,0],coords[1],
                       color=TEAL,stroke_width=3.2)
        yn=VGroup(
            CubicBezier(coords[0],[-3.85,-.05,0],[-3.15,-1.15,0],coords[2],
                        color=AMBER,stroke_width=3.2),
            CubicBezier(coords[1],[-1.15,-.05,0],[-1.85,-1.15,0],coords[2],
                        color=AMBER,stroke_width=3.2))
        p,n,l=[at(baryon(s,.54),*point[:2])
               for s,point in zip(("p","n","Λ"),coords)]
        self.play(Create(nn),FadeIn(p),FadeIn(n))
        self.reveal(at(text("NN",25,TEAL,True),-2.5,1.42))
        self.play(Create(yn),FadeIn(l))
        self.reveal(at(text("ΛN",25,AMBER,True),-3.64,-.72),
                    at(text("ΛN",25,AMBER,True),-1.36,-.72))
        self.checkpoint("The NN pair and two ΛN pairs enter the three-body Hamiltonian.")
        eq=at(MathTex(r"H=T+V_{NN}+V_{\Lambda p}+V_{\Lambda n}",
                      font_size=42,color=WHITE),3,.45)
        self.play(Write(eq))
        self.reveal(at(text("binding energy  →  new constraint",27,MUTED),3,-1.25))
        self.takeaway("The hypertriton calculation is an outlook application")
        self.end()


class S19Jacobi(SeminarSlide):
    number=19; title="Describe internal motion with Jacobi vectors"; section="Few-body physics"; minutes=1.2
    def construct(self):
        self.heading()
        p=[-4.4,-.9,0];n=[-1.5,-.9,0];l=[-2.2,1.6,0]
        trio=VGroup(at(badge("1",CORAL,.38),*p[:2]),
                    at(badge("2",TEAL,.38),*n[:2]),
                    at(badge("3",AMBER,.38),*l[:2]))
        self.play(FadeIn(trio))
        x=Arrow(p,n,buff=.4,color=CORAL)
        midpoint=[(p[0]+n[0])/2,-.9,0]
        y=Arrow(midpoint,l,buff=.35,color=TEAL)
        self.play(GrowArrow(x),FadeIn(at(text("x : pair separation",25,CORAL),2.4,1)))
        self.checkpoint("One coordinate describes separation inside a pair.")
        self.play(GrowArrow(y),FadeIn(at(text("y : third particle relative to pair",25,TEAL),2.4,.1)))
        self.reveal(at(MathTex(r"\rho^2=x^2+y^2",font_size=48,color=WHITE),2.6,-1.35))
        self.takeaway("Separate overall motion from internal geometry")
        self.end()


class S20Symmetry(SeminarSlide):
    number=20; title="What non-symmetrized HH changes"; section="Few-body physics"; minutes=1.4
    def construct(self):
        self.heading()
        hh=at(block("CONVENTIONAL HH","symmetry in basis",AMBER,5.7),-3.4,.65)
        nshh=at(block("NSHH","symmetry after solving",TEAL,5.7),3.4,.65)
        self.reveal(hh)
        self.checkpoint("Conventional HH constructs basis functions with the required exchange symmetry.")
        self.reveal(nshh)
        eq=at(MathTex(r"P_{12}\psi=-\psi",font_size=52,color=WHITE),0,-1.1)
        self.play(Write(eq))
        self.takeaway("The physical state still obeys fermion symmetry")
        self.end()


class S21Benchmark(SeminarSlide):
    number=21; title="Validate the solver with the triton"; section="Few-body physics"; minutes=1.1
    def construct(self):
        self.heading()
        values=[("a","−10.706","−10.705"),("b","−8.463","−8.463"),
                ("c","−7.066","−7.066"),("d","−6.137","−6.136"),
                ("o","−9.696","−9.696")]
        headers=[("MODEL",-4.9),("NSHH [MeV]",-.7),("HH [MeV]",3.75)]
        self.reveal(*[at(text(s,25,TEAL,True),x,2.15) for s,x in headers])
        self.checkpoint("LO triton ground-state energies transcribed from the supplied seminar.")
        for i,(name,a,b) in enumerate(values):
            y=1.25-i*.66
            self.reveal(at(text(name,27,WHITE),-4.9,y),
                        at(text(a,27,WHITE),-.7,y),
                        at(text(b,27,WHITE),3.75,y),run_time=.35)
        self.takeaway("Agreement within 1 keV at displayed precision")
        self.end()


class S22Outlook(SeminarSlide):
    number=22; title="From scattering to the hypertriton"; section="Outlook"; minutes=1.5
    def construct(self):
        self.heading()
        steps=[("1","FIT THE FORCE","ΛN scattering",CORAL),
               ("2","TEST THE MODEL","regulator stability",AMBER),
               ("3","PREDICT BINDING","hypertriton with NSHH",TEAL)]
        for i,(n,head,detail,color) in enumerate(steps):
            x=-4.75+i*4.75
            card=at(block(head,detail,color,4.15),x,.4)
            self.reveal(card)
            if i<2:self.checkpoint("The fit and its regulator sensitivity provide the input to few-body calculations.")
        self.takeaway("Which new observables best constrain the force?")
        self.end()


SCENES = [S01Aim,S02Applications,S03Levels,S04EOS,S05Features,S06EFT,
          S07Potential,S08Regulator,S09Scattering,S10Observables,S11ChiSquare,
          S12FitSetup,S13LO,S14NLO,S15Cutoff,S16Predictions,S17Families,
          S18Hypertriton,S19Jacobi,S20Symmetry,S21Benchmark,S22Outlook]
