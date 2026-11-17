"""Independent accepted triangle clearance and actual FF/coupled-state audit."""
import argparse,csv,json,os,shutil,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
def gaps(p,center,radius):
    a,b,c=p[:,0],p[:,1],p[:,2];ab=b-a;ac=c-a;n=np.cross(ab,ac);n2=np.sum(n*n,axis=1)
    if np.any(n2<=0):raise ValueError('degenerate actual triangle;no epsilon denominator')
    t=np.sum((center-a)*n,axis=1)/n2;projection=center-t[:,None]*n;ap=projection-a;aa=np.sum(ab*ab,axis=1);bb=np.sum(ab*ac,axis=1);cc=np.sum(ac*ac,axis=1);den=aa*cc-bb*bb
    if np.any(den<=0):raise ValueError('degenerate actual barycentric basis')
    u=(cc*np.sum(ab*ap,axis=1)-bb*np.sum(ac*ap,axis=1))/den;v=(aa*np.sum(ac*ap,axis=1)-bb*np.sum(ab*ap,axis=1))/den;distance=np.where((u>=0)&(v>=0)&(u+v<=1),t*t*n2,np.inf)
    for x,y in ((a,b),(a,c),(b,c)):
        edge=y-x;length=np.sum(edge*edge,axis=1)
        if np.any(length<=0):raise ValueError('collapsed actual edge')
        fraction=np.clip(np.sum((center-x)*edge,axis=1)/length,0,1);point=x+fraction[:,None]*edge;distance=np.minimum(distance,np.sum((point-center)**2,axis=1))
    return np.sqrt(distance)-radius
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();source=ROOT/'results'/('autonomous_film_'+a.case);meta=json.loads((source/'identity.json').read_text());summary=json.loads((source/'summary.json').read_text())
    if summary['status']!='PASS':raise ValueError('completed actual coupled execution required')
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');scene=ET.parse(source/'scene.scn');topology=scene.find('.//TriangleSetTopologyContainer');rest=np.fromstring(topology.get('position'),sep=' ').reshape(-1,3);tri=np.fromstring(topology.get('triangles'),sep=' ',dtype=int).reshape(-1,3)
    if not any(scene.find(name) is not None for name in ('CoupledSphereODE','AdaptiveCoupledSphereODE','FrozenCoupledGridODE','CoupledRestartODE','IsolatedReintegratedSphereODE','SingleRowRadauSphereODE','CoupledEventLobattoODE')) or scene.find('FreeMotionAnimationLoop') is not None or scene.find('CollisionPipeline') is not None:raise ValueError('not isolated custom sole-owner scene')
    state_file=meta.get('state_file','coupled.states.csv');states=list(csv.DictReader((source/state_file).open()));film=list(csv.DictReader((source/'film.csv').open()));events=list(csv.DictReader((source/'coupled.events.csv').open()));rows=list(csv.DictReader((source/'coupled.rows.csv').open()));errors=dict(world=0.,gap=0.,time=0.,shell=0.,attachment=0.,K_film=0.,T=0.);minimum=float('inf');seen=set();graph=[]
    for s,f in zip(states,film):
        world=rest+np.fromstring(s['local_displacement'],sep=' ').reshape(-1,3);actual=np.fromstring(f['x'],sep=' ').reshape(-1,3);center=np.fromstring(s['body_center'],sep=' ');g=float(np.min(gaps(world[tri],center,meta['buffer_radius'])));minimum=min(minimum,g);errors['world']=max(errors['world'],float(np.max(np.abs(world-actual))));errors['gap']=max(errors['gap'],abs(g-float(s['minimum_gap'])));errors['time']=max(errors['time'],abs(float(s['time'])-float(f['time'])));errors['T']=max(errors['T'],abs(float(s['end_tension'])-float(f['T_per_rail'])))
        for name,k in (('shell','U_shell'),('attachment','U_attachment'),('K_film','K')):errors[name]=max(errors[name],abs(float(s['K_film' if name=='K_film' else k])-float(f[k])))
        graph.append([float(s['time']),g,*center,float(s['U_attachment']),float(s['K_film']),float(s['K_linear'])])
    for row in rows:
        key=(row['step'],row['stage'],row['row'])
        if key in seen:raise ValueError('duplicate row ownership')
        seen.add(key)
        if float(row['impulse'])<0 or abs(np.linalg.norm([float(row[k]) for k in ('nx','ny','nz')])-1)>1e-12:raise ValueError('invalid actual row multiplier/normal')
    event_checks={k:max([abs(float(r[k])) for r in events]) if events else None for k in ('momentum_residual','linear_balance','angular_balance')}
    valid=len(states)==len(film)==meta['steps'] and minimum>=-1e-10 and all(v<=1e-11 for v in errors.values()) and all(v is None or v<=1e-12 for v in event_checks.values())
    os.environ.setdefault('MPLCONFIGDIR',str(out/'matplotlib_cache'));import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    fig,axes=plt.subplots(1,3,figsize=(14,4));graph=np.array(graph);axes[0].plot(graph[:,0],graph[:,1]);axes[0].set_title('Whole accepted triangle gap [mm]');axes[1].plot(graph[:,0],graph[:,4]-graph[0,4]);axes[1].set_title('Actual free body z motion [mm]');axes[2].plot(graph[:,0],graph[:,5],label='attachment');axes[2].plot(graph[:,0],graph[:,6],label='film kinetic');axes[2].plot(graph[:,0],graph[:,7],label='body translational');axes[2].legend();axes[2].set_title('Partial energy terms [F mm]')
    for ax in axes:ax.set_xlabel('physical time [s]');ax.grid()
    fig.suptitle('Actual custom coupled SOFA / NOT qualified grasp or full energy');fig.tight_layout();fig.savefig(out/'observables.png',dpi=160);plt.close(fig)
    selected=set((0,len(states)//2,len(states)-1));frames=[]
    if events:
        entry=min(float(e['time']) for e in events);times=np.array([float(s['time']) for s in states]);before=np.where(times<entry)[0];after=np.where(times>=entry)[0]
        if len(before):selected.add(int(before[-1]))
        if len(after):selected.add(int(after[0]))
    selected=sorted(selected)
    for i in selected:
        s=states[i];world=rest+np.fromstring(s['local_displacement'],sep=' ').reshape(-1,3);center=np.fromstring(s['body_center'],sep=' ');name='state_'+str(i);(out/(name+'.obj')).write_text('\n'.join(['# Actual custom coupled SOFA;scale1;NOT qualified grasp']+['v '+' '.join(format(v,'.17g') for v in x) for x in world]+['f '+' '.join(str(int(j)+1) for j in x) for x in tri])+'\n');fig,ax=plt.subplots(figsize=(8,4));ax.add_collection(PolyCollection(world[tri][:,:,[0,2]],facecolor='#83b6c7',edgecolor='#345',linewidth=.25,alpha=.5));ax.add_patch(plt.Circle((center[0],center[2]),meta['body_radius'],color='#bbb',alpha=.4));ax.autoscale();ax.set_aspect('equal');ax.set_xlabel('x [mm]');ax.set_ylabel('z [mm]');ax.set_title('Actual coupled SOFA t='+s['time']+'s / scale1 / NOT qualified grasp');fig.tight_layout();fig.savefig(out/(name+'.png'),dpi=160);plt.close(fig);frames.append(dict(time=float(s['time']),center=center.tolist(),obj=name+'.obj'))
    write_json(out/'summary.json',dict(status='PASS' if valid else 'FAIL',scope='independent clearance/actual FF/owned row/instantaneous momentum audit only;NOT fulltime/energy/grasp',case=a.case,errors=errors,minimum_independent_gap=minimum,event_checks=event_checks,owned_rows=len(rows),frames=frames,source_hashes={f:sha(source/f) for f in ('identity.json','scene.scn','summary.json',state_file,'coupled.events.csv','coupled.rows.csv','film.csv')},energy_not_measured=['synchronized damping work','full tendon quadrature consistency','external work','whole-step angular momentum balance','integration energy residual']))
    print(json.dumps(dict(status='PASS' if valid else 'FAIL',errors=errors,minimum_gap=minimum,event_checks=event_checks)))
if __name__=='__main__':main()
