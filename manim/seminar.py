"""Animated scientific seminar. All authoring and new plotting live in this project.
Render the named S01...S22 scenes in Full HD; then run build_player.py.
Source evidence is copied read-only by prepare_assets.py.
"""
from pathlib import Path
import csv, json, os
import numpy as np
import manimpango
from manim import *
from manim_slides import Slide

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'assets'
# Palette sampled from seminario_passaggio_anno.pdf.
CREAM='#FFFCF5'; INK='#3D4545'; DARK='#322C21'; TEAL='#3C7F72'; ORANGE='#D24923'; GOLD='#F8B037'; MUTED='#737874'; GRID='#DDD9CF'; PALE='#E4EDE5'
RUST='#992800'; ACCENT='#C53807'
FONT='Open Sans SemiCondensed'
TITLE_FONT='Yanone Kaffeesatz'
# Register project-local fonts: no dependence on the viewer's installed fonts.
for font_file in sorted((ASSETS/'fonts').glob('*.ttf')):
 if not manimpango.register_font(str(font_file)):
  raise RuntimeError(f'Could not register font: {font_file}')
TOTAL=22

def txt(s,size=28,color=INK,weight=NORMAL):
 # Existing medium-weight labels are the deck's main sentences and subheadings.
 main=weight==MEDIUM
 return Text(s,font=TITLE_FONT if main else FONT,font_size=size*1.18 if main else size,
  color=color,weight=BOLD if main else weight,line_spacing=.65)
def headline(s,size=48,color=CREAM):
 return Text(s,font=TITLE_FONT,font_size=size,color=color,weight=BOLD,line_spacing=.55)
def math(s,size=34,color=INK):
 return MathTex(s,font_size=size,color=color)
def place(m,x,y): return m.move_to([x,y,0])
def left(m,x,y): return m.move_to([x+m.width/2,y,0])
def fit(m,w):
 if m.width>w: m.scale_to_fit_width(w)
 return m

def particle(label,color,r=.34):
 body=Circle(r,color=color,stroke_width=2,fill_color=color,fill_opacity=.15)
 return VGroup(body,txt(label,26,color,MEDIUM))

def model(order,radius,envelope=False):
 tag=f'{radius:g}'.replace('.','p')
 name=f'cross_section_uncertainty_{order.lower()}_r0_{tag}.csv' if envelope else f'{order.lower()}_r0{radius:.1f}'.replace('.','p')+'.csv'
 rows=[]
 with (ASSETS/name).open() as f:
  for row in csv.DictReader(f):
   if row['observable']=='cross_section': rows.append((float(row['ecm_mev']),float(row['cross_section_mb'])))
 # Identical duplicate energies occur where multiple measurements share a bin.
 values={x:y for x,y in rows}
 return np.array(sorted(values.items()))
def experiment():
 rows=[]
 for line in (ASSETS/'experimental_cross_section.dat').read_text().splitlines():
  if line.startswith('#') or not line.strip():continue
  f=line.split();rows.append([float(v) for v in f[:6]])
 return np.array(rows)

class SeminarSlide(Slide):
 number=0; title=''; section=''; minutes=1; dark=False
 def setup(self):
  super().setup(); self.camera.background_color=ManimColor(CREAM);self.beat=0
 def play(self,*animations,**kwargs):
  # The reference builds ideas in a gentle sequence, with time to follow motion.
  duration=float(kwargs.pop('run_time',1))
  entrances=(FadeIn,Create,Write,GrowArrow,GrowFromCenter)
  staged=len(animations)>1 and all(isinstance(a,entrances) for a in animations)
  if staged:
   duration=duration*1.25+min(.9,.14*(len(animations)-1))
   animations=(LaggedStart(*animations,lag_ratio=.16),)
  else:
   duration=max(.7,duration*1.25)
  kwargs.setdefault('rate_func',smooth)
  return super().play(*animations,run_time=duration,**kwargs)
 def focus_on(self,mobject,color=TEAL):
  self.play(Circumscribe(mobject,color=color,buff=.12,stroke_width=1.5),run_time=1.1)
 def reveal_curve(self,graph,label):
  tip=Dot(graph.get_start(),radius=.052,color=graph.get_color())
  self.add(tip)
  self.play(Create(graph),MoveAlongPath(tip,graph),FadeIn(label),run_time=1.45)
  self.remove(tip)
 def frame(self):
  # The reference's full-width charcoal banner, four stripes, and hanging tab.
  band=Rectangle(width=16,height=1.08,stroke_width=0,fill_color=DARK,fill_opacity=1).move_to([0,3.43,0])
  stripes=VGroup(*[Rectangle(width=2.84,height=.183,stroke_width=0,fill_color=c,fill_opacity=1)
   .move_to([-6.58,3.80-i*.244,0]) for i,c in enumerate([TEAL,RUST,ORANGE,GOLD])])
  header=left(fit(headline(self.title,48),10.9),-5.04,3.43)
  # Straight sides meet a semicircular bottom, like the PDF's page-number marker.
  tab=Union(Rectangle(width=1.02,height=.53).move_to([6.64,4.235,0]),
   Circle(radius=.51).move_to([6.64,4.0,0]),fill_color=ACCENT,fill_opacity=1,stroke_width=0)
  n=place(Text(str(self.number),font=FONT,font_size=39,color=CREAM,weight=BOLD,slant=ITALIC),6.64,4.02)
  footer=Text('Margherita Sagina (University of Pisa)',font=FONT,font_size=19,color=INK,weight=SEMIBOLD,slant=ITALIC).move_to([0,-4.16,0])
  gap=footer.width/2+.24
  rules=VGroup(Line([-8,-4.16,0],[-gap,-4.16,0],color=DARK,stroke_width=5),
   Line([gap,-4.16,0],[8,-4.16,0],color=DARK,stroke_width=5))
  self.add(band,stripes,header,tab,n,rules,footer)
  previous=sorted((ROOT/'work/stills').glob(f'{self.number-1:02d}-*.png'))
  if previous:
   # Dissolve the previous explanation into the next while the frame stays still.
   transition=ImageMobject(str(previous[-1])).set(width=16).set_z_index(100)
   self.add(transition)
   self.play(FadeOut(transition),run_time=.55)
  else:
   self.remove(header,stripes,n)
   self.play(FadeIn(header),LaggedStart(*[FadeIn(line) for line in stripes],lag_ratio=.12),FadeIn(n),run_time=.8)
 def note(self,s):
  return f'{self.title}\nSuggested speaking time: {self.minutes:g} min.\n{s}'
 def pause(self,s=''):
  self.wait(.15)
  self.beat+=1
  folder=ROOT/'work'/'stills';folder.mkdir(parents=True,exist_ok=True)
  self.renderer.camera.get_image().save(folder/f'{self.number:02d}-{self.beat:02d}.png')
  self.next_slide(notes=self.note(s))
 def finish(self,s=''):
  self.wait(.2)
  self.beat+=1
  folder=ROOT/'work'/'stills';folder.mkdir(parents=True,exist_ok=True)
  self.renderer.camera.get_image().save(folder/f'{self.number:02d}-{self.beat:02d}.png')
 def takeaway(self,s,color=TEAL):
  t=fit(txt(s,27,color,MEDIUM),14.1);place(t,0,-3.18)
  box=SurroundingRectangle(t,buff=.14,corner_radius=.08,color=color,stroke_width=1.3,
   fill_color=color,fill_opacity=.035)
  self.play(Create(box),FadeIn(t),run_time=.85);return t
 def plot_axes(self,xmax=80,width=10.4,height=3.8,center=(-.7,-.25),ymax=280):
  ax=Axes(x_range=[0,xmax,20 if xmax>=80 else 5],y_range=[0,ymax,50],x_length=width,y_length=height,tips=False,
   axis_config={'color':INK,'stroke_width':1.7,'include_numbers':True,'font_size':21,'decimal_number_config':{'num_decimal_places':0,'color':INK}})
  place(ax,center[0],center[1]+.15)
  xl=math(r'E_{\mathrm{CM}}\ [\mathrm{MeV}]',26).next_to(ax.x_axis,DOWN,buff=.35)
  yl=math(r'\sigma\ [\mathrm{mb}]',25).next_to(ax.y_axis,UP,buff=.18)
  grid=VGroup(*[Line(ax.c2p(0,y),ax.c2p(xmax,y),stroke_width=.7,color=GRID) for y in [50,100,150,200,250] if y<ymax])
  return ax,VGroup(ax,xl,yl,grid)
 def data_dots(self,ax,xmax=80,highlight=None):
  dots=VGroup()
  for p,dp,x,dx,y,dy in experiment():
   if x>xmax or y>280:continue
   c=MUTED if highlight is None or x<=highlight else '#ABB1A7'
   vert=Line(ax.c2p(x,max(0,y-dy)),ax.c2p(x,min(280,y+dy)),color=c,stroke_width=1.2)
   hor=Line(ax.c2p(max(0,x-dx),y),ax.c2p(min(xmax,x+dx),y),color=c,stroke_width=1)
   dot=Dot(ax.c2p(x,y),radius=.037,color=c)
   dots.add(VGroup(vert,hor,dot))
  return dots
 def curve(self,ax,order,radius,xmax=80,envelope=False,color=None):
  vals=model(order,radius,envelope);vals=vals[(vals[:,0]<=xmax)&(vals[:,1]>=0)&(vals[:,1]<=280)]
  return VMobject(color=color or (ORANGE if order=='LO' else TEAL),stroke_width=3.4).set_points_as_corners([ax.c2p(x,y) for x,y in vals])

