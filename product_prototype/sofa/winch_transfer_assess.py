"""Actual row ownership, matched control and unintended root contact gate."""
import argparse,collections,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha

def read(path):return list(csv.DictReader(path.open()))
def unique_row(text,col=None):
 rows=set()
 for part in text.split(';'):
  if not part:continue
  row,c,value=part.split(':')
  if (col is None or int(c)==col) and np.linalg.norm(np.fromstring(value,sep=' '))>0:rows.add(int(row))
 assert len(rows)==1,rows;return next(iter(rows))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());active=BASE/'results/winch_observed1884';control=BASE/'results/winch_control1883';root=ET.parse(active/'scene.scn').getroot();dt=float(root.get('dt'));qa=np.array([np.fromstring(r['q'],sep=' ').reshape(-1,3) for r in read(active/'skin.csv')]);qc=np.array([np.fromstring(r['q'],sep=' ').reshape(-1,3) for r in read(control/'skin.csv')]);assert len(qa)==len(qc)==100;q0=np.fromstring(root.find("Node[@name='finger0']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);tip=int(q0[:,2].argmin());records=[]
 for j in range(2):
  output=[r for r in read(active/f'tendon{j}_phases.csv') if r['phase']=='accepted_end'];inputs=[r for r in read(active/f'winch{j}_input_phases.csv') if r['phase']=='accepted_end'];qinit=np.fromstring(root.find(f"Node[@name='fingerTendon{j}']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);L0=np.linalg.norm(np.diff(qinit,axis=0),axis=1).sum();forces=[];length=[];inputids=[];outputids=[]
  for inp,op in zip(inputs,output):
   ir=unique_row(inp['J'],0);orr=unique_row(op['J']);lam=np.fromstring(op['lambda_Ns'],sep=' ');q=np.fromstring(op['q'],sep=' ').reshape(-1,3);forces.append([float(lam[ir]/dt),float(lam[orr]/dt)]);length.append(abs(np.linalg.norm(np.diff(q,axis=0),axis=1).sum()-L0));inputids.append(ir);outputids.append(orr)
  records.append(dict(tendon=j,input_row_ids=sorted(set(inputids)),output_row_ids=sorted(set(outputids)),maximum_input_tension_N=max(x[0] for x in forces),maximum_output_tension_N=max(x[1] for x in forces),final_input_output_tension_N=forces[-1],maximum_output_geometric_length_error_m=float(max(length))))
 counts=collections.Counter();peak={};root_contacts=0
 for r in read(active/'contact_provenance.csv'):
  lam=float(r['lambda_Ns']);pair=(r['model0'],r['model1'])
  if lam!=0:
   counts[pair]+=1;peak[pair]=max(peak.get(pair,0),abs(lam/dt))
   if any('/winch'in n for n in pair):root_contacts+=1
 pairs=[dict(model_pair=list(k),nonzero_response_rows=v,maximum_absolute_row_multiplier_equivalent_N=peak[k]) for k,v in counts.items()];delta=qa[-1,tip]-qc[-1,tip];maxdiff=float(np.linalg.norm(qa-qc,axis=2).max());d=dict(status='FAIL_UNINTENDED_ROOT_ROTOR_SUPPORT_CONTACT' if root_contacts else 'PASS_INCREMENTAL_ACTUATION_SCOPE_ONLY' if delta[0]<0 and maxdiff>1e-6 else 'FAIL_INCREMENTAL_DIRECTION',actual_incremental_inward_direction=bool(delta[0]<0),reference_minimum_z_vertex_id=tip,reference_vertex_active_minus_control_m=delta.tolist(),maximum_active_control_nodal_difference_m=maxdiff,actual_tendon_records=records,contact_pairs=pairs,nonzero_root_contact_rows=root_contacts,source_sha256=sha(Path(__file__)),inputs_sha256={str(p):sha(p) for p in [active/'scene.scn',active/'skin.csv',active/'contact_provenance.csv',control/'skin.csv']},scope='Actual Native child-J row ownership; no4row assumption. Observer1884purity exactly0. Nonzero response row count is NOT area. Scalar row force-equivalent peak is NOT net vertical support or root reaction. Matched zero-stroke control still has taut length constraints and gravity, not force-free. Valid physical startup1882is not promoted to unbraced drive: real root rotor/Support contact must be removed mechanically. Historical failures preserved, no q/v or oldraw edits.')
 (out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
if __name__=='__main__':main()
