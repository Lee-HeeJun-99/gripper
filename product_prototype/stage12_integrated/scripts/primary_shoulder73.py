"""Same P1, actual positive keeper shoulder on existing Root boss.
Retains split-pin as capture hardware; broad seating replaces unsupported
pin-only gravity moment path. Nominal geometry, not toleranced/strength release.
"""
import sys,json,shutil,itertools
import numpy as np
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,fuse,canonical,translate,export,bounds,common,overlap,volume,solid_count
from build_stage1 import compound
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from scipy.optimize import linprog

def main():
 out=ROOT/'cad/exports'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_ground65a/summary.json';old=json.loads(cp.read_text());refs=dict(old['part_references']);assert all(sha(REPO/r['path'])==r['SHA256'] for r in [*refs.values(),old['assembly'],old['BOM']]);parts={n:read(REPO/r['path']) for n,r in refs.items()};n='ROOT_SOCKET_KEEPER';source=parts[n]
 flange=box(57.15,-1.85,-.975,5.7,3.7,3.175);new=translate(canonical(fuse(source,flange)),0,0,-.025);export(new,out/n);parts[n]=read(out/(n+'.step'));refs[n]=ref(out/(n+'.step'));bb={n:bounds(s) for n,s in parts.items()};pairs=[]
 for m,s in parts.items():
  assert not(ROOT/'runtime/STOP').exists()
  if m!=n and overlap(bb[n],bb[m]):pairs.append(dict(pair=[n,m],intersection_mm3=common(parts[n],s)))
 hits=[p for p in pairs if p['intersection_mm3']>1e-8];w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
 bom=json.loads((REPO/old['BOM']['path']).read_text());bom['revision']=out.name;row=next(r for r in bom['parts'] if r['part_ID']==n);row.update(STEP=refs[n],interface='Positive broad keeper shoulder rests on actual Root boss top z=-1; transverse splitpin remains capture, two sockets retained. Nominal seating -.025mm; all source/material/process/strength/convergence gates unqualified.')
 dump(out/'BOM.json',bom)
 g=GProp_GProps();BRepGProp.VolumeProperties_s(parts[n],g);c=g.CentreOfMass();cg=np.array([c.X(),c.Y(),c.Z()]);mass=g.Mass()*7.9e-6;weight=mass*9.80665
 # Actual planar support polygon: flange rectangle minus Root slot rectangle.
 # Vertices carried through full six-resultant normal-contact feasibility.
 pts=np.array([[x,y,-1.] for x in [57.15,58.95,61.05,62.85] for y in [-1.85,-1.05,1.05,1.85] if not(58.95<x<61.05 and -1.05<y<1.05)])
 A=np.array([np.r_[0,0,1,y,-x,0] for x,y,z in pts]).T;load=np.r_[0,0,-weight,np.cross(cg,np.array([0,0,-weight]))];lp=linprog(np.ones(len(pts)),A_eq=A,b_eq=-load,bounds=(0,None),method='highs');checks=dict(valid=bool(BRepCheck_Analyzer(parts[n]).IsValid()),one_solid=solid_count(parts[n])==1,all83hashes=True,whole_assembly_changed_pair_clear=not hits,actual_gravity_contact_cone=bool(lp.success));local=dict(assumed_density_kg_mm3=7.9e-6,keeper_volume_mm3=g.Mass(),keeper_centroid_mm=cg.tolist(),keeper_mass_ASSUMED_kg=mass,keeper_weight_ASSUMED_N=weight,support_points_mm=pts.tolist(),support_polyhedron='Actual flange outerrectangle57.15..62.85 x+-1.85 minus actual Root slot opening58.95..61.05 x+-1.05. All supportpoints lie on remaining material.',external_keeper_wrench_N_Nmm=load.tolist(),six_row_normal_cone_feasible=bool(lp.success),only_gravity_load=True)
 if lp.success:local.update(point_normal_forces_N=lp.x.tolist(),all6_residual=(A@lp.x+load).tolist(),maximum_original_residual=float(abs(A@lp.x+load).max()))
 dump(out/'shoulder_gravity_reference.json',local)
 d=dict(old);d.update(revision=out.name,parent=ref(cp),producer=ref(out/'producer.py'),part_references=refs,part_bounds_mm=bb,parts=83,assembly=ref(out/'ASSEMBLY.step'),BOM=ref(out/'BOM.json'),changed=[dict(part_ID=n,STEP=refs[n],STL=ref(out/(n+'.stl')),valid=checks['valid'],solids=solid_count(parts[n]),volume_mm3=volume(parts[n]),bounds_mm=bb[n])],unchanged_part_STEP_count=82,changed_CAD_files=[ref(out/(n+'.step')),ref(out/(n+'.stl'))],checks=checks,interferences=hits,changed_pair_queries=pairs,shoulder_gravity_reference=ref(out/'shoulder_gravity_reference.json'),status='SAME_P1_POSITIVE_KEEPER_SHOULDER_CAD_GRAVITY_REFERENCE' if all(checks.values()) else 'SAME_P1_POSITIVE_KEEPER_SHOULDER_DESIGN_FAIL',design_change='Same83part P1, fuse finite broad flange into actual Root keeper, nominally seat-.025mm on existing Root boss. Keep original transverse splitpin/sockets/bolts/83parts and Motor->Drum->Tendon->Finger->Root->Ground. No unrelatedcoupon.',newly_qualified_system_gate_ids=[],accepted83body_physical_equilibria=0,whole_system_release=False,capacity_qualified=False,limitations=['Positive nominalgravity support only; all83body equilibrium, pin/host/bolt/nut/thread/preload, friction, loads and elastic pressure remain unsolved.','No strength/minimum/certifieddensity/tolerance/assembly/mesh/time/globalenergy/systemPASS. Shoulder changes keeper and requires changedStage1 revalidation.','Source ratings, original criteria and full3Finger/cartridge/distalPETslide/jamming extensions retained.']))
 dump(out/'summary.json',d);print(json.dumps(dict(checks=checks,hits=hits,gravity=local)));return 0 if all(checks.values()) else 2
if __name__=='__main__':sys.exit(main())
