"""Independent accepted-state/whole-triangle audit of isolated impact trials."""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_surface_distance import point_triangles
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args()
    source=ROOT/'results'/('autonomous_film_'+a.case);summary=json.loads((source/'summary.json').read_text())
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);records={};inputs={}
    for directory in sorted(source.glob('film_sequence_*')):
        if summary['cases'][directory.name]['status']!='PASS':raise ValueError('complete executions required')
        tree=ET.parse(directory/'scene.scn');root=tree.find("MechanicalObject[@name='dofs']")
        world=tree.find("Node[@name='assembly']/Node[@name='actual']/MechanicalObject")
        if world is None:world=next(e for e in tree.findall('.//MechanicalObject') if e.get('name')=='world')
        rest=np.fromstring(world.get('rest_position'),sep=' ').reshape(-1,3)
        triangles=np.fromstring(tree.find('.//TriangleSetTopologyContainer').get('triangles'),sep=' ',dtype=int).reshape(-1,3)
        center=np.fromstring(tree.find("Node[@name='fixed']/MechanicalObject").get('position'),sep=' ')
        radius=float(tree.find('FilmIsolatedEventStep').get('radius'))
        endpoints=list(csv.DictReader((directory/'event.csv.endpoint.csv').open()));actual=list(csv.DictReader((directory/'journal.csv').open()));local=list(csv.DictReader((directory/'displacement.csv').open()))
        if len(endpoints)!=len(actual) or len(actual)!=len(local):raise ValueError('incomplete state journals')
        minimum=float('inf');world_error=0;local_error=0;energy_error=0;degenerate=0
        for e,r,l in zip(endpoints,actual,local):
            if abs(float(e['time'])-float(r['time']))>1e-12 or abs(float(e['time'])-float(l['time']))>1e-12:raise ValueError('journal physical-time mismatch')
            q=np.fromstring(e['local_displacement'],sep=' ').reshape(-1,3);x=np.fromstring(r['x'],sep=' ').reshape(-1,3)
            u=np.fromstring(l['u'],sep=' ').reshape(-1,3)
            local_error=max(local_error,float(np.max(np.abs(q-u))));world_error=max(world_error,float(np.max(np.abs(x-(rest+q)))))
            for k,j in (('shell_energy','U_shell'),('attachment_energy','U_attachment'),('kinetic_energy','K')):energy_error=max(energy_error,abs(float(e[k])-float(r[j])))
            distance,_,bad=point_triangles(center,x[triangles]);degenerate+=len(bad) if hasattr(bad,'__len__') else int(bad)
            minimum=min(minimum,float(np.min(distance-radius)))
        records[directory.name]=dict(status='PASS' if minimum>=-1e-10 and local_error==0 and world_error<=1e-12 and energy_error<=1e-20 and degenerate==0 else 'FAIL',minimum_buffered_triangle_gap_mm=minimum,maximum_local_displacement_error_mm=local_error,maximum_world_position_error_mm=world_error,maximum_stored_kinetic_energy_difference_Fmm=energy_error,degenerate=degenerate)
        for name in ('scene.scn','event.csv.endpoint.csv','journal.csv','displacement.csv','event.csv'):inputs[str((directory/name).relative_to(ROOT))]=sha(directory/name)
    result=dict(status='PASS' if records and all(r['status']=='PASS' for r in records.values()) else 'FAIL',scope='whole FE triangles at ACCEPTED endpoints and actual FF/owner journal identity;NOT swept CCD,contact area,full energy or original C2-time certification',records=records,time_gate=summary['sequence_time'],inputs=inputs,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),script_sha256=sha(__file__))
    write_json(out/'summary.json',result);print(json.dumps(records))
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(3,1,figsize=(8,8),sharex=True)
    for directory in sorted(source.glob('film_sequence_*')):
        rows=list(csv.DictReader((directory/'event.csv.endpoint.csv').open()));events=list(csv.DictReader((directory/'event.csv').open()));t=np.array([float(r['time']) for r in rows])*1000
        axes[0].plot(t,[np.fromstring(r['local_velocity'],sep=' ').reshape(-1,3)[102,2] for r in rows],label=directory.name)
        axes[1].plot(t,[float(r['attachment_energy']) for r in rows])
        axes[2].plot(t,[float(r['gap']) for r in rows])
        event=events[0];axes[0].scatter([1000*float(event['event_time'])]*2,[float(event['pre_normal']),float(event['post_normal'])],s=12)
    axes[0].set_ylabel('Tip velocity [mm/s]');axes[1].set_ylabel('Attachment U [F mm]');axes[2].set_ylabel('Point gap [mm]');axes[2].set_xlabel('Physical time [ms]');axes[0].legend()
    fig.suptitle('Actual SOFA: isolated point impact, ZERO tendon tension\n'+a.case+'; not wrapping/grasp certification')
    fig.tight_layout();fig.savefig(out/'actual_impact.png',dpi=160);plt.close(fig)
if __name__=='__main__':main()
