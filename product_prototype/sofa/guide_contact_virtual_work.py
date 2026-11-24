"""Actual Guide source-row impulse/velocity contractions,NOT SDK-stage energy."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);meta=json.loads((src/'summary.json').read_text());assert meta['status']=='PASS_READONLY_GUIDE_ROW_WRENCH_COUPON' and meta['maximum_observer_q_v_error']<=1e-12;root=ET.parse(src/'scene.scn').getroot();records=json.loads((src/'pair_wrenches.json').read_text());state={};free={}
 for i in range(3):
  rows=read(src/f'guide_frames{i}.csv');initial=root.find(f"Node[@name='guides{i}']/MechanicalObject");n=len(np.fromstring(initial.get('position'),sep=' '))//7;previous=np.zeros((n,6));assert initial.get('velocity') is None,'Explicitnonzeroinitialvelocityrequiresseparateaudit'
  for r in rows:
   v=np.fromstring(r['rigid_v'],sep=' ').reshape(-1,6);state[(i,float(r['time_s']))]=(previous,v);previous=v
  for r in read(src/f'direct{i}.csv'):free[(i,float(r['time_s']),int(r['row_id']),int(r['column_id']))]=np.fromstring(r['free_v'],sep=' ')
 blocks={}
 for r in records:
  f=r['guide_finger'];t=r['time_s'];row=r['row_id'];col=r['rigid_column'];imp=np.array(r['impulse_Ns_Nms']);previous,v=state[(f,t)];b=blocks.setdefault((t,row),dict(time_s=t,row_id=row,source_pair=r['source_pair'],accepted_endpoint_contraction_J=0.,free_velocity_contraction_J=0.,midpoint_accepted_contraction_J=0.,net_linear_impulse=np.zeros(3),parent_entries=0));b['accepted_endpoint_contraction_J']+=float(imp@v[col]);b['free_velocity_contraction_J']+=float(imp@free[(f,t,row,col)]);b['midpoint_accepted_contraction_J']+=float(imp@(.5*(previous[col]+v[col])));b['net_linear_impulse']+=imp[:3];b['parent_entries']+=1
 sums={k:float(sum(b[k] for b in blocks.values())) for k in ('accepted_endpoint_contraction_J','free_velocity_contraction_J','midpoint_accepted_contraction_J')};linear=max((float(abs(b['net_linear_impulse']).max()) for b in blocks.values()),default=None)
 for b in blocks.values():b['net_linear_impulse']=b['net_linear_impulse'].tolist()
 (out/'row_contractions.json').write_text(json.dumps(list(blocks.values())));d=dict(status='ACTUAL_GUIDE_ROW_VIRTUAL_WORK_INVENTORY_ONLY',case=a.case,actual_source_rows=len(blocks),sums=sums,maximum_pair_net_linear_impulse_component_Ns=linear,scope='Sum actual mappedRigid3 rowJ-transposelambda contractedwith actualfree/accepted/previousacceptedGuidev. These are separatelylabeled discretekinematiccontractions,NOT observedSDKstagework,physicalheat,dissipation or globalenergyclosure. Netlinearimpulsechecksinternalpairtranslationalbalance only;parentreferencepoint/angularbalanceunqualified. Noq/vmodified.',source_sha256=sha(Path(__file__)),input_hashes={f:sha(src/f) for f in ('summary.json','pair_wrenches.json','scene.scn')});(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
