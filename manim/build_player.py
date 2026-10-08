"""Package Manim Slides checkpoints into a portable, offline seminar player."""
from pathlib import Path
import json, shutil, zipfile
from seminar import SCENES
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'outputs';OUT.mkdir(exist_ok=True)
(OUT/'media').mkdir(exist_ok=True);(OUT/'posters').mkdir(exist_ok=True)
deck=[]
for cls in SCENES:
 data=json.loads((ROOT/'slides'/f'{cls.__name__}.json').read_text())
 parts=[]
 for i,item in enumerate(data['slides']):
  name=f'{cls.number:02d}-{i+1:02d}.mp4';shutil.copyfile(ROOT/item['file'],OUT/'media'/name)
  parts.append('media/'+name)
 stills=sorted((OUT/'pngs').glob(f'{cls.__name__}-[0-9][0-9].png'))
 if not stills: raise FileNotFoundError(f'No PNGs for {cls.__name__}; run python deck.py pngs')
 poster=f'posters/{cls.number:02d}.png';shutil.copyfile(stills[-1],OUT/poster)
 notes='\n\n'.join(dict.fromkeys(x['notes'] for x in data['slides'] if x['notes']))
 deck.append(dict(title=cls.title,section=cls.section,minutes=cls.minutes,clips=parts,poster=poster,notes=notes))