class S01Aim(SeminarSlide):
 number=1;title='The hyperon–nucleon interaction';section='Aim';minutes=.5
 def construct(self):
  # Cover retains the original aim, with an explicit physical interaction as the focal point.
  self.frame()
  intro=left(txt('PhD research seminar',20,ACCENT,MEDIUM),-7.1,2.32)
  title=left(headline('The hyperon–nucleon\ninteraction',58,INK),-7.1,1.30)
  subtitle=left(txt('A local contact model\nconstrained by scattering data',30,INK),-7.1,-.55)
  author=left(txt('Margherita Sagina',27,INK,MEDIUM),-7.1,-2.9)
  affil=left(txt('University of Pisa  /  INFN',19,MUTED),-7.1,-3.45)
  self.play(FadeIn(intro),FadeIn(title,shift=UP*.2),run_time=1)
  a=place(particle('Λ',GOLD,.83),3.1,.45);b=place(particle('N',ORANGE,.83),6,.45)
  bond=DashedLine(a.get_right()+RIGHT*.1,b.get_left()-RIGHT*.1,color=INK,dash_length=.09,stroke_width=2)
  pot=place(math(r'V_{\Lambda N}(r)',38,INK),4.55,-.8)
  self.play(FadeIn(a),FadeIn(b),Create(bond),run_time=.9)
  self.play(FadeIn(pot),FadeIn(subtitle),FadeIn(author),FadeIn(affil),run_time=.8)
  question=left(txt('How well do the data determine the force?',25,ACCENT,MEDIUM),-7.1,-1.8)
  self.play(FadeIn(question),run_time=.7)
  self.finish()

