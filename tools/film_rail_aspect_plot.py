"""Read-only actual no-object SOFA candidate geometry,not a prescribed wrap pose."""
import argparse,csv,json,os,shutil,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);m=json.loads((src/'summary.json').read_text())
 if m['status']!='PASS':raise ValueError('complete actual/reference API comparison required')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');os.environ.setdefault('MPLCONFIGDIR',str(out/'matplotlib_cache'));import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 fig,axes=plt.subplots(2,3,figsize=(15,8));rows=[];error=0.
 for j,h in enumerate((.075,.1,.125)):
  folder=src/('rail'+str(h));trial=m['trials'][str(h)]
  for f,digest in trial['raw_hashes'].items():
   if sha(folder/f)!=digest:raise ValueError('actual geometry raw changed')
  if sha(folder/'scene.scn')!=trial['scene_sha256']:raise ValueError('actual Scene changed')
  tree=ET.parse(folder/'scene.scn');topology=tree.find('.//TriangleSetTopologyContainer');rest=np.fromstring(topology.get('position'),sep=' ').reshape(-1,3);tri=np.fromstring(topology.get('triangles'),sep=' ',dtype=int).reshape(-1,3);field=list(csv.DictReader((folder/'film.csv').open()))[-1];x=np.fromstring(field['x'],sep=' ').reshape(-1,3);u=np.fromstring(list(csv.DictReader((folder/'displacement.csv').open()))[-1]['u'],sep=' ').reshape(-1,3);error=max(error,float(np.max(abs(x-rest-u))))
  with (out/('actual_rail'+str(h)+'.obj')).open('w') as f:
   f.write('# ACTUAL SOFA saved local geometry,scale1;NO object/contact/grasp\n')
   for v in x:f.write('v '+' '.join(format(z,'.17g') for z in v)+'\n')
   for t in tri:f.write('f '+' '.join(str(i+1) for i in t)+'\n')
  ax,profile=axes[0,j],axes[1,j];P=np.array([[1.,0,0],[0,1/np.sqrt(2),1/np.sqrt(2)]]);from matplotlib.collections import PolyCollection;projection=x@P.T;ax.add_collection(PolyCollection(projection[tri],facecolor='tab:blue',edgecolor='gray',linewidth=.1,alpha=.2));ax.autoscale_view();ax.set_aspect('equal');ax.set_xlabel('orthographic x [mm]');ax.set_ylabel('orthographic (y+z)/sqrt2 [mm]');ax.set_title(f'ACTUAL rail {1000*h:g}um, t={1000*float(field["time"]):g}ms\nGeometry scale1;wire omitted')
  for name,start,ny in (('Skin',0,5),('Left rail',105,3),('Right rail',168,3)):
   line=x[start:start+21*ny].reshape(21,ny,3).mean(axis=1);reference=rest[start:start+21*ny].reshape(21,ny,3).mean(axis=1);profile.plot(line[:,0],line[:,2]-reference[:,2],label=name)
  profile.set_xlabel('actual local x [mm]');profile.set_ylabel('width-mean local z deformation [mm]');profile.legend(fontsize=7);profile.grid();rows.append(dict(rail_thickness_mm=h,actual_time_s=float(field['time']),stage_tendon_work_Nmm=trial['stage_tendon_work_Nmm'],legacy_sampled_work_Nmm=float(field['tendon_work']),**trial['endpoint_shape']))
 fig.suptitle(f'ACTUAL SOFA single free coupon;same core volume/mass/C2 Tmax100uN per rail;dt={1e6*m["nominal_dt_s"]:g}us\nDLL {m["binary_sha256"][:12]};zero gravity,NO object/contact;profile axes independent;NOT time/wrapping/grasp certification');fig.tight_layout(rect=(0,0,1,.92));fig.savefig(out/'actual_rail_comparison.png',dpi=160);plt.close(fig)
 with (out/'actual_comparison.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 r=dict(status='PASS' if error<=1e-12 else 'FAIL',scope='actual scale1 geometry/profile reconstruction ONLY;NOT performance qualification',input_summary_sha256=sha(src/'summary.json'),binary_sha256=m['binary_sha256'],actual_reconstruction_max_abs_mm=error,matched_tension=True,matched_core_material_volume=True,matched_actuation_work=False,contact_area=None,pressure=None,holding_load=None,selected_design=None,raw_hashes={f.name:sha(f) for f in out.iterdir() if f.suffix in ('.png','.csv','.obj')});write_json(out/'summary.json',r);print(json.dumps(r))
if __name__=='__main__':main()
