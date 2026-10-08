from pathlib import Path
import json,av
ROOT=Path(__file__).resolve().parent
names=['S03Levels','S07Potential','S08Regulator','S09Scattering','S13LO','S19Jacobi','S20Symmetry']
files=[]
for name in names:
 files += [ROOT/s['file'] for s in json.loads((ROOT/'slides'/f'{name}.json').read_text())['slides']]
output=ROOT/'outputs/animation_preview.mp4'
with av.open(str(files[0])) as first:
 with av.open(str(output),'w',options={'movflags':'+faststart'}) as out:
  stream=out.add_stream_from_template(first.streams.video[0]);offset=0
  for file in files:
   with av.open(str(file)) as inp:
    video=inp.streams.video[0];assert video.time_base==first.streams.video[0].time_base
    duration=video.duration
    for packet in inp.demux(video):
     if packet.dts is None:continue
     packet.pts+=offset;packet.dts+=offset;packet.stream=stream;out.mux(packet)
    offset+=duration
with av.open(str(output)) as check:
 count=sum(1 for _ in check.decode(video=0))
 print(f'Preview decoded successfully: {count} frames, {count/30:.1f} seconds.')