class S02Applications(SeminarSlide):
 number=2;title='Why study the ΛN interaction?';section='Applications';minutes=.8
 def construct(self):
  self.frame()
  a=left(txt('Neutron-star matter',31,TEAL,MEDIUM),-6.6,1.95)
  b=left(txt('Light hypernuclei',31,ORANGE,MEDIUM),1.0,1.95)
  self.play(FadeIn(a),FadeIn(b),run_time=.7)
  # Physical schematics, not quantitative stellar models.
  cloud=VGroup(*[particle('n' if i%4 else 'Λ',TEAL if i%4 else GOLD,.22).move_to([-5.4+(i%4)*.73,.55-(i//4)*.7,0]) for i in range(12)])
  h=VGroup(place(particle('p',ORANGE,.42),2.2,.35),place(particle('n',TEAL,.42),3.6,.35),place(particle('Λ',GOLD,.42),4.6,-.8))
  lines=VGroup(Line(h[0].get_center(),h[1].get_center(),color=MUTED),Line(h[0].get_center(),h[2].get_center(),color=MUTED),Line(h[1].get_center(),h[2].get_center(),color=MUTED))
  self.play(LaggedStart(*[FadeIn(o) for o in cloud],lag_ratio=.05),Create(lines),FadeIn(h),run_time=1.3)
  self.pause('Original project motivation: the interaction affects composition and the equation of state. The few-body branch provides a controlled application. All particle positions are schematic.')
  desc1=left(txt('Composition and pressure\nThe hyperon puzzle',27),-6.6,-2)
  desc2=left(txt('Binding energies\nThe hypertriton  ³ΛH',27),1,-2)
  self.play(FadeIn(desc1),FadeIn(desc2),run_time=.7)
  self.takeaway('The same microscopic interaction enters both applications')
  self.finish()

class S03Levels(SeminarSlide):
 number=3;title='Hyperons open additional states';section='Applications';minutes=1.4
 def construct(self):
  self.frame()
  axis=Arrow([-6.5,-1.85,0],[-6.5,2,0],color=INK,buff=0)
  energy=left(txt('Energy',23),-6.65,2.25)
  ntitle=place(txt('Neutrons',29,TEAL,MEDIUM),-3.7,2.1)
  ltitle=place(txt('Λ hyperons',29,GOLD,MEDIUM),2.5,2.1)
  levels=VGroup(*[Line([-5.35,-1.45+i*.53,0],[-2,-1.45+i*.53,0],color=TEAL,stroke_width=2) for i in range(6)])
  llevels=VGroup(*[Line([.9,.1+i*.53,0],[4.25,.1+i*.53,0],color=GOLD,stroke_width=2) for i in range(3)])
  self.play(Create(axis),FadeIn(energy),FadeIn(ntitle),FadeIn(ltitle),Create(levels),Create(llevels),run_time=1)
  low=VGroup(*[Dot([-4.5+j*.85,-1.45+i*.53,0],radius=.09,color=TEAL) for i in range(3) for j in range(3)])
  self.play(LaggedStart(*[FadeIn(d) for d in low],lag_ratio=.08),run_time=1)
  self.pause('Schematic energy levels including species-dependent energy offsets. These are not neutron-star spectra. Increasing density increases the neutron chemical potential.')
  high=VGroup(*[Dot([-4.5+j*.85,-1.45+i*.53,0],radius=.09,color=TEAL) for i in range(3,6) for j in range(3)])
  self.play(LaggedStart(*[FadeIn(d) for d in high],lag_ratio=.1),run_time=1.2)
  mu=DashedLine([-5.6,1.46,0],[4.8,1.46,0],color=ORANGE)
  mul=left(math(r'\mu_n',28,ORANGE),5,1.46)
  self.play(Create(mu),FadeIn(mul),run_time=.7)
  self.pause('Once the relevant chemical-equilibrium threshold is reached, additional baryon species can become energetically favourable. The actual onset depends on the interactions.')
  paths=[ArcBetweenPoints(d.get_center(),[1.75+j*.85,.1,0],angle=-.25) for j,d in enumerate(high[-3:])]
  trails=VGroup(*[TracedPath(d.get_center,stroke_color=GOLD,stroke_width=2,stroke_opacity=.28) for d in high[-3:]])
  self.add(trails)
  self.play(*[MoveAlongPath(d,path) for d,path in zip(high[-3:],paths)],run_time=1.8)
  for d in high[-3:]:d.set_color(GOLD)
  for trail in trails:trail.clear_updaters()
  self.play(FadeOut(trails),run_time=.35)
  label=place(txt('A new species can reduce the energy cost',29,TEAL,MEDIUM),0,-2.55)
  caveat=place(txt('Schematic illustration. Interactions determine the onset.',19,MUTED),0,-3.35)
  self.play(FadeIn(label),FadeIn(caveat),run_time=.7);self.finish()

class S04EOS(SeminarSlide):
 number=4;title='The hyperon puzzle';section='Applications';minutes=1.3
 def construct(self):
  self.frame()
  ax=Axes(x_range=[0,1,1],y_range=[0,1,1],x_length=7,y_length=4,tips=False,axis_config={'color':INK,'include_ticks':False}).move_to([-2.4,-.2,0])
  labels=VGroup(math(r'\varepsilon\quad\text{Energy density}',26).next_to(ax.x_axis,DOWN,buff=.3),math(r'P\quad\text{Pressure}',26).next_to(ax.y_axis,UP,buff=.15))
  nucleonic=ax.plot(lambda x:.82*x**1.5,x_range=[.06,1],color=TEAL,stroke_width=4)
  hyper=ax.plot(lambda x:.82*x**1.5 if x<.45 else .82*.45**1.5+.36*(x-.45),x_range=[.06,1],color=ORANGE,stroke_width=4)
  self.play(Create(ax),FadeIn(labels),Create(nucleonic),run_time=1.1)
  nlab=place(txt('Nucleonic model',24,TEAL),-.9,1.3)
  self.play(FadeIn(nlab));self.pause('The equation of state relates pressure to energy density. Curves are qualitative, not numerical research results. Source context: Logoteta, Universe 7, 408 (2021), doi:10.3390/universe7110408.')
  self.play(TransformFromCopy(nucleonic,hyper),run_time=1.6)
  hlab=place(txt('With hyperons',24,ORANGE),-.55,-.35)
  right=left(txt('Lower pressure\nat the same energy density',26),2.2,1.1)
  right2=left(txt('Many models then support\na smaller maximum mass',26),2.2,-.1)
  obs=left(txt('Observed stars reach\nabout 2 solar masses',28,TEAL,MEDIUM),2.2,-1.6)
  self.play(FadeIn(hlab),FadeIn(right),FadeIn(right2),run_time=.8);self.pause('Softening and the resulting maximum mass are model dependent. A contact model fitted at low energy is a starting point for studying the force, not a direct dense-matter prediction.')
  self.play(FadeIn(obs));self.takeaway('A reliable hyperonic interaction is part of the problem')
  self.add(place(txt('Qualitative EoS curves',17,MUTED),-2.5,2.15));self.finish()

class S05Features(SeminarSlide):
 number=5;title='A local contact interaction';section='Model';minutes=.8
 def construct(self):
  self.frame()
  a=place(particle('Λ',GOLD,.54),-5.4,.25);b=place(particle('N',TEAL,.54),-2.6,.25)
  dist=DoubleArrow(a.get_right()+RIGHT*.1,b.get_left()-RIGHT*.1,buff=0,color=INK)
  r=place(math('r',32),-4,.8)
  local=left(txt('Local',34,TEAL,MEDIUM),-6.5,1.85)
  desc=left(txt('Coordinate-space interaction\nRelative distance and spin operators',27),-6.5,-1.5)
  contact=left(txt('Contact EFT',34,ORANGE,MEDIUM),1.0,1.85)
  eq=left(math(r'V(r)=\sum_i C_i\,O_i(r)',38),1,.15)
  desc2=left(txt('Short-range physics in contact terms\nCoefficients fitted to data',27),1,-1.5)
  self.play(FadeIn(local),FadeIn(a),FadeIn(b),GrowArrow(dist),FadeIn(r),FadeIn(desc),run_time=1)
  self.pause('Local means the potential acts at the same relative coordinate. Spin-orbit operators still involve derivatives, so distance-only wording is a simplification.')
  self.play(FadeIn(contact),FadeIn(eq),FadeIn(desc2),run_time=.8)
  self.takeaway('A simple operator structure for demanding nuclear calculations');self.finish()

class S06EFT(SeminarSlide):
 number=6;title='Effective field theory and resolution';section='EFT';minutes=1.2
 def construct(self):
  self.frame()
  configs=[('QCD','Quarks and gluons','qcd',-5.1),('Chiral EFT','Baryons and explicit mesons','chiral',0),('Contact EFT','Baryons and contact terms','contact',5.1)]
  groups=[]
  for title,desc,file,x in configs:
   pic=ImageMobject(str(ASSETS/f'eft_{file}.png'));pic.scale_to_fit_height(2.8);pic.move_to([x,-.15,0])
   head=place(txt(title,31,ORANGE if file=='contact' else TEAL,MEDIUM),x,1.9)
   sub=fit(txt(desc,22),4.5);place(sub,x,-2.12)
   groups.append(Group(head,pic,sub))
  for i,g in enumerate(groups):
   self.play(FadeIn(g,shift=LEFT*.18),run_time=.85)
   if i<2:self.pause('Original EFT drawings retained from the supplied seminar. They depict NN examples to explain resolution. In the hyperonic application the retained baryons include Λ. The expansion is controlled by Q divided by a breakdown scale, rather than universal laboratory-energy cutoffs.')
  self.play(groups[0].animate.set_opacity(.5),groups[1].animate.set_opacity(.5),run_time=.6)
  focus=SurroundingRectangle(groups[2],buff=.25,color=ORANGE,stroke_width=2)
  self.play(Create(focus));self.takeaway('Unresolved meson dynamics enters the fitted contact coefficients')
  self.finish()

class S07Potential(SeminarSlide):
 number=7;title='The ΛN potential in coordinate space';section='EFT';minutes=1.4
 def construct(self):
  self.frame()
  lo=math(r'V^{\mathrm{LO}}_{\Lambda N}=\left[C_S+C_T(\boldsymbol\sigma_\Lambda\!\cdot\!\boldsymbol\sigma_N)\right]F(r)',37)
  left(lo,-6.9,1.88)
  lab=left(txt('LO: 2 free coefficients',26,ORANGE,MEDIUM),3.65,.96)
  lo.save_state();lab.save_state()
  lo.scale(1.18).move_to([0,.7,0]);lab.move_to([0,-.55,0])
  self.play(Write(lo),FadeIn(lab),run_time=1.2)
  self.pause('LO has central and spin-spin contact terms. Potential derived in earlier group work and reviewed here for this audience.')
  self.play(Restore(lo),Restore(lab),run_time=1.15)
  eqs=[r'V^{\mathrm{NLO}}_{\Lambda N}=\left[C_1+C_2(\boldsymbol\sigma_\Lambda\!\cdot\!\boldsymbol\sigma_N)\right]\left[-F^{(2)}(r)-\frac{2}{r}F^{(1)}(r)\right]',r'\qquad-C_3\frac{F^{(1)}(r)}{r}\,\boldsymbol L\!\cdot\!\boldsymbol S',r'\qquad-C_4\left[F^{(2)}(r)-\frac{F^{(1)}(r)}{r}\right]S_{\Lambda N}(\hat{\boldsymbol r})',r'\qquad-C_5\frac{F^{(1)}(r)}{r}\,\boldsymbol L\!\cdot\!\boldsymbol D']
  ms=VGroup(*[fit(math(e,32),11.2) for e in eqs]).arrange(DOWN,aligned_edge=LEFT,buff=.21)
  left(ms,-6.9,-.42)
  self.play(LaggedStart(*[Write(m) for m in ms],lag_ratio=.28),run_time=2.4)
  nlo=left(txt('NLO: 5 additional\ncoefficients',25,TEAL,MEDIUM),3.9,-1.95)
  self.play(FadeIn(nlo));self.pause('Here V NLO denotes the correction. The interaction used at NLO is V LO plus this correction. S, tensor, and D are the spin-orbit, tensor, and antisymmetric spin-orbit structures. Source: PhD summary Eq. 2.1–2.5.')
  self.takeaway('At NLO we fit all 7 coefficients together');self.finish()

class S08Regulator(SeminarSlide):
 number=8;title='The regulator sets the short-distance resolution';section='EFT';minutes=1
 def construct(self):
  self.frame()
  formula=left(math(r'F(r)=\frac{e^{-r^2/R_0^2}}{\pi^{3/2}R_0^3}',39),-6.6,1.45)
  derivs=left(math(r'F^{(1)}=\frac{dF}{dr},\qquad F^{(2)}=\frac{d^2F}{dr^2}',31),-6.6,-.1)
  desc=left(txt('R₀ changes the width\nand the height of the Gaussian',27),-6.6,-1.7)
  ax=Axes(x_range=[0,4,1],y_range=[0,.2,.1],x_length=6.6,y_length=3.65,tips=False,axis_config={'color':INK,'include_numbers':True,'font_size':21,'decimal_number_config':{'color':INK}}).move_to([3.5,-.35,0])
  xl=math(r'r\ [\mathrm{fm}]',25).next_to(ax.x_axis,DOWN)
  yl=math(r'F(r)\ [\mathrm{fm}^{-3}]',23).next_to(ax.y_axis,UP)
  def g(r):return ax.plot(lambda x:np.exp(-x*x/r**2)/(np.pi**1.5*r**3),x_range=[0,4],color=TEAL,stroke_width=4)
  radius=ValueTracker(1)
  graph=always_redraw(lambda:g(radius.get_value()));val=place(txt('R₀ = 1.0 fm',27,TEAL,MEDIUM),3.5,2)
  self.play(FadeIn(formula),FadeIn(derivs),FadeIn(desc),Create(ax),FadeIn(xl),FadeIn(yl),Create(graph),FadeIn(val),run_time=1.2)
  self.pause('This graph evaluates the actual normalized regulator, not a potential. Increasing R0 broadens it while preserving its 3D normalization.')
  for r in [1.5,2.0,2.5]:
   next_val=place(txt(f'R₀ = {r:.1f} fm',27,TEAL,MEDIUM),3.5,2)
   self.play(radius.animate.set_value(r),TransformMatchingShapes(val,next_val),run_time=1.45)
   val=next_val
  self.takeaway('We refit the coefficients for each R₀');self.finish()

class S09Scattering(SeminarSlide):
 number=9;title='Two particles, one scattering wavefunction';section='Scattering';minutes=1.2
 def construct(self):
  self.frame()
  a=place(particle('Λ',GOLD,.35),-5.6,1.45);b=place(particle('p',TEAL,.35),-3.45,1.45)
  rel=Arrow(a.get_center(),b.get_center(),buff=.45,color=INK)
  eq=left(math(r'\Psi(\boldsymbol R,\boldsymbol r)=\Psi_{\mathrm{CM}}(\boldsymbol R)\,\psi(\boldsymbol r)',32),-.8,1.45)
  self.play(FadeIn(a),FadeIn(b),GrowArrow(rel),FadeIn(eq),run_time=.8)
  ax=Axes(x_range=[0,10,2],y_range=[-1.2,1.2,1],x_length=11.8,y_length=2.35,tips=False,axis_config={'color':MUTED,'include_ticks':False}).move_to([0,-.5,0])
  free=ax.plot(lambda r:np.sin(1.8*r),x_range=[0,10],color=MUTED,stroke_width=2)
  delta=ValueTracker(0)
  phase=always_redraw(lambda:ax.plot(lambda r:np.sin(1.8*r+delta.get_value()),x_range=[0,10],color=TEAL,stroke_width=3.5))
  labels=VGroup(place(txt('Free reference',22,MUTED),-4,-2.1),place(txt('Interacting solution',22,TEAL),1.8,-2.1))
  self.play(Create(ax),Create(free),Create(phase),FadeIn(labels),run_time=1.2)
  self.pause('Schematic reduced radial S-wave outside the interaction region. Spatial profiles, not a classical trajectory or a time-dependent collision movie. The full scattering solution can include coupled channels.')
  self.play(delta.animate.set_value(.75),run_time=2)
  formula=place(math(r'u_0(r)\propto\sin(kr+\delta_0)',35),0,-2.55)
  self.play(FadeIn(formula));self.takeaway('The interaction changes the asymptotic phase');self.finish()

class S10Observables(SeminarSlide):
 number=10;title='Phase shifts, cross sections, scattering lengths';section='Scattering';minutes=1.2
 def construct(self):
  self.frame()
  h1=left(txt('Scattering at finite energy',29,TEAL,MEDIUM),-6.7,1.93)
  h2=left(txt('The low-energy limit',29,ORANGE,MEDIUM),1,1.93)
  e1=left(math(r'\sigma_L=\frac{4\pi}{k^2}(2L+1)\sin^2\delta_L',34),-6.7,.6)
  cap=left(txt('Illustration for one uncoupled channel\nThe calculation sums the spin channels',23,MUTED),-6.7,-.55)
  e2=left(math(r'k\cot\delta_0=-\frac{1}{a}+O(k^2)',35),1,.6)
  cap2=left(txt('Scattering length a\nSummarises the threshold behaviour',25),1,-.55)
  self.play(FadeIn(h1),FadeIn(e1),FadeIn(cap),run_time=.8);self.pause('The displayed partial-wave formula is a pedagogical single-channel expression. The actual unpolarized Λp calculation includes channel coupling and spin weights.')
  self.play(FadeIn(h2),FadeIn(e2),FadeIn(cap2),run_time=.8)
  cs=left(txt('Unpolarized data mix singlet and triplet contributions',26),-6.7,-1.8)
  cons=left(txt('Additional constraints on a_s and a_t help separate them',27,TEAL,MEDIUM),-6.7,-2.5)
  self.play(FadeIn(cs),FadeIn(cons));self.add(place(txt('Scattering lengths inferred through femtoscopic analysis, not direct measurements',18,MUTED),0,-3.35));self.finish()

class S11ChiSquare(SeminarSlide):
 number=11;title='Constraining the interaction with data';section='Fitting';minutes=1
 def construct(self):
  self.frame()
  a=math(r'\chi^2(\boldsymbol C)=\sum_i\frac{[\sigma_i^{\mathrm{th}}(\boldsymbol C)-\sigma_i^{\mathrm{exp}}]^2}{(\Delta\sigma_i)^2}',40)
  left(a,-6.5,1.2)
  b=math(r'+\sum_{j=s,t}\frac{[a_j^{\mathrm{th}}(\boldsymbol C)-a_j^{\mathrm{inferred}}]^2}{(\Delta a_j)^2}',40)
  left(b,-3.2,-.35)
  a.save_state();a.scale(1.12).move_to([0,.55,0])
  self.play(Write(a),run_time=1.2);self.pause('Each residual measures a difference relative to its assigned uncertainty. Cross sections from NN-online experimental archive.')
  self.play(Restore(a),run_time=.95)
  self.play(Write(b),run_time=1.15)
  vals=place(math(r'a_s\in[-3.34,-2.10]\ \mathrm{fm}\qquad a_t\in[-1.56,-1.18]\ \mathrm{fm}',30),0,-1.8)
  self.play(FadeIn(vals));self.takeaway('Cross sections and threshold information constrain the same coefficients')
  self.add(place(txt('Mihaylov et al. (2024), Phys. Lett. B 850, 138550',18,MUTED),0,-3.75));self.finish()

class S12FitSetup(SeminarSlide):
 number=12;title='The fitting strategy';section='Fitting';minutes=.9
 def construct(self):
  self.frame()
  lo=left(txt('Leading order',32,ORANGE,MEDIUM),-6.6,1.9)
  nlo=left(txt('Next-to-leading order',32,TEAL,MEDIUM),1,1.9)
  col1=VGroup(txt('2 free parameters',34,ORANGE,MEDIUM),math(r'C_S,\ C_T',34),math(r'E_{\mathrm{CM}}\leq15\ \mathrm{MeV}',32),txt('S-wave fit',25)).arrange(DOWN,aligned_edge=LEFT,buff=.4)
  col2=VGroup(txt('7 free parameters',34,TEAL,MEDIUM),math(r'C_S,\ C_T,\ C_1,\ldots,C_5',34),math(r'E_{\mathrm{CM}}\leq80\ \mathrm{MeV}',32),txt('S- and P-wave contributions',25)).arrange(DOWN,aligned_edge=LEFT,buff=.4)
  left(col1,-6.6,-.1);left(col2,1,-.1)
  self.play(FadeIn(lo),LaggedStart(*[FadeIn(m) for m in col1],lag_ratio=.22),run_time=1.4)
  self.play(FadeIn(nlo),LaggedStart(*[FadeIn(m) for m in col2],lag_ratio=.22),run_time=1.4)
  self.pause('LO and NLO use different fit windows and operator content. Therefore compare their physical behaviour with those differences explicit.')
  self.takeaway('Many initial guesses test the dependence on the starting point')
  self.finish()

class S13LO(SeminarSlide):
 number=13;title='Leading-order results';section='Results';minutes=1.1
 def construct(self):
  self.frame();ax,decor=self.plot_axes(20,width=10.6,center=(-1,-.2))
  dots=self.data_dots(ax,20,15)
  line=DashedLine(ax.c2p(15,0),ax.c2p(15,280),color=MUTED)
  self.play(Create(decor),FadeIn(dots),Create(line),run_time=.9)
  side=VGroup(txt('2 parameters',27,ORANGE,MEDIUM),txt('Fit window',22),math(r'E_{\mathrm{CM}}\leq15\ \mathrm{MeV}',27)).arrange(DOWN,aligned_edge=LEFT,buff=.3);left(side,4.8,1.2)
  self.play(FadeIn(side))
  curves=[]
  for i,r in enumerate([1,1.5,2,2.5]):
   c=[ORANGE,TEAL,GOLD,RUST][i]
   graph=self.curve(ax,'LO',r,20,color=c);label=left(txt(f'R₀ = {r:g} fm',24,c,MEDIUM),4.8,-.35-i*.48)
   self.reveal_curve(graph,label);curves.append(graph)
   if i==1:self.pause('Actual cross-section CSVs from the original plotting project, copied read-only. Points outside 15 MeV are comparisons, not fitted data. Curve segments join the supplied calculated energies.')
  self.takeaway('The LO description becomes more sensitive to softer regulators');self.finish()

class S14NLO(SeminarSlide):
 number=14;title='Next-to-leading-order results';section='Results';minutes=1.1
 def construct(self):
  self.frame();ax,decor=self.plot_axes(80,width=10.6,center=(-1,-.2))
  dots=self.data_dots(ax,80)
  self.play(Create(decor),FadeIn(dots),run_time=.9)
  side=VGroup(txt('7 parameters',27,TEAL,MEDIUM),txt('Fit window',22),math(r'E_{\mathrm{CM}}\leq80\ \mathrm{MeV}',27)).arrange(DOWN,aligned_edge=LEFT,buff=.3);left(side,4.8,1.2)
  self.play(FadeIn(side))
  for i,r in enumerate([1,1.5,2]):
   c=[ORANGE,TEAL,GOLD][i];g=self.curve(ax,'NLO',r,80,color=c)
   label=left(txt(f'R₀ = {r:g} fm',24,c,MEDIUM),4.8,-.4-i*.52)
   self.reveal_curve(g,label)
   if i==0:self.pause('NLO fitted curves from the provided analysis outputs. The full potential has seven fitted coefficients. ECM denotes centre-of-mass kinetic energy.')
  self.takeaway('Additional operators describe a wider fitted energy interval');self.finish()

class S15Cutoff(SeminarSlide):
 number=15;title='NLO reduces the regulator dependence';section='Results';minutes=1.2
 def construct(self):
  self.frame()
  # Values from thesis Table 2.15, preserving the distinction between LO representatives and NLO cluster means.
  radii=[.7,1,1.5,2]
  lo_s=[-2.630,-3.271,-3.044,-3.853];lo_t=[-1.115,-1.554,-1.548,-1.929]
  ns=[(-2.857,-2.834),(-2.923,-2.823),(-2.819,-2.587),(-2.758,-2.714)]
  nt=[(-1.427,-1.407),(-1.464,-1.421),(-1.440,-1.423),(-1.393,-1.371)]
  plots=[]
  for x,tag,los,nlos,ylim,step in [(-3.85,'a_s',lo_s,ns,[-4,-2.3],.5),(3.85,'a_t',lo_t,nt,[-2.1,-1],.5)]:
   ax=Axes(x_range=[.5,2.2,.5],y_range=[*ylim,step],x_length=5.9,y_length=3.4,tips=False,axis_config={'color':INK,'include_numbers':True,'font_size':22,'decimal_number_config':{'color':INK}}).move_to([x,-.3,0])
   lab=math(tag+r'\ [\mathrm{fm}]',32).next_to(ax.y_axis,UP,buff=.1)
   # Hide the y=0 horizontal axis; draw a bottom axis without changing coordinates.
   ax.x_axis.set_opacity(0)
   bottom=Line(ax.c2p(.5,ylim[0]),ax.c2p(2.2,ylim[0]),color=INK,stroke_width=1.7)
   ticks=VGroup()
   for r in [.5,1,1.5,2]:
    point=ax.c2p(r,ylim[0]);ticks.add(Line(point+UP*.045,point+DOWN*.045,color=INK),txt(f'{r:g}',21).move_to(point+DOWN*.23))
   xl=math(r'R_0\ [\mathrm{fm}]',25).next_to(bottom,DOWN,buff=.44)
   lore=VMobject(color=ORANGE,stroke_width=3).set_points_as_corners([ax.c2p(r,v) for r,v in zip(radii,los)])
   lod=VGroup(*[Dot(ax.c2p(r,v),radius=.06,color=ORANGE) for r,v in zip(radii,los)])
   nd=VGroup()
   for r,(l,h) in zip(radii,nlos):
    nd.add(Line(ax.c2p(r,l),ax.c2p(r,h),color=TEAL,stroke_width=5),Dot(ax.c2p(r,(l+h)/2),radius=.065,color=TEAL))
   plots.append((VGroup(ax,bottom,ticks,lab,xl),VGroup(lore,lod),nd))
  self.play(*[Create(p[0]) for p in plots],*[Create(p[1]) for p in plots],run_time=1)
  legend=place(txt('LO representatives',22,ORANGE),-2,2.15);legend2=place(txt('NLO cluster means',22,TEAL),2.3,2.15)
  self.play(FadeIn(legend),FadeIn(legend2));self.pause('Source: thesis Table 2.15, newer summary of selected fits. NLO marks span the cluster means at each cutoff. These are not statistical error bars. Cross-section slides retain the original supplied plotting selections.')
  self.play(*[FadeIn(p[2]) for p in plots],run_time=.85)
  self.takeaway('Scattering lengths remain more stable as R₀ changes')
  self.add(place(txt('NLO ranges span cluster means, not confidence intervals',18,MUTED),0,-3.7));self.finish()

class S16Predictions(SeminarSlide):
 number=16;title='Beyond the fitted energy range';section='Results';minutes=1.2
 def construct(self):
  self.frame();ax,decor=self.plot_axes(220,width=10.6,center=(-1,-.2))
  self.play(Create(decor),FadeIn(self.data_dots(ax,220)),run_time=.85)
  def band(order,radii,color):
   arrays=[model(order,r,True) for r in radii]
   # Keep the common original grid, no intermediate cutoff sampling.
   common=sorted(set.intersection(*[set(a[:,0]) for a in arrays])); common=[x for x in common if 0<x<=220]
   lookup=[dict(a) for a in arrays]
   lows=[min(d[x] for d in lookup) for x in common]; highs=[max(d[x] for d in lookup) for x in common]
   pts=[ax.c2p(x,np.clip(y,0,280)) for x,y in zip(common,lows)]+[ax.c2p(x,np.clip(y,0,280)) for x,y in reversed(list(zip(common,highs)))]
   return Polygon(*pts,color=color,stroke_width=1,fill_opacity=.25)
  lo=band('LO',[1.5,2,2.5],ORANGE);nlo=band('NLO',[1.5,2],TEAL)
  limit=DashedLine(ax.c2p(15,0),ax.c2p(15,280),color=ORANGE)
  label=VGroup(txt('LO  /  2 parameters',24,ORANGE,MEDIUM),txt('Fit ≤ 15 MeV',22),txt('R₀: 1.5, 2, 2.5 fm',20)).arrange(DOWN,aligned_edge=LEFT,buff=.25);left(label,4.5,.9)
  self.play(FadeIn(lo),Create(limit),FadeIn(label),run_time=1)
  self.pause('Band is the minimum-to-maximum envelope across the discrete regulators stated. It is not a confidence interval or full EFT truncation uncertainty.')
  limit2=DashedLine(ax.c2p(80,0),ax.c2p(80,280),color=TEAL)
  lab2=VGroup(txt('NLO  /  7 parameters',24,TEAL,MEDIUM),txt('Fit ≤ 80 MeV',22),txt('R₀: 1.5, 2 fm',20)).arrange(DOWN,aligned_edge=LEFT,buff=.25);left(lab2,4.5,-1)
  self.play(lo.animate.set_opacity(.13),FadeIn(nlo),Create(limit2),FadeIn(lab2),run_time=1)
  self.takeaway('A smaller regulator spread, with limits to the contact description')
  self.add(place(txt('NLO R₀ = 1 fm excluded: pathological high-energy extrapolation',18,MUTED),0,-3.7));self.finish()

class S17Families(SeminarSlide):
 number=17;title='The available data leave parameter ambiguity';section='Results';minutes=1
 def construct(self):
  self.frame()
  label=left(txt('Two NLO families at R₀ = 1.5 fm',30,TEAL,MEDIUM),-6.6,1.9)
  self.play(FadeIn(label))
  headers=['Family','χ²ν','C_S','C_T','C₁','C₂','C₃','C₄','C₅']
  rows=[['1','1.021','−6.338','4.175','−1.817','2.791','−1.116','0.198','−17.735'],['2','1.112','−15.551','−4.113','−5.901','−2.507','10.802','−0.543','−0.310']]
  xs=np.linspace(-6.5,6.5,9)
  h=VGroup(*[place(txt(s,23,TEAL,MEDIUM),x,.95) for s,x in zip(headers,xs)])
  rule=Line([-7,.58,0],[7,.58,0],color=GRID)
  self.play(FadeIn(h),Create(rule));self.pause('Thesis Table 2.16. Representative solutions have comparable fit quality, although several coefficients differ substantially. Cs and Ct in fm², subleading coefficients in fm⁴. The scan does not establish uniqueness or statistical posterior probabilities.')
  for i,row in enumerate(rows):
   g=VGroup(*[place(txt(s,23,INK),x,-.03-i*.8) for s,x in zip(row,xs)])
   self.play(FadeIn(g),run_time=.6)
  units=place(txt('C_S, C_T in fm²     C₁ … C₅ in fm⁴',20,MUTED),0,-1.7)
  self.play(FadeIn(units))
  self.takeaway('Bound-state calculations can test the consequences of this ambiguity');self.finish()

class S18Hypertriton(SeminarSlide):
 number=18;title='Application to the hypertriton';section='NSHH';minutes=.8
 def construct(self):
  self.frame()
  p=place(particle('p',ORANGE,.52),-4.9,.8);n=place(particle('n',TEAL,.52),-2.5,.8);l=place(particle('Λ',GOLD,.52),-3.7,-1.65)
  nn=Line(p.get_center(),n.get_center(),color=TEAL,stroke_width=3)
  yn=VGroup(Line(p.get_center(),l.get_center(),color=GOLD,stroke_width=3),Line(n.get_center(),l.get_center(),color=GOLD,stroke_width=3))
  self.play(Create(nn),FadeIn(p),FadeIn(n),run_time=.65)
  self.play(Create(yn),FadeIn(l),run_time=.8)
  nnl=place(txt('NN',25,TEAL),-3.7,1.38);ynl=place(txt('ΛN',25,GOLD),-5.0,-.8)
  self.play(FadeIn(nnl),FadeIn(ynl))
  eq=left(math(r'H=T+V_{NN}+V_{\Lambda p}+V_{\Lambda n}',34),.55,.8)
  target=left(fit(txt('A three-particle bound state\nTwo nucleons and a different-mass hyperon',27),6.7),.55,-.6)
  self.play(FadeIn(eq),FadeIn(target));self.takeaway('The next test of the fitted interaction is a binding energy')
  self.add(place(txt('Two-body Hamiltonian shown. Hypertriton calculations are work in progress.',18,MUTED),0,-3.75));self.finish()

class S19Jacobi(SeminarSlide):
 number=19;title='Jacobi coordinates describe internal motion';section='NSHH';minutes=1.2
 def construct(self):
  self.frame()
  p=place(particle('1',ORANGE,.35),-5.5,.2);n=place(particle('2',TEAL,.35),-2.8,.2);l=place(particle('3',GOLD,.35),-3.15,2)
  self.play(FadeIn(p),FadeIn(n),FadeIn(l),run_time=.7)
  cm=Dot([-4.15,.2,0],color=MUTED,radius=.065)
  x=Arrow(p.get_center(),n.get_center(),buff=.42,color=ORANGE)
  y=Arrow(cm.get_center(),l.get_center(),buff=.18,color=TEAL)
  xl=place(math(r'\boldsymbol x',32,ORANGE),-4.15,-.4)
  yl=place(math(r'\boldsymbol y',32,TEAL),-3.0,.94)
  self.play(GrowArrow(x),FadeIn(xl),run_time=.8)
  self.pause('One Jacobi vector describes the pair separation. Diagram schematic, with two equal-mass particles for the displayed pair midpoint. Actual coordinates include mass-dependent scale factors.')
  self.play(FadeIn(cm),GrowArrow(y),FadeIn(yl),run_time=.8)
  desc=left(txt('Pair separation\nThird particle relative to the pair',29),.6,1.1)
  eq=left(math(r'\rho^2=x^2+y^2',37),.6,-.3)
  cap=left(txt('An overall size coordinate\nplus angles for shape and orientation',26),.6,-1.5)
  self.play(FadeIn(desc),run_time=.7)
  self.play(TransformFromCopy(VGroup(xl,yl),eq),FadeIn(cap),run_time=1.1)
  self.pause('Remove the overall centre-of-mass coordinate first. HH describes the internal angular variables. Keep this explanation conceptual rather than deriving the basis.')
  group=VGroup(p,n,l,cm,x,y,xl,yl)
  self.play(group.animate.scale(.78,about_point=[-4.15,.8,0]),run_time=1.2)
  self.takeaway('The centre-of-mass motion separates from the internal problem');self.finish()

class S20Symmetry(SeminarSlide):
 number=20;title='What “non-symmetrized” means';section='NSHH';minutes=1.4
 def construct(self):
  self.frame()
  head1=left(txt('HH',34,ORANGE,MEDIUM),-6.6,1.9)
  head2=left(txt('NSHH',34,TEAL,MEDIUM),1,1.9)
  hh=left(txt('Build the required symmetry\ninto the basis first',29),-6.6,.8)
  nshh=left(txt('Use a basis without\npreassigned permutation symmetry',29),1,.8)
  self.play(FadeIn(head1),FadeIn(hh),run_time=.7);self.pause('Conventional HH builds appropriate exchange symmetry before solving. NSHH avoids that preparatory basis construction. Source: Nannini and Marcucci (2018), doi:10.3389/fphy.2018.00122.')
  self.play(FadeIn(head2),FadeIn(nshh),run_time=.7)
  sym=place(math(r'P_{12}\psi=-\psi',43,TEAL),0,-.65)
  label=place(txt('Identical fermions still require an antisymmetric physical state',27),0,-1.6)
  self.play(Write(sym),FadeIn(label),run_time=1.1)
  self.focus_on(sym)
  self.pause('The Hamiltonian has symmetry sectors when it commutes with the corresponding particle exchange. Identify the physical sector of its eigenstates. There is no identical-particle antisymmetry requirement for exchanging Λ with a nucleon. The nucleon treatment depends on the species/isospin formulation.')
  lower=place(txt('Flexible basis construction and different masses\nA larger basis can increase the computational cost',25,MUTED),0,-2.55)
  self.play(FadeIn(lower));self.finish()

class S21Benchmark(SeminarSlide):
 number=21;title='Validation with the triton';section='NSHH';minutes=1.1
 def construct(self):
  self.frame()
  label=left(txt('Ground-state energies at LO',29,TEAL,MEDIUM),-6.5,1.93)
  self.play(FadeIn(label))
  headers=['Model','NSHH [MeV]','HH [MeV]','|difference| [keV]']
  xs=[-5.3,-2.1,1.25,5.1]
  self.play(FadeIn(VGroup(*[place(txt(s,26,TEAL,MEDIUM),x,1.13) for s,x in zip(headers,xs)])))
  data=[('a','−10.706','−10.705','1'),('b','−8.463','−8.463','0'),('c','−7.066','−7.066','0'),('d','−6.137','−6.136','1'),('o','−9.696','−9.696','0')]
  for i,row in enumerate(data):
   vals=VGroup(*[place(txt(s,28,INK),x,.38-i*.58) for s,x in zip(row,xs)])
   self.play(FadeIn(vals),run_time=.35)
  self.pause('Values transcribed from the supplied seminar. Absolute differences computed from the displayed rounded energies. This benchmarks the numerical implementation, not agreement with experimental triton energy. Hypertriton result is not yet claimed.')
  self.takeaway('Agreement within 1 keV at the displayed precision')
  self.add(place(txt('Next: complete NLO validation, then combine NN and ΛN interactions',20,MUTED),0,-3.75));self.finish()

class S22Outlook(SeminarSlide):
 number=22;title='Conclusions and outlook';section='Outlook';minutes=1.5
 def construct(self):
  self.frame()
  done=left(txt('Results so far',30,ACCENT,MEDIUM),-6.6,1.92)
  lines=VGroup(txt('A local ΛN contact interaction fitted up to NLO',30,INK,MEDIUM),txt('More stable low-energy observables across regulators',30,INK,MEDIUM),txt('Several data-compatible families of coefficients',30,INK,MEDIUM)).arrange(DOWN,aligned_edge=LEFT,buff=.38);left(lines,-6.6,.48)
  self.play(FadeIn(done),LaggedStart(*[FadeIn(t) for t in lines],lag_ratio=.2),run_time=1.1)
  self.pause('The potential derivation predates this fitting project. This project improves the determination and analysis of the coefficients. Keep the distinction between fitted observables and extrapolations.')
  nextt=left(txt('Next steps',30,ACCENT,MEDIUM),-6.6,-1.18)
  nexts=left(txt('Hypertriton binding energy with NSHH\nLocal chiral extension with explicit meson exchange',29,INK),-6.6,-2.08)
  self.play(FadeIn(nextt),FadeIn(nexts),run_time=.8)
  q=left(txt('Which additional observables best constrain the force?',27,ACCENT,MEDIUM),-6.6,-3.3)
  box=SurroundingRectangle(q,buff=.14,corner_radius=.08,color=ACCENT,stroke_width=1.3,fill_color=ACCENT,fill_opacity=.035)
  self.play(Create(box),FadeIn(q));self.finish()

SCENES=[S01Aim,S02Applications,S03Levels,S04EOS,S05Features,S06EFT,S07Potential,S08Regulator,S09Scattering,S10Observables,S11ChiSquare,S12FitSetup,S13LO,S14NLO,S15Cutoff,S16Predictions,S17Families,S18Hypertriton,S19Jacobi,S20Symmetry,S21Benchmark,S22Outlook]
