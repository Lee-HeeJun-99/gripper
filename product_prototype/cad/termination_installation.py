"""Positive-clearance threading contract;no assumed compressible terminal."""
import argparse,json,subprocess
from pathlib import Path
import numpy as np
from manufacturing_assembly import BASE,evaluate,sha
from assembly_recipe_io import resolve_recipe

def threading(end_a_max,end_b_max,opening_min):
 if not all(np.isfinite(x) and x>0 for x in (end_a_max,end_b_max,opening_min)):raise ValueError('finite positive dimensions required')
 smaller=min(end_a_max,end_b_max)
 return dict(max_feed_end_diameter_mm=smaller,diametral_clearance_mm=opening_min-smaller,positive_clearance=bool(opening_min>smaller))

def minimum_loop_radius(loop):
 p=np.asarray(loop,dtype=float)[:,1:];a=p[:-1];v=np.diff(p,axis=0);den=np.sum(v*v,axis=1)
 if np.any(den==0):raise ValueError('degenerate hole edge')
 t=np.clip(-np.sum(a*v,axis=1)/den,0,1);return float(np.linalg.norm(a+t[:,None]*v,axis=1).min())

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
 if Path(a.tag).name!=a.tag:p.error('local tag required')
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/product_distal_seat992/assembly_delta_recipe.json';spec=BASE/'config/termination_candidates_v48.json';parts,hashes=resolve_recipe(src);openings=[]
 for p0 in parts:
  if not p0['name'].endswith('_s5_eyelet'):continue
  op=p0['shape']
  while op['op']=='transform':op=op['shape']
  section=evaluate(op).section(plane_origin=[0,0,0],plane_normal=[1,0,0])
  if section is None or len(section.discrete)!=2:raise ValueError('two actual ring loops required')
  radii=[minimum_loop_radius(line) for line in section.discrete];openings.append(dict(part=p0['name'],mesh_minimum_central_hole_diameter_mm=2*min(radii),physical_hole_diameter_mm=None))
 minimum=min(r['mesh_minimum_central_hole_diameter_mm'] for r in openings);cfg=json.loads(spec.read_text());d={r['item']:max(r['diameter_mm']) for r in cfg['candidates']};records=[dict(condition=name,**threading(x,y,minimum)) for name,x,y in [('one_NI000001_stop_plus_nominal_free_.45_end',d['NI000001'],.45),('both_factory_NI000001_KU000016_stops',d['NI000001'],d['KU000016'])]]
 for f in (Path(__file__),spec,BASE/'cad/assembly_recipe_io.py',BASE/'cad/manufacturing_assembly.py'):hashes[str(f.relative_to(BASE))]=sha(f)
 result=dict(status='CONDITIONAL_ASSEMBLY_ORDER_NOT_INSTALLATION_APPROVAL',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes=hashes,distal_mesh_openings=openings,records=records,required_sequence=['Supplier one-end swaged NI000001 with other end un-terminated (quote/finished dimensions required)','Feed nominal free end through distal Eyelet toward Root,not terminal through closed ring','Route remaining closed guides and independently openable pulley/Root hardware','Attach reusable motor/drum termination ONLY after threading;actual termination design and test still REQUIRED','Measure seating/load/retention;unload before service'],actual_threading_trial=None,fabrication_ready=False,scope='Mesh-derived central flat-to-flat hole for6distalEyelets only,not minimum bore overwholepart/allguides. Nominalfreewire.45 isNOTmeasuredfrayed/cutenddiameter. Bothprefittedstops cannotthread theseclosedrings across catalogmaxrange;NOimaginarycompression/forcedsplit. No physicalassembly/strength/adhesive/drumtermination approval. Source manufacturer offersassembledends;notlooseDIYcrimpqualification.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],mesh_opening_min_mm=minimum,records=records),indent=2))
if __name__=='__main__':main()
