"""Scientific accepted-state projection,not a concept or imposed wrapping pose."""
import argparse,csv,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from analyse import BASE,sha
def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/b3_contact_layer_union_withdraw1352';g=json.loads((src/'pad_mesh.json').read_text());mesh=json.loads((src/'mesh.json').read_text());body=read(src/'object.csv');film=read(src/'finger0.csv');pad=read(src/'contact_layer0.csv');fig,axes=plt.subplots(1,2,figsize=(9,6));records=[]
 for ax,wanted in zip(axes,(.6,1.2)):
  k=next(k for k,r in enumerate(body) if abs(float(r['time_s'])-wanted)<1e-12);q=np.fromstring(film[k]['q_m'],sep=' ').reshape(-1,3)*1000;p=np.fromstring(pad[k]['q'],sep=' ').reshape(-1,3)*1000;c=np.fromstring(body[k]['rigid_q'],sep=' ')[:3]*1000;ax.add_patch(plt.Circle(c[[0,2]],30,color='#aaa',alpha=.25,label='Actual sphere projection R30'))
  for points,tris,color,label in [(q,mesh['triangles'],'#317ca3','Skin + rails'),(p,g['triangles'],'#cf653d','Added compliant layer')]:
   ax.add_collection(PolyCollection(points[np.array(tris)][:,:,[0,2]],facecolors=color,edgecolors=color,linewidths=.2,alpha=.25,label=label))
  ax.set(xlim=(-35,58),ylim=(-115,5),aspect='equal',xlabel='World X (mm)',ylabel='World Z (mm)',title=f'Actual accepted t={float(body[k]["time_s"]):.3f}s');ax.grid(alpha=.2);records.append(dict(actual_time_s=float(body[k]['time_s']),object_center_m=(c/1000).tolist()))
 axes[0].legend(loc='upper left',fontsize=7);fig.suptitle('Native finite-layer hypothesis: actual accepted coordinates, finger 0 X-Z projection\nAssumed layer material;NOT unsupported Holding / Wrapping / numerical qualification',fontsize=10);fig.tight_layout();fig.savefig(out/'actual_projection.png',dpi=150);fig.savefig(out/'actual_projection.svg');plt.close(fig)
 d=dict(status='ACTUAL_ACCEPTED_PROJECTION_ONLY',source_commit=__import__('subprocess').check_output(['git','rev-parse','HEAD'],text=True).strip(),records=records,scope='Unamplified actual Native coordinates,projected triangles and sphere outline. Not contact area,manufactured geometry,force distribution or concept pose.',input_hashes={f:sha(src/f) for f in ('scene.scn','object.csv','finger0.csv','contact_layer0.csv','mesh.json','pad_mesh.json')},source_sha256=sha(Path(__file__)),physical_validation='NOT QUALIFIED');(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(dict(status=d['status'])))
if __name__=='__main__':main()
