"""All six REST lead paths against one completed candidate,not whole wire CCD."""
import argparse,json,subprocess,sys,time,re
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,evaluate,sha,sector
from assembly_recipe_io import resolve_recipe
from deformed_wire_screen import probes

def worker(a):
 out=BASE/'results'/a.tag;start=time.monotonic();src=BASE/'results/product_remaining_f2lead975/assembly_delta_recipe.json';parts,hashes=resolve_recipe(src);solids=[evaluate(p['shape']) for p in parts];sources=[BASE/'results'/n/'summary.json' for n in ('product_supplier_first_recheck890','product_supplier_second_full_wire887')];routes=[np.asarray(json.loads(f.read_text())['route_mm']) for f in sources];records=[]
 for finger in range(3):
  S=sector(120*finger)
  for cable,route0 in enumerate(routes):
   route=route0@S[:3,:3].T+S[:3,3];prefix=f'f{finger}_c{cable}';intended={prefix+'_root_redirect',f'f{finger}_two_channel_drum',*[prefix+f'_turn{k}' for k in (1,2,3)]};contacts=[];count=0;t=time.monotonic()
   if a.finger_chain_only:
    eyes=[]
    for part,body in zip(parts,solids):
     m=re.fullmatch(prefix+r'_s(\d+)_eyelet',part['name'])
     if m:eyes.append((int(m[1]),part['name'],body.center_mass))
    eyes.sort()
    if len(eyes)<2 or [x[0] for x in eyes]!=list(range(len(eyes))):raise ValueError('continuous station identity required')
    if np.linalg.norm(eyes[0][2]-route[0])>1e-10:raise ValueError('first guide/Root route identity mismatch')
    route=np.asarray([x[2] for x in eyes]);intended={x[1] for x in eyes}
   for sample,probe in probes(route,.22522275007459786):
    count+=1
    for p,body in zip(parts,solids):
     if np.any(np.minimum(body.bounds[1],probe.bounds[1])-np.maximum(body.bounds[0],probe.bounds[0])<=0):continue
     h=trimesh.boolean.intersection([probe,body],engine='manifold')
     if len(h.faces):contacts.append(dict(sample=sample,part=p['name'],faces=len(h.faces),signed_volume_mm3=float(h.volume),classification='INTENDED_PROXIMITY_NOT_CONTACT_PASS' if p['name'] in intended else 'UNRESOLVED_OBSTACLE'))
   record=dict(finger=finger,cable=cable,probe_count=count,route_mm=route.tolist(),runtime_s=time.monotonic()-t,intersections=contacts);records.append(record);(out/f'lead_f{finger}_c{cable}.json').write_text(json.dumps(record,indent=2))
 for f in [Path(__file__),BASE/'cad/assembly_recipe_io.py',BASE/'cad/manufacturing_assembly.py',BASE/'cad/deformed_wire_screen.py',*sources]:hashes[str(f.relative_to(BASE))]=sha(f)
 result=dict(status='COMPLETED_REST_LEAD_OBSTACLE_REVIEW' if any(h['classification']=='UNRESOLVED_OBSTACLE' for r in records for h in r['intersections']) else 'SIX_COMPLETED_REST_LEADS_OBSTACLE_CLEAR_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes=hashes,assembly_part_count=len(parts),lead_results=[{k:v for k,v in r.items() if k!='intersections'}|dict(unresolved=sum(h['classification']=='UNRESOLVED_OBSTACLE' for h in r['intersections'])) for r in records],runtime_s=time.monotonic()-start,fabrication_ready=False,scope='All6lead paths firstguide→Root→3turns→drum against SAME completed283part REST candidate975. New retained neighbours justify this audit;prior individual scopes unchanged. Positive intendedwheelproximities retained,not physicalcontact approval. NO wire-wire/moving/fullfinger CCD,wire friction/fatigue/preload/joint/Native/holding/STEPqualification.')
 result['finger_chain_only']=a.finger_chain_only
 if a.finger_chain_only:
  result['status']='FINGER_GUIDE_CHAIN_REVIEW' if any(r['unresolved'] for r in result['lead_results']) else 'SIX_REST_GUIDE_CHAINS_OBSTACLE_CLEAR_ONLY'
  result['scope']='ONLY6REST station0..lastguidecentre straight chains from actual ringvolume centroids against283parts. Firststation/leadroute match checked1e-10mm identity guard,not contact tolerance. NO Root/turn/drum repetition. Eyelet wall proximities explicitly retained,not borefriction/wirebending/finiteguidecontact approval. No distalanchor/pulltermination segments/fullwire/movingCCD/Native/holding/STEPqualification.'
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],runtime_s=result['runtime_s']),indent=2))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--finger-chain-only',action='store_true');p.add_argument('--worker',action='store_true');a=p.parse_args()
 if Path(a.tag).name!=a.tag:p.error('local tag required')
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--worker']+(['--finger-chain-only'] if a.finger_chain_only else []);proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_COMPLETED_LEAD_CHILD',process=proc),indent=2))
 d=json.loads((out/'summary.json').read_text());print(json.dumps({k:d[k] for k in ('status','runtime_s') if k in d},indent=2))
if __name__=='__main__':main()
