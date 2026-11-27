"""Same immutable actual contact material probes for every contact discretization.
Direct FE displacement interpolation, no producer/FEMassembler/optimizer.
"""
import sys,json,shutil
import numpy as np
from baseline_registry import ROOT,REPO,ref,dump
from anchor_gap_trace37 import prepare,locate

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');prior=ROOT/'validation/integrated/primaryP1_anchor37_fixed_h5_n2';old=json.loads((prior/'summary.json').read_text());geo=json.loads((REPO/old['geometry']['path']).read_text());reports=[]
 for tag in sys.argv[2:]:
  src=ROOT/'validation/integrated'/tag;d=json.loads((src/'summary.json').read_text());a=[dict(np.load(REPO/r['path'])) for r in d['fields']]
  for k,b in enumerate(a):
   if 'U' not in b:b['U']=np.column_stack([np.load(REPO/r['reference']['path'])['U'] for r in d['body_results'][k]['displacement_chunks']])
  # Upstream source has opposite sign on body1;store contact/source pieces separately.
  prepared={};positions=[];directions=[];elastic=[];labels=[];unmapped=0
  for j,pat in enumerate(geo['patches'][:-3]):
   n=np.array(pat['direction']);axis=int(np.argmax(abs(n)));value=pat['exact_CAD_centroid_mm'][axis];key=(axis,round(value,7))
   if key not in prepared:prepared[key]=prepare(a[1],axis,value)
   for qd in geo['body_quadrature'][0][j]['quadrature']:
    q=np.array(qd['point_mm']);hit=locate(q,prepared[key])
    if hit is None:unmapped+=1;continue
    nd,bc=hit;u0=np.einsum('a,aim->im',qd['barycentric'],a[0]['U'].reshape(-1,3,d['contact_variables']+6)[qd['nodes']]);u1=np.einsum('a,aim->im',bc,a[1]['U'].reshape(-1,3,d['contact_variables']+6)[nd]);trace=np.r_[n@(u0[:,:-6]-u1[:,:-6]),n@(u0[:,-6:]+u1[:,-6:])];elastic.append(trace);positions.append(q);directions.append(n);labels.append(j)
  elastic=np.array(elastic);positions=np.array(positions);directions=np.array(directions);ops=np.load(REPO/d['operators']['path']);eq=ops['equality'];scale=np.tile([1,1,1,.01,.01,.01],2);states=[]
  for row in d['rows']:
   ae=np.array(row['reduced_equality_matrix']);lm=np.array(row['equality_multiplier']);T=ae@np.linalg.pinv(eq*scale[:,None],rcond=1e-10);r=(scale*(T.T@lm)).reshape(2,6);dr=r[0]-r[1];gap=elastic@np.r_[row['contact_forces_N'],row['external_wrench_N_Nmm']]+np.einsum('qi,qi->q',directions,dr[:3]+np.cross(dr[3:],positions));states.append(dict(case=row['case'],minimum_fixed_probe_gap_mm=float(gap.min()),negative1e_minus8_count=int(sum(gap<-1e-8)),original_patch_at_minimum=int(labels[int(np.argmin(gap))])))
  reports.append(dict(source=ref(src/'summary.json'),probe_count=len(positions),unmapped=unmapped,rows=states,minimum_fixed_probe_gap_mm=min(s['minimum_fixed_probe_gap_mm'] for s in states),negative1e_minus8_count=sum(s['negative1e_minus8_count'] for s in states)))
 dump(out/'summary.json',dict(status='ACTUAL_P1_IDENTICAL_MATERIAL_PROBE_CONTACT_FAIL' if any(r['negative1e_minus8_count'] for r in reports) else 'ACTUAL_P1_FIXED_PROBE_NO_VIOLATION_NOT_CONTINUOUS_CERTIFICATE',candidate=old['candidate'],verifier=ref(out/'verifier.py'),interpolation_helper=ref(ROOT/'scripts/anchor_gap_trace37.py'),fixed_material_probe_geometry=ref(REPO/old['geometry']['path']),reports=reports,identical_probe_counts=len(set((r['probe_count'],r['unmapped']) for r in reports))==1,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Same material points of immutable37actualBRep/FEintersectioncentroids;sampled minima only,not global continuous bounds.','Sample counts on changed integration partitions are not directly comparable;this report fixes probe positions.','Zero cellresultant does not allow pointwise penetration;all sampled negative gaps retained.','Six-rigid recovery uses original1e-10equilibriumrankcutoff;no near-null roundoff inversion.']))
 print(json.dumps([dict(source=r['source']['path'],minimum=r['minimum_fixed_probe_gap_mm'],negative=r['negative1e_minus8_count']) for r in reports]))
if __name__=='__main__':main()
