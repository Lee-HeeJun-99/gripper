"""Independent Gmsh OCC reimport of every actual P1 part and mass-wrench sum."""
import json,shutil
import numpy as np
import gmsh
from baseline_registry import ROOT,REPO,ref,sha,dump

def main():
 out=ROOT/'validation/integrated/primaryP1_full_mass_verify1';out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');assert not(ROOT/'runtime/STOP').exists();src=ROOT/'validation/integrated/primaryP1_full_mass1/summary.json';d=json.loads(src.read_text());gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);rows=[];W=np.zeros(6);m=0
 for r in d['parts']:
  gmsh.model.add(r['part_ID']);assert sha(REPO/r['STEP']['path'])==r['STEP']['SHA256'];v=gmsh.model.occ.importShapes(str(REPO/r['STEP']['path']));assert len(v)==1;vol=gmsh.model.occ.getMass(*v[0]);c=np.array(gmsh.model.occ.getCenterOfMass(*v[0]));mass=(.0095 if r['part_ID']=='F0_MICRO_MOTOR' else .0028) if r['density_assumed_kg_m3'] is None else vol*1e-9*r['density_assumed_kg_m3'];f=np.array([0,0,-mass*9.80665]);w=np.r_[f,np.cross(c*.001,f)];W+=w;m+=mass;rows.append(dict(part_ID=r['part_ID'],volume_relative=abs(vol/r['volume_mm3']-1),centroid_max_error_mm=float(np.max(abs(c-r['centroid_mm']))),mass_error_kg=abs(mass-r['mass_kg']),wrench_max_error=float(np.max(abs(w-r['gravity_wrench_N_Nm'])))));gmsh.model.remove()
 gmsh.finalize();grip=-W-np.array(d['operating_external_port_N_Nm']);checks=dict(all78_reimported=len(rows)==78,volume=all(r['volume_relative']<1e-8 for r in rows),centroid=all(r['centroid_max_error_mm']<1e-6 for r in rows),mass=abs(m-d['total_conditional_mass_kg'])<1e-10,full_wrench=np.max(abs(grip-d['required_external_base_grip_full_wrench_N_Nm']))<1e-9)
 dump(out/'summary.json',dict(status='ACTUAL78PART_CONDITIONAL_MASS_INDEPENDENT_REIMPORT_PASS' if all(checks.values()) else 'ACTUAL78PART_MASS_REIMPORT_FAIL',source=ref(src),candidate=d['candidate'],verifier=ref(out/'verifier.py'),checks={k:bool(v) for k,v in checks.items()},rows=rows,independent_mass_kg=m,required_external_grip_N_Nm=grip.tolist(),newly_qualified_system_gate_ids=[],whole_system_release=False,scope='Independent API reimport/volume/centroid/mass/wrench arithmetic only; same underlyingOCCT family,not an independent geometry engine. Density/COM envelope assumptions are not verified physical measurements.'));print(json.dumps(dict(checks={k:bool(v) for k,v in checks.items()},mass_kg=m,grip_N_Nm=grip.tolist())));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