html=r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Local hyperonic interactions · Margherita Sagina</title><style>
:root{color-scheme:dark;--bg:#322c21;--cream:#fffcf5;--teal:#3c7f72;--gold:#f8b037}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--cream);font-family:system-ui,-apple-system,sans-serif;overflow:hidden}button{font:inherit;cursor:pointer;border:1px solid #746c5c;border-radius:7px;background:#433c30;color:var(--cream);padding:9px 14px}button:hover,button:focus-visible{background:#554c3d;outline:2px solid var(--teal)}#stage{position:fixed;inset:0;display:flex;align-items:center;justify-content:center}video{width:100%;height:100%;object-fit:contain}#landing{position:absolute;inset:0;display:grid;align-items:end;justify-items:center;padding-bottom:6vh;background:linear-gradient(transparent 70%,#322c21c9)}#landing button{background:var(--cream);color:var(--bg);font-weight:600;padding:14px 24px}#controls{position:fixed;bottom:0;left:0;right:0;display:flex;gap:9px;align-items:center;padding:12px 18px;background:#322c21f5;border-top:1px solid #746c5c;transition:opacity .25s;z-index:5}body.quiet #controls{opacity:0;pointer-events:none}#caption{flex:1;font-size:13px;line-height:1.6}#caption span{color:#dcd6c7}#progress{height:3px;background:var(--teal);position:absolute;top:-3px;left:0;transition:width .3s}#overview,#notes,#help{position:fixed;inset:5vh 5vw;background:#322c21fa;border:1px solid #746c5c;border-radius:12px;padding:25px;z-index:10;overflow:auto}dialog[open]{display:block}dialog{color:var(--cream)}.top{display:flex;align-items:center;justify-content:space-between;margin-bottom:18px}.top h2{margin:0;font-size:23px}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:18px}.tile{padding:0;text-align:left;overflow:hidden}.tile img{display:block;width:100%;aspect-ratio:16/9;object-fit:contain}.tile strong{display:block;padding:12px;font-size:14px}.tile small{display:block;padding:0 12px 12px;color:#dcd6c7}#notesText{white-space:pre-wrap;line-height:1.7;max-width:900px;font-size:17px}kbd{background:#554c3d;padding:3px 7px;border-radius:4px}#help p{line-height:1.9}#toast{position:fixed;top:20px;left:50%;transform:translateX(-50%);padding:10px 16px;background:#322c21e0;border-radius:8px;display:none;z-index:20}@media(max-width:700px){#controls{gap:5px;padding:8px}#caption{display:none}button{padding:7px 9px}}
</style></head><body><main id="stage"><video id="video" playsinline preload="auto" aria-label="Animated seminar slide"></video><div id="landing"><button id="start">Start presentation →</button></div></main><nav id="controls" aria-label="Presentation controls"><div id="progress"></div><button id="prev" title="Previous build (Left)">←</button><button id="next" title="Next build (Space / Right)">Next →</button><button id="replay" title="Replay (R)">Replay</button><div id="caption"></div><button id="overviewButton">Slides</button><button id="notesButton">Notes</button><button id="helpButton">?</button><button id="fullscreen">Full screen</button></nav><dialog id="overview"><div class="top"><h2>Seminar · 22 slides · about 25 minutes</h2><button data-close>Close</button></div><div class="grid" id="grid"></div></dialog><dialog id="notes"><div class="top"><h2>Speaker notes</h2><button data-close>Close</button></div><div id="notesText"></div></dialog><dialog id="help"><div class="top"><h2>Present at your own pace</h2><button data-close>Close</button></div><p>Each animation stops at a checkpoint. Explain the current picture, then advance.</p><p><kbd>Space</kbd> or <kbd>→</kbd> next build · <kbd>←</kbd> previous build<br><kbd>Shift</kbd> + arrow: next / previous slide<br><kbd>R</kbd> replay current build · <kbd>P</kbd> pause / resume<br><kbd>O</kbd> slide overview · <kbd>N</kbd> speaker notes · <kbd>F</kbd> full screen<br><kbd>Esc</kbd> close a panel</p><p>The suggested speaking times total 24.3 minutes; the animations themselves are short. No internet connection is needed. Keep this HTML file together with its media and posters folders.</p></dialog><div id="toast" role="status"></div><script>
const DECK=__DECK__;
let chapter=0,beat=0,started=false,timer;const $=id=>document.getElementById(id),v=$('video');
function notify(message){$('toast').textContent=message;$('toast').style.display='block';setTimeout(()=>$('toast').style.display='none',1800)}
function wake(){document.body.classList.remove('quiet');clearTimeout(timer);if(started)timer=setTimeout(()=>{if(!document.querySelector('dialog[open]'))document.body.classList.add('quiet')},3000)}
function refresh(){const d=DECK[chapter];$('caption').innerHTML='';let title=document.createElement('div');title.textContent=d.title;let detail=document.createElement('span');detail.textContent=`${chapter+1} / ${DECK.length} · Build ${beat+1} / ${d.clips.length} · ${d.section} · Suggested ${d.minutes} min`;$('caption').append(title,detail);$('progress').style.width=((chapter+(beat+1)/d.clips.length)/DECK.length*100)+'%';$('notesText').textContent=`${d.title}\nSuggested speaking time: ${d.minutes} min\n\n${d.notes||'Introduce this part of the research storyline.'}`;document.title=`${chapter+1}. ${d.title} · Margherita Sagina`}
function load(play=true,end=false){v.pause();v.poster=DECK[chapter].poster;v.src=DECK[chapter].clips[beat];v.onloadedmetadata=()=>{if(end)v.currentTime=Math.max(0,v.duration-.04);else if(play)v.play().catch(()=>notify('Click Next to play the animation'));};refresh();wake()}
function advance(){if(!started){start();return}if(beat+1<DECK[chapter].clips.length)beat++;else if(chapter+1<DECK.length){chapter++;beat=0}else{notify('End of presentation');return}load()}
function previous(){if(beat>0)beat--;else if(chapter>0){chapter--;beat=DECK[chapter].clips.length-1}load(false,true)}
function jump(i){chapter=Math.max(0,Math.min(DECK.length-1,i));beat=0;started=true;$('landing').style.display='none';load()}
function start(){started=true;$('landing').style.display='none';load()}
function full(){if(document.fullscreenElement)document.exitFullscreen();else document.documentElement.requestFullscreen().catch(()=>notify('Use your browser’s full-screen command'))}
function panel(id){const dialog=$(id);dialog.open?dialog.close():dialog.showModal();wake()}
$('start').onclick=start;$('next').onclick=advance;$('prev').onclick=previous;$('replay').onclick=()=>load();$('fullscreen').onclick=full;$('overviewButton').onclick=()=>panel('overview');$('notesButton').onclick=()=>panel('notes');$('helpButton').onclick=()=>panel('help');
document.querySelectorAll('[data-close]').forEach(b=>b.onclick=()=>b.closest('dialog').close());
DECK.forEach((d,i)=>{const b=document.createElement('button');b.className='tile';const im=document.createElement('img');im.src=d.poster;im.alt=d.title;const t=document.createElement('strong');t.textContent=`${String(i+1).padStart(2,'0')} · ${d.title}`;const s=document.createElement('small');s.textContent=`${d.section} · ${d.minutes} min`;b.append(im,t,s);b.onclick=()=>{$('overview').close();jump(i)};$('grid').append(b)});
v.addEventListener('click',advance);document.addEventListener('mousemove',wake);document.addEventListener('keydown',e=>{if(document.querySelector('dialog[open]')){if(e.key==='Escape')document.querySelector('dialog[open]').close();return}const k=e.key.toLowerCase();if([' ','arrowright','arrowleft'].includes(k))e.preventDefault();if(k===' '||k==='arrowright'){e.shiftKey?jump(chapter+1):advance()}else if(k==='arrowleft'){e.shiftKey?jump(chapter-1):previous()}else if(k==='r')load();else if(k==='p')v.paused?v.play():v.pause();else if(k==='f')full();else if(k==='o')panel('overview');else if(k==='n')panel('notes')});
v.poster=DECK[0].poster;refresh();
</script></body></html>'''
light_css='''
:root{color-scheme:light;--bg:#fffcf5;--cream:#322c21;--teal:#3c7f72;--gold:#f8b037}
body{background:#fffcf5;color:#322c21}
button{background:#f4f0e8;color:#322c21;border-color:#c7c4ba}
button:hover,button:focus-visible{background:#eae5da}
#landing{background:linear-gradient(transparent 70%,#fffcf5dc)}
#landing button{background:#322c21;color:#fffcf5}
#controls{background:#fffcf5f5;border-top-color:#c7c4ba}
#caption span,.tile small{color:#626c6b}
#overview,#notes,#help{background:#fffcf5fa;border-color:#c7c4ba}
kbd{background:#eae5da}
#toast{background:#fffcf5ed;border:1px solid #c7c4ba}
'''
(OUT/'seminar.html').write_text(
 html.replace('__DECK__',json.dumps(deck,ensure_ascii=False))
     .replace('24.3 minutes',f'{sum(d["minutes"] for d in deck):g} minutes')
     .replace('</style>',light_css+'</style>'))
(OUT/'deck.json').write_text(json.dumps(deck,ensure_ascii=False,indent=2))
(OUT/'README.md').write_text('''# Animated seminar

Open **seminar.html** in a browser and click **Start presentation**. The deck runs offline. Keep the media and posters folders next to the HTML file.

- Space / Right: next animation checkpoint.
- Left: previous checkpoint, held at its final frame.
- Shift + arrow: next / previous slide.
- R: replay. P: pause / resume. F: full screen.
- O: slide overview. N: scientific source and speaker notes.

22 slides, suggested speaking times totalling 24.1 minutes. These times include the spoken explanation; animations pause until you advance.

The data plots use the supplied calculations and reports. Provenance is recorded in ../assets/provenance.json. Qualitative diagrams are identified in the speaker notes. The HH/NSHH table benchmarks the triton; the hypertriton is an outlook application.

The layout and diagrams are authored in Manim. Fonts are bundled in ../assets/fonts and registered locally at render time.

Editable Manim source is ../seminar.py. Use ../deck.py to render, export PNGs and present the deck.
''')
with zipfile.ZipFile(OUT/'animated_seminar.zip','w',compression=zipfile.ZIP_DEFLATED) as z:
 for p in [OUT/'seminar.html',OUT/'README.md',*sorted((OUT/'media').glob('*.mp4')),*sorted((OUT/'posters').glob('*.png'))]:z.write(p,p.relative_to(OUT))
print(f'Packaged {len(deck)} slides, {sum(len(d["clips"]) for d in deck)} animation checkpoints.')
