"""Render actual post-fix film journals; no concept geometry or fake grasp."""
import csv,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.runtime/matplotlib_design'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from curve_common import sha,write_json

def main():
    folder=ROOT/'designs/visualizations/film_newton_20261116_v1';folder.mkdir(exist_ok=False)
    campaign=ROOT/'results/autonomous_film_20261116_exact_time13'
    fig,axes=plt.subplots(2,2,figsize=(12,8));sources={}
    for i in (1,2,4):
        path=campaign/str(i)/'journal.csv';rows=list(csv.DictReader(path.open()));sources[str(path.relative_to(ROOT))]=sha(path)
        for ax,key,label in zip(axes.flat,('tip_z','U','contact_area','normal_force'),('Tip z [mm]','Stored U [F mm]','Reference contact area [mm2]','Normal reaction [F]')):
            ax.plot([float(r['time']) for r in rows],[float(r[key]) for r in rows],label=f'dt={.2/i:g} s');ax.set_xlabel('time [s]');ax.set_ylabel(label);ax.grid(alpha=.25);ax.legend()
    fig.suptitle('Actual SOFA film coupon: final equilibrium recovered; transient convergence FAIL')
    fig.tight_layout();fig.savefig(folder/'actual_trajectories.png',dpi=160);plt.close(fig)
    rows=list(csv.DictReader((campaign/'2/journal.csv').open()));fig,axes=plt.subplots(1,3,figsize=(14,4))
    for ax,index in zip(axes,(0,14,len(rows)-1)):
        row=rows[index];flat=list(map(float,row['x'].split()));vertices=[flat[k:k+3] for k in range(0,len(flat),3)];faces=[]
        for i in range(20):
            for j in range(4):q=5*i+j;faces.extend(((q,q+5,q+1),(q+5,q+6,q+1)))
        polys=[[(vertices[k][0],vertices[k][1]+50*vertices[k][2]) for k in face] for face in faces]
        colors=['#dc8645' if max(vertices[k][2] for k in face)>.1 else '#79aabc' for face in faces]
        ax.add_collection(PolyCollection(polys,facecolors=colors,edgecolors='#355c70',linewidths=.3));ax.autoscale_view();ax.set_xlabel('x [mm]');ax.set_ylabel('y + 50*z [mm]');ax.set_title(f'Actual t={float(row["time"]):g} s')
    fig.suptitle('Actual simulated states; z exaggerated x50; orange = triangle with active fraction, not full contact area')
    fig.tight_layout();fig.savefig(folder/'actual_states.png',dpi=160);plt.close(fig)
    write_json(folder/'source.json',dict(classification='Actual Simulated State; NOT Numerically Qualified transient or free-object grasp',sources=sources))
    print(folder)

if __name__=='__main__':main()
