"""Actual saved Native states/triangles;no prescribed shape or interpolated dynamics."""
import argparse,csv,json,os,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def vec(s):return np.fromstring(s,sep=' ')
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);os.environ['MPLCONFIGDIR']=str(out/'mplconfig')
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 fig,axes=plt.subplots(1,3,figsize=(14,4.8));inputs={};cases=('product_root_wire_section845','product_root_wire_section846')
 scene=ET.parse(BASE/'results'/cases[0]/'scene.scn').getroot();top=scene.find("./Node[@name='wheel']/Node/MeshTopology");vertices=vec(top.get('position')).reshape(-1,3)*1000;faces=vec(top.get('triangles')).astype(int).reshape(-1,3)
 for tri in vertices[faces]:
  points=[]
  for i,j in ((0,1),(1,2),(2,0)):
   if tri[i,2]*tri[j,2]<0:points.append(tri[i]+(tri[j]-tri[i])*(-tri[i,2])/(tri[j,2]-tri[i,2]))
  if len(points)==2:axes[0].plot(*np.array(points)[:,:2].T,color='.55',lw=.8)
 for case,color in zip(cases,('tab:blue','tab:orange')):
  folder=BASE/'results'/case;meta=json.loads((folder/'summary.json').read_text());rows=list(csv.DictReader((folder/'wire.csv').open()));q=np.array([vec(r['rigid_q'])[:3] for r in rows]);vel=np.array([vec(r['rigid_v'])[:3] for r in rows]);imp=np.array([vec(r['object_impulse_Ns_Nms'])[:3] for r in rows]);times=np.array([float(r['time_s']) for r in rows]);active=np.where(np.linalg.norm(imp,axis=1)>0)[0];normal=imp[active[0]]/np.linalg.norm(imp[active[0]])
  axes[0].plot(q[:,0]*1000,q[:,1]*1000,'.-',ms=2,label=case[-3:],color=color)
  axes[0].add_patch(plt.Circle(q[-1,:2]*1000,meta['wire_radius_m']*1000,fill=False,color=color,lw=1))
  axes[1].plot(times*1000,vel@normal*1000,'.-',ms=2,label=case[-3:],color=color)
  axes[2].plot(times*1000,np.linalg.norm(imp,axis=1)*1e9,'.-',ms=2,color=color,label=case[-3:])
  for name in ('wire.csv','scene.scn','summary.json'):inputs[str((folder/name).relative_to(BASE))]=sha(folder/name)
 axes[0].set(xlim=(1.48,2.3),ylim=(-.25,.4),xlabel='x [mm]',ylabel='y [mm]',title='Actual wheel section + accepted sphere paths');axes[0].set_aspect('equal');axes[0].legend()
 axes[1].set(xlabel='Accepted step time [ms]',ylabel='Normal velocity [mm/s]',title='Actual velocity, normal from first impulse');axes[1].axhline(0,color='.5',lw=.5);axes[1].legend()
 axes[2].set(xlabel='Accepted step time [ms]',ylabel='Step impulse [nN s]',title='Native J-transpose lambda (NOT force peak)');axes[2].legend()
 fig.suptitle('Actual Native SOFA26.06 wire-section proxy, NOT complete wire/gripper\ndt=250us, mu=0, inward10uN, assumed10mg, fixed wheel; source cebebc3 + preserved producer snapshots',fontsize=10);fig.tight_layout();fig.savefig(out/'actual_wire_section.png',dpi=160);plt.close(fig)
 result=dict(status='ACTUAL_NATIVE_STATE_PLOT_ONLY',source_sha256=sha(Path(__file__)),input_hashes=inputs,scope='Actual saved states and plane section of actual scene triangles. No enlarged displacement or prescribed dynamic pose. Circle is the actual sphereproxy radius. Lines join accepted samples for plotting,notcontinuous integration/event proof. Notcontact/time/energy/wholewirePASS.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(out/'actual_wire_section.png')
if __name__=='__main__':main()
