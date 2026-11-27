"""Independent 78-part mass coverage: reject double-counted motor in Root port.
CAD material sensitivities remain conditional; not physical mass certification.
"""
import sys,json,shutil,collections
import numpy as np
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

def W(q,f):return np.r_[f,np.cross(q,f)]
def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');assert not(ROOT/'runtime/STOP').exists();src=ROOT/'cad/exports/primaryP1_seated22/summary.json';cad=json.loads(src.read_text());parts=[];nom={}
 for n,r in cad['part_references'].items():
  assert sha(REPO/r['path'])==r['SHA256'];g=GProp_GProps();BRepGProp.VolumeProperties_s(read(REPO/r['path']),g);c=g.CentreOfMass();rho=1400 if n=='F0_SKIN' else 2700 if n in ('OPEN_FRAME','MOTOR_CAP','TEST_BASE','F0_SPOOL','F0_DRUM_NIPPLE_CAP') else 7900;m=.0095 if n=='F0_MICRO_MOTOR' else .0028 if n=='F0_STOCK_HUB' else g.Mass()*rho*1e-9;nom[n]=m;parts.append(dict(part_ID=n,STEP=r,volume_mm3=g.Mass(),centroid_m=[c.X()*.001,c.Y()*.001,c.Z()*.001],mass_kg=m,density_assumed_kg_m3=None if n in ('F0_MICRO_MOTOR','F0_STOCK_HUB') else rho))
 dump(out/'actual_CAD_mass.json',dict(parts=parts,total_conditional_mass_kg=sum(nom.values()),candidate=ref(src)))
 rows=[]
 for tag in sys.argv[2:]:
  ss=ROOT/'validation/integrated'/tag/'summary.json';summary=json.loads(ss.read_text());state=json.loads((REPO/summary['state']['path']).read_text());string=state['string'];rep=state['moving_mass_points']+state['fixed_mass_points']+string['rotors'];summed=collections.defaultdict(float)
  for q in rep:summed[q['part_ID']]+=q['mass_kg']
  summed['F0_MICRO_MOTOR']+=.0095;summed['F0_TENDON_WIRE']+=nom['F0_TENDON_WIRE']
  passive=[]
  for q in parts:
   if q['part_ID'] not in summed:passive.append(q);summed[q['part_ID']]=q['mass_kg']
  # Passive set may ONLY contain the actual five elastic bodies and axial hardware.
  allowed={'OPEN_FRAME','F0_ROOT_BACK','MOTOR_CAP','GROUND_PLATE','TEST_BASE'}|{f'F0_RF{i}_{k}' for i in range(2) for k in ('BOLT','NUT')}|{f'MOTOR_CAP_{k}_{x}_{y}' for x in (-7,7) for y in (-29.5,-13.5) for k in ('BOLT','NUT')}|{f'{p}_{k}_{i}' for p in ('GROUND','FIXTURE') for k in ('BOLT','NUT') for i in range(4)}
  diffs={n:summed[n]-m for n,m in nom.items()};gravity=np.array([0,0,-9.80665]);passiveW=sum((W(np.array(q['centroid_m']),q['mass_kg']*gravity) for q in passive),np.zeros(6));base=-(np.array(state['Root_origin_wrench_N_Nm'])+np.array(state['Motor_origin_wrench_N_Nm'])+passiveW);totalmass=sum(summed.values());massforce=base[2]-sum(nom.values())*9.80665
  check=dict(all78unique=set(summed)==set(nom),passive_exact=set(q['part_ID'] for q in passive)==allowed,part_mass=all(abs(d)<1e-10 for d in diffs.values()),total_mass=abs(totalmass-sum(nom.values()))<1e-10,total_Z_force=abs(massforce)<1e-8)
  check={k:bool(v) for k,v in check.items()}
  rows.append(dict(source=ref(ss),checks=check,per_part_mass_error_kg=diffs,represented_mass_kg=totalmass,actual_CAD_mass_kg=sum(nom.values()),required_Base_external_wrench_N_Nm=base.tolist(),base_Z_gravity_error_N=float(massforce),passive_parts=[q['part_ID'] for q in passive],passive_gravity_wrench_N_Nm=passiveW.tolist()))
 ok=all(rows[-1]['checks'].values());negative=not all(rows[0]['checks'].values()) if len(rows)>1 else None
 result=dict(status='ACTUAL_P1_LOAD_COVERAGE_VERIFY_PASS' if ok and negative is not False else 'ACTUAL_P1_LOAD_COVERAGE_VERIFY_FAIL',candidate=ref(src),verifier=ref(out/'verifier.py'),mass_ledger=ref(out/'actual_CAD_mass.json'),rows=rows,double_motor_original_rejected=negative,checks=dict(corrected_coverage=ok,double_motor_rejected=negative),newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['ExactCADmasswithconditionaldensitiesandnominalmanufacturerMotor/Hubmass,notphysicalbounds/COMinertia.','Basewrenchisnecessaryglobalbalance,notphysicalanchororstrength. Passivebody/hardwareweightpositionsarenominalCADnotnewelasticfieldpositions.']);dump(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k!='rows'}));print([(r['source'],r['checks'],r['represented_mass_kg'],r['base_Z_gravity_error_N']) for r in rows]);raise SystemExit(0 if ok and negative is not False else 2)
if __name__=='__main__':main()
