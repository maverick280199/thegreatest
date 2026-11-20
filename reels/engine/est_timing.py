"""est_timing.py <reelDir>: preview-only timing from script.json (no audio yet): ~13 chars/s, synthetic mouth track, silent voice.mp3"""
import json, sys, os, math, subprocess
d = sys.argv[1]; sc = json.load(open(os.path.join(d,'script.json')))['sentences']
t = 0.3; S = []
for s in sc:
    dur = max(0.8, len(s['text'])/13.0); S.append({'text':s['text'],'scene':s['scene'],'start':round(t,2),'end':round(t+dur,2)}); t += dur + 0.4
scenes=[]
for s in S:
    if not scenes or scenes[-1]['i']!=s['scene']: scenes.append({'i':s['scene'],'start':0 if not scenes else s['start']-0.12})
total = round(t+1.0,2)
json.dump({'duration':total,'sentences':S,'scenes':scenes},open(os.path.join(d,'timing.json'),'w'),indent=1)
rms=[]
for f in range(int(total*30)):
    x=f/30; speaking=any(s['start']<=x<=s['end'] for s in S)
    rms.append(round(abs(math.sin(x*11))*0.8 if speaking else 0,3))
json.dump({'fps':30,'rms':rms},open(os.path.join(d,'amp.json'),'w'))
subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','anullsrc=r=44100:cl=mono','-t',str(total),os.path.join(d,'voice.mp3')],check=True)
print('preview duration',total)
