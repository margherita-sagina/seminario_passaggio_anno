from manim import *
from manim_slides import Slide
class Smoke(Slide):
 def construct(self):
  t=MathTex(r'V_{\Lambda N}=[C_S+C_T\,\boldsymbol\sigma_\Lambda\cdot\boldsymbol\sigma_N]F(r)',color='#24302E')
  self.play(FadeIn(t),run_time=.3)
  self.wait(.1)
  self.next_slide(notes='Test')
  self.play(t.animate.shift(UP),run_time=.3)
  self.wait(.1)
