"""Actual frictionless coupon states; no concept or grasp animation."""
import argparse,csv,json,os,subprocess
from curve_common import ROOT,sha,write_json
from film_nonlinear_assess import read

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    if not a.tag.replace('_','').isalnum():raise ValueError('tag')
    out=ROOT/'designs/visualizations'/('contact_dynamics_'+a.tag);out.mkdir(exist_ok=False)
    os.environ['MPLCONFIGDIR']=str(out/'matplotlib_cache')
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.tri as tri
    import numpy as np
    cases=[('20261116_consistent_tangent41','1','dt=.01'),('20261116_consistent_tangent41','4','dt=.0025'),('20261116_contact_6400_43','1','dt=.0003125'),('20261116_contact_12800_47','1','dt=.00015625')]
    inputs={};fig,axes=plt.subplots(2,2,figsize=(11,7))
    for name,index,label in cases:
        path=ROOT/'results'/('autonomous_film_'+name);summary=json.loads((path/'summary.json').read_text())
        if summary.get('process_status')!='PASS':raise RuntimeError('incomplete plot input')
        source=path/index/'journal.csv';inputs[str(source.relative_to(ROOT))]=sha(source);data=read(source.parent)
        for ax,key,unit in zip(axes.flat,('tip_z','U','contact_area','normal_force'),('mm','F mm','reference mm²','model F')):
            ax.plot(data['time'],data[key],label=label,lw=1);ax.set(xlim=(1.3,2),xlabel='physical time s',ylabel=key+' / '+unit);ax.grid(alpha=.2)
    axes.flat[0].legend();fig.suptitle('Actual SOFA fixed-plane coupon: coarse time gate FAIL; not grasp qualification')
    fig.tight_layout();fig.savefig(out/'actual_contact_trajectories.png',dpi=170);plt.close(fig)
    path=ROOT/'results/autonomous_film_20261116_contact_6400_43/1/journal.csv';rows=list(csv.DictReader(path.open()));time=np.array([float(r['time']) for r in rows])
    triangles=[]
    for i in range(20):
        for j in range(4):triangles.extend([(i*5+j,(i+1)*5+j,i*5+j+1),((i+1)*5+j+1,i*5+j+1,(i+1)*5+j)])
    fig,axes=plt.subplots(4,1,figsize=(11,10),constrained_layout=True)
    for ax,target in zip(axes,(1.3,1.41,1.5,2.)):
        k=int(np.argmin(abs(time-target)));x=np.fromstring(rows[k]['x'],sep=' ').reshape(-1,3)
        pressure=1e-5*np.maximum(x[:,2]-.1,0)
        artist=ax.tripcolor(tri.Triangulation(x[:,0],x[:,1],triangles),pressure,shading='gouraud',cmap='magma')
        fig.colorbar(artist,ax=ax,label='penalty force / reference area (model F/mm²)')
        ax.set_aspect('equal');ax.set(xlabel='actual x / mm',ylabel='actual y / mm',title=f'Actual SOFA t={time[k]:.5f}s, A0={float(rows[k]["contact_area"]):.5g} mm²')
    fig.suptitle('Actual coupon coordinates, no displacement magnification; not Film+Rails or free-object grasp')
    fig.savefig(out/'actual_reference_pressure.png',dpi=170);plt.close(fig)
    write_json(out/'source.json',dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),tool_sha256=sha(__file__),inputs=inputs,
        geometry='actual stored deformed film coordinates',pressure='reference-area penalty traction,not deformed-area Cauchy pressure',qualification='coarse convergence FAIL;no grasp or real-material claim',displacement_scale=1))
    print(out)

if __name__=='__main__':main()
