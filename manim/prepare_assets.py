"""Copy source evidence read-only; never import or run the original analysis code."""
from pathlib import Path
from PIL import Image
import csv,json,shutil,hashlib
ROOT=Path(__file__).resolve().parent
SOURCE=Path('/Users/margherita/Desktop/UNIPI/TESI/CODICE/CODICI_PHASE-SHIFTS/PARALLEL-PETSC/Analisi/lambda_n_cross_section_modern')
assets=ROOT/'assets'; assets.mkdir(exist_ok=True)
manifest={}
for p in sorted((SOURCE/'results').glob('*.csv')):
 if p.name.startswith(('lo_r','nlo_r','cross_section_uncertainty_')):
  shutil.copyfile(p,assets/p.name)
  manifest[p.name]={'source':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
  meta=p.with_suffix(p.suffix+'.meta.json')
  if meta.exists(): shutil.copyfile(meta,assets/meta.name)
p=SOURCE/'data/experimental_cross_section.dat'
shutil.copyfile(p,assets/p.name)
manifest[p.name]={'source':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
# Original author-provided EFT drawings, cropped without redrawing.
im=Image.open(next((ROOT/'work').glob('eft-*.png')))
w,h=im.size
for name,box in {'qcd':(.068,.524,.275,.85),'chiral':(.386,.535,.62,.842),'contact':(.755,.56,.922,.822)}.items():
 im.crop(tuple(round(v*(w if i%2==0 else h)) for i,v in enumerate(box))).save(assets/('eft_'+name+'.png'))
manifest['eft_drawings']={'source':'seminario_passaggio_anno.pdf, PDF page 10','treatment':'crop only'}
(assets/'provenance.json').write_text(json.dumps(manifest,indent=2))
print(f'Copied {len(manifest)-1} evidence files. Original code and results unchanged.')
