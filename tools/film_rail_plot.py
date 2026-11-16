"""Actual coupled SOFA states only; no invented wrapping/object animation."""
import argparse,csv,json,os
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    if not a.tag.replace('_','').isalnum():raise ValueError('tag')
    base=ROOT/'results/autonomous_film_20261116_rail_recovery90';summary=json.loads((base/'summary.json').read_text());identity=json.loads((base/'identity.json').read_text())
    if summary['status']!='PASS':raise RuntimeError('failed states cannot be displayed as valid actuation')
    rows=list(csv.DictReader((base/'1/journal.csv').open()));time=np.array([float(r['time']) for r in rows]);out=ROOT/'designs/visualizations'/('film_rail_'+a.tag);out.mkdir(exist_ok=False)
    os.environ['MPLCONFIGDIR']=str(out/'matplotlib_cache');import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
    nx=21;faces=[]
    for offset,ny,width,thickness,y,z in identity['layout']:
        for i in range(nx-1):
            for j in range(ny-1):faces.extend([(offset+i*ny+j,offset+(i+1)*ny+j,offset+i*ny+j+1),(offset+(i+1)*ny+j+1,offset+i*ny+j+1,offset+(i+1)*ny+j)])
    fig,axes=plt.subplots(2,2,figsize=(12,7),constrained_layout=True)
    selected=[]
    for ax,target in zip(axes.flat,(.2,1.,2.,8.)):
        index=int(np.argmin(abs(time-target)));x=np.fromstring(rows[index]['x'],sep=' ').reshape(-1,3);wires=[]
        for offset,ny,*_ in identity['layout'][1:]:
            guide=[]
            for i in (0,5,10,15,20):
                p0,p1,p2=x[offset+3*i],x[offset+3*i+2],x[offset+3*(i+1 if i<20 else i-1)]
                tangent=p2-p0 if i<20 else p0-p2;normal=np.cross(tangent,p1-p0);normal/=np.linalg.norm(normal);guide.append((p0+p1)/2-.2*normal)
            wires.append(np.array(guide))
        for part,(offset,ny,*_) in enumerate(identity['layout']):
            middle=x[offset+ny//2:offset+nx*ny:ny];ax.plot(middle[:,0],middle[:,2],label=('skin','left rail','right rail')[part])
        for wire in wires:ax.plot(wire[:,0],wire[:,2],'--',color='orange',lw=1)
        ax.set(xlabel='actual x / mm',ylabel='actual z / mm',title=f't={time[index]:.2f}s;T/rail={float(rows[index]["T_per_rail"]):.3g} model F');ax.grid(alpha=.2)
        name=f'actual_t{target:g}.obj'
        with (out/name).open('x') as stream:
            stream.write('# Actual SOFA midsurfaces and eccentric guide paths;no object/grasp;no coordinate magnification\n')
            for point in np.concatenate([x,*wires]):stream.write('v '+' '.join(format(v,'.17g') for v in point)+'\n')
            for face in faces:stream.write('f '+' '.join(str(i+1) for i in face)+'\n')
            for k in range(2):stream.write('l '+' '.join(str(len(x)+5*k+j+1) for j in range(5))+'\n')
        selected.append(dict(time=float(time[index]),row=index,obj=name))
    axes.flat[0].legend();fig.suptitle('Actual film + two flexible rails + routed tendons;separate axis scales,coordinates unmodified;not grasp qualification')
    fig.savefig(out/'actual_actuation_recovery.png',dpi=180);fig.savefig(out/'actual_actuation_recovery.svg');plt.close(fig)
    fig,axes=plt.subplots(2,2,figsize=(11,7),constrained_layout=True)
    for key in ('skin_tip_z','left_tip_z','right_tip_z'):axes[0,0].plot(time,[float(r[key]) for r in rows],label=key)
    axes[0,0].set(ylabel='actual tip z / mm');axes[0,0].legend()
    axes[0,1].plot(time,[float(r['T_per_rail']) for r in rows]);axes[0,1].set(ylabel='prescribed tension / rail / model F')
    for key in ('U_shell','U_attachment','K','tendon_work'):axes[1,0].plot(time,[float(r[key]) for r in rows],label=key)
    axes[1,0].legend();axes[1,0].set(ylabel='model F mm;not whole grasp energy')
    axes[1,1].plot(time,[float(r['cable_length'])-200 for r in rows]);axes[1,1].set(ylabel='two-path length change / mm')
    for ax in axes.flat:ax.set(xlabel='physical time / s');ax.grid(alpha=.2)
    fig.suptitle('Actual low-tension no-object prototype;coupled time convergence not yet qualified');fig.savefig(out/'actual_control_energy.png',dpi=180);plt.close(fig)
    write_json(out/'source.json',dict(journal_sha256=sha(base/'1/journal.csv'),identity_sha256=sha(base/'identity.json'),selected=selected,script_sha256=sha(__file__),
        scope='actual accepted SOFA rectangular equal-core prototype;not tapered concept,not contact/grasp/physical-material certification',coordinate_scale=1,axis_display='independent x/z plotting scales,not a geometric 3D magnification',geometry='thin-shell midsurfaces;physical thickness specified in material kernel,not fake mesh extrusion'))
    print(out)
if __name__=='__main__':main()
