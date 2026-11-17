"""Render saved actual owner states, with no deformation magnification."""
import argparse,csv,json,os,shutil,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args()
    source=ROOT/'results'/('autonomous_film_'+a.case);summary=json.loads((source/'summary.json').read_text())
    if summary['status']!='PASS':raise ValueError('complete actual execution required')
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py')
    scene=ET.parse(source/'scene.scn');topology=scene.find('.//TriangleSetTopologyContainer');rest=np.asarray(list(map(float,topology.get('position').split()))).reshape(-1,3);triangles=np.asarray(list(map(int,topology.get('triangles').split()))).reshape(-1,3)
    owner=scene.find('FilmWholeSurfaceEventOwner');center=np.asarray(list(map(float,owner.get('center').split())));buffer_radius=float(owner.get('radius'))
    actual_radius=float(scene.find('.//SphereCollisionModel').get('radius'))
    states=list(csv.DictReader((source/'event.csv.states.csv').open()));events=list(csv.DictReader((source/'event.csv.surface.csv').open()))
    time=float(events[0]['event_time']) if events else float(states[-1]['time'])
    before=[s for s in states if float(s['time'])<time];after=[s for s in states if float(s['time'])>=time]
    selected=[('pre_saved',before[-1] if before else states[0]),('post_saved',after[0] if after else states[-1]),('end',states[-1])]
    os.environ.setdefault('MPLCONFIGDIR',str(out/'matplotlib_cache'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    fig,axes=plt.subplots(len(selected),2,figsize=(11,9));frames=[]
    for k,(name,state) in enumerate(selected):
        world=rest+np.asarray(list(map(float,state['local_displacement'].split()))).reshape(-1,3)
        obj=out/(name+'.obj');lines=['# Actual saved SOFA state; displacement magnification1;not qualified grasp']
        lines.extend('v '+' '.join(format(v,'.17g') for v in point) for point in world)
        lines.extend('f '+' '.join(str(int(i)+1) for i in tri) for tri in triangles);obj.write_text('\n'.join(lines)+'\n')
        for j,(d,e) in enumerate(((0,2),(1,2))):
            ax=axes[k,j];ax.add_collection(PolyCollection(world[triangles][:,:,[d,e]],facecolor='#82b4ca',edgecolor='#345',alpha=.45,linewidth=.25))
            # Orthographic sphere silhouette, not a computed contact patch.
            ax.add_patch(plt.Circle((center[d],center[e]),actual_radius,color='#bbb',alpha=.4));ax.add_patch(plt.Circle((center[d],center[e]),buffer_radius,fill=False,linestyle='--',color='#555'))
            ax.autoscale();ax.set_aspect('equal');ax.grid();ax.set_xlabel('xyz'[d]+' [mm]');ax.set_ylabel('xyz'[e]+' [mm]');ax.set_title(name+' t='+format(float(state['time']),'.8g')+'s')
        frames.append(dict(name=name,time=float(state['time']),obj_sha256=sha(obj)))
    fig.suptitle('Actual SOFA fixed-sphere coupon / scale1 / NOT qualified grasp\n'+a.case);fig.tight_layout();fig.savefig(out/'actual_states.png',dpi=160);plt.close(fig)
    write_json(out/'summary.json',dict(status='PASS',scope='saved-state visualization only;NOT contact-area/pressure/grasp certification',source_case=a.case,source_identity=json.loads((source/'identity.json').read_text()),source_hashes={f:sha(source/f) for f in ('scene.scn','event.csv.states.csv','event.csv.surface.csv','summary.json')},event_time=time,frames=frames,displacement_magnification=1,sphere_note='fixed R8 surface,buffer8.01;orthographic silhouettes,not contact patches'))
    print(json.dumps(dict(status='PASS',path=str(out))))
if __name__=='__main__':main()
