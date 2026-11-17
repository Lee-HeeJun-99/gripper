"""Audit actual Native mixed-state journals;never certify custom event/grasp law."""
import argparse,csv,json,os,shutil,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args()
    source=ROOT/'results'/('autonomous_film_'+a.case);summary=json.loads((source/'summary.json').read_text());identity=json.loads((source/'identity.json').read_text())
    if summary['status'] not in ('EXPERIMENTAL','FAIL'):raise ValueError('unknown Native result')
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');audits={};frames=[];hashes={}
    os.environ.setdefault('MPLCONFIGDIR',str(out/'matplotlib_cache'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    fig,axes=plt.subplots(1,3,figsize=(14,4))
    for key,record in summary['cases'].items():
        case=source/key
        if record.get('execution_status')!='PASS':audits[key]=dict(status='NOT ASSESSED',reason='incomplete actual process');continue
        rows=list(csv.DictReader((case/'body.csv').open()));time=np.array([float(r['time']) for r in rows]);dt=np.array([float(r['dt']) for r in rows]);steps=int(key)
        state=np.array([[float(r[k]) for k in ('x','y','z','vx','vy','vz','wx','wy','wz')] for r in rows]);impulse=np.array([[float(r[k]) for k in ('native_ix','native_iy','native_iz')] for r in rows]);valid=len(rows)==steps and np.all(np.isfinite(state))
        metrics={k:max(float(r[k]) for r in rows) for k in ('BE_position_residual','mapped_center_error','impulse_balance_residual','contact_action_reaction_residual','contact_moment_begin_residual','contact_moment_end_residual')}
        # Sphere center mapping has zero contact moment. Isotropic free spin
        # must follow the independently evaluated BE Rayleigh recurrence.
        omega=np.array(identity['initial_body_omega'],dtype=float);spin_error=0.
        for h,r in zip(dt,rows):
            omega=omega/(1+identity['rayleigh_mass']*h)
            spin_error=max(spin_error,float(np.linalg.norm(omega-[float(r[k]) for k in ('wx','wy','wz')])))
        valid=valid and metrics['BE_position_residual']<=1e-10 and metrics['mapped_center_error']<=1e-12 and metrics['impulse_balance_residual']<=1e-12 and metrics['contact_action_reaction_residual']<=1e-12 and metrics['contact_moment_begin_residual']<=1e-12 and spin_error<=1e-12
        audits[key]=dict(status='PASS' if valid else 'FAIL',scope='actual Native impulse/BE update identities only',metrics=metrics,independent_BE_spin_error=spin_error,minimum_buffer_gap=min(float(r['minimum_buffer_gap']) for r in rows),contact_frames=int(np.count_nonzero(np.linalg.norm(impulse,axis=1)>0)))
        axes[0].plot(time,state[:,2]-state[0,2],label=key+' steps');axes[1].plot(time,np.linalg.norm(impulse,axis=1),label=key);axes[2].plot(time,[float(r['minimum_buffer_gap']) for r in rows],label=key)
        for name in ('body.csv','film.csv','displacement.csv','scene.scn','process/result.json'):hashes[str((case/name).relative_to(source))]=sha(case/name)
        if identity.get('c2_closing'):
            film=list(csv.DictReader((case/'film.csv').open()));displacements=list(csv.DictReader((case/'displacement.csv').open()));scene=ET.parse(case/'scene.scn');topology=scene.find('.//TriangleSetTopologyContainer');rest=np.array(list(map(float,topology.get('position').split()))).reshape(-1,3);tri=np.array(list(map(int,topology.get('triangles').split()))).reshape(-1,3)
            if len(film)!=steps or len(displacements)!=steps:raise ValueError('incomplete actual film state')
            for index in sorted(set((0,steps//2,steps-1))):
                t=float(displacements[index]['time'])
                if abs(t-time[index])>1e-12 or abs(float(film[index]['time'])-t)>1e-12:raise ValueError('misaligned actual states')
                world=rest+np.fromstring(displacements[index]['u'],sep=' ').reshape(-1,3)
                # FF x is the actual world geometry;do not infer mapping blindly.
                actual=np.fromstring(film[index]['x'],sep=' ').reshape(-1,3)
                if not np.allclose(world,actual[:len(rest)],rtol=0,atol=1e-12):raise ValueError('actual film world mapping differs from rest+u')
                name=key+'_'+str(index);lines=['# Actual SOFA Native state;scale1;NOT qualified grasp']+['v '+' '.join(format(v,'.17g') for v in point) for point in world]+['f '+' '.join(str(int(i)+1) for i in f) for f in tri];(out/(name+'.obj')).write_text('\n'.join(lines)+'\n')
                view,ax=plt.subplots(figsize=(8,4));ax.add_collection(PolyCollection(world[tri][:,:,[0,2]],facecolor='#84b9c7',edgecolor='#345',linewidth=.2,alpha=.5));ax.add_patch(plt.Circle((state[index,0],state[index,2]),identity['object_radius'],color='#aaa',alpha=.4));ax.autoscale();ax.set_aspect('equal');ax.set_xlabel('x [mm]');ax.set_ylabel('z [mm]');ax.set_title('Actual Native SOFA t='+str(t)+'s / scale1 / NOT qualified grasp');view.tight_layout();view.savefig(out/(name+'.png'),dpi=160);plt.close(view);frames.append(dict(time=t,body_center=state[index,:3].tolist(),obj=name+'.obj',png=name+'.png'))
    for ax,title in zip(axes,('Actual body z displacement [mm]','Native normal impulse magnitude [F s]','Whole-triangle buffered gap [mm]')):ax.set_title(title);ax.set_xlabel('physical time [s]');ax.grid();ax.legend()
    fig.tight_layout();fig.savefig(out/'native_observables.png',dpi=160);plt.close(fig)
    write_json(out/'summary.json',dict(status='PASS' if audits and all(v['status']=='PASS' for v in audits.values()) else 'FAIL',scope='limited passive/analytic identity audit and actual visualization;NOT time/energy/grasp qualification',source_case=a.case,identity=identity,source_hashes=hashes,cases=audits,frames=frames,displacement_magnification=1))
    print(json.dumps(dict(cases=audits)))
if __name__=='__main__':main()
