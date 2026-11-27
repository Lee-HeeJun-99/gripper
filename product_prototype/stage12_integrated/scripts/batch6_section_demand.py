"""Actual AO net-section demand; conditional section equilibrium, not notch capacity."""
import json,sys,shutil,math
import numpy as np
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.BRepCheck import BRepCheck_Analyzer

def main():
 assert not (ROOT/'runtime/STOP').exists()
 out=ROOT/'validation/finger/batch6_section_demand1';out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
 src=ROOT/'cad/exports/revAO_root2/summary.json';d=json.loads(src.read_text());load=ROOT/'validation/finger/batch6_actual_specimen3/summary.json';w=json.loads(load.read_text())
 refs={n:d['part_references'][n] for n in ['F0_RAIL_L','F0_RAIL_R']}
 deps=[ROOT/'scripts/baseline_registry.py',S1/'scripts/incremental_stage1.py',S1/'scripts/build_stage1.py']
 dump(out/'inputs.json',dict(candidate=ref(src),load=ref(load),parts=refs,dependencies=[ref(p) for p in deps],producer=ref(out/'producer.py'),limits=dict(section_relative=1e-4,refinement_relative=1e-4,balance_absolute=1e-10),contract='AO original only. Diagnostic1mN REST wrench. Equal symmetric Rail sharing,plane sections,linear stress. Root-hole section is explicit no-clamp-transfer counterfactual,NOT actual internal force in clamped zone. No notch stress,allowable,material rating or demand bound.'))
 assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values())
 rows=[]
 for name,r in refs.items():
  s=read(REPO/r['path']);assert BRepCheck_Analyzer(s).IsValid()
  for z in [-8.,1.]:
   for h in [.08,.04,.02,.01]:
    assert not (ROOT/'runtime/STOP').exists()
    slab=BRepAlgoAPI_Common(s,box(40,-30,z-h/2,20,60,h)).Shape();g=GProp_GProps();BRepGProp.VolumeProperties_s(slab,g,1e-11)
    m=g.MatrixOfInertia();a=g.Mass()/h
    # Tensor identity removes z and y variance even for variable-width hole slabs.
    iy=(m.Value(2,2)+m.Value(3,3)-m.Value(1,1))/(2*h)
    rows.append(dict(part=name,z_mm=z,h_mm=h,A_mm2=a,Iyy_mm4=iy,cx_mm=g.CentreOfMass().X()))
 F,M,N=w['equivalent_tip_wrench_N_Nmm'];stations=[]
 for z in [-84.,-46.,-8.,-7.,1.]:
  width=3. if z!=1 else .9;A=2*.2*width;I=2*width*.2**3/12
  moment=M+F*(z-w['cut_tip_z_mm']);sig=[N/A-moment*.1/I,N/A+moment*.1/I]
  stations.append(dict(z_mm=z,N_N=N,M_Nmm=moment,A_mm2=A,Iyy_mm4=I,sigma_faces_MPa=sig,max_abs_sigma_MPa=max(map(abs,sig)),scope='unloaded-clamp-transfer counterfactual' if z==1 else 'free-span reference' ))
 checks=dict(finite=all(math.isfinite(r[k]) for r in rows for k in ['A_mm2','Iyy_mm4','cx_mm']),positive=all(r['A_mm2']>0 and r['Iyy_mm4']>0 for r in rows))
 finest=[r for r in rows if r['h_mm']==.01]
 err=max(max(abs(r['A_mm2']/(.18 if r['z_mm']==1 else .6)-1),abs(r['Iyy_mm4']/(.0006 if r['z_mm']==1 else .002)-1)) for r in finest)
 checks['finest_point_section']=err<1e-4
 differences=[]
 for name in refs:
  for z in [-8.,1.]:
   rr=[r for r in rows if r['part']==name and r['z_mm']==z];differences += [abs(a['A_mm2']/rr[-1]['A_mm2']-1) for a in rr]
 # coarse->fine error recorded, not suppressed by adjacent-only comparisons
 checks['all_base_to_finest_sections']=max(differences)<.0001
 dump(out/'summary.json',dict(status='CONDITIONAL_AO_NET_SECTION_DEMAND_VERIFIED' if all(checks.values()) else 'SECTION_DEMAND_FAIL',revision='revAO_root2',producer=ref(out/'producer.py'),inputs=ref(out/'inputs.json'),checks=checks,sections=rows,stations=stations,finest_point_section_relative_error=err,base_to_finest_area_relative_errors=differences,diagnostic_tension_N=.001,actual_demand_N=None,allowable_MPa=None,actual_capacity_qualified=False,whole_system_release=False,scope='Actual AO CAD-derived nominal net sections and conditional demand only',limitations=['No actual clamp load transfer; root-hole moment continuation is counterfactual','Nominal section stress is not notch peak, pin contact, buckling or strength','No tolerance distribution/minimum material/rated components or complete system load bound','AO current and AA adopted unchanged; AX wider root not combined']))
 print(json.dumps(dict(checks=checks,err=err,stations=stations)));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
