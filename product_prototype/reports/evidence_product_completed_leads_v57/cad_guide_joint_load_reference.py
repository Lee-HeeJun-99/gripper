"""Conditional ideal two-leg guide load at CAD datum,not measured wire contact."""
import argparse,csv,json,subprocess,sys,time,itertools
from pathlib import Path
import numpy as np
from manufacturing_assembly import BASE,evaluate,sha

def point_wrench(point,neighbor_a,neighbor_b,datum,T_a,T_b):
 p,a,b,o=map(lambda x:np.asarray(x,dtype=float),(point,neighbor_a,neighbor_b,datum))
 if any(x.shape!=(3,) or not np.all(np.isfinite(x)) for x in (p,a,b,o)) or not np.all(np.isfinite([T_a,T_b])) or min(T_a,T_b)<0:raise ValueError('finite geometry and nonnegative tensions required')
 u=a-p;v=b-p
 if np.linalg.norm(u)==0 or np.linalg.norm(v)==0:raise ValueError('undefined zero-length leg')
 u/=np.linalg.norm(u);v/=np.linalg.norm(v);F=T_a*u+T_b*v;M=np.cross(p-o,F)/1000
 return F,M,u,v

def worker(a):
 out=BASE/'results'/a.tag;start=time.monotonic();src=BASE/'results/product_captive_nut941/full_assembly_recipe.json';routefile=BASE/'results/product_supplier_second_root886/route_mm.json';parts=json.loads(src.read_text())['parts'];lookup={p['name']:p for p in parts};route=np.asarray(json.loads(routefile.read_text()));point=evaluate(lookup['f0_c1_s0_eyelet']['shape']).center_mass;adj=evaluate(lookup['f0_c1_s1_eyelet']['shape']).center_mass;datum=evaluate(lookup['f0_c1_s0_rail_pressure_pad_RESEARCH']['shape']).center_mass
 gap=float(np.linalg.norm(point-route[0]))
 if gap>1e-10:raise ValueError('actualCADguide/Rootroute origin mismatch')
 rows=[]
 for Ta,Tb in itertools.product((.5,1.5,3.),repeat=2):
  F,M,u,v=point_wrench(point,adj,route[1],datum,Ta,Tb)
  force_residual=F-Ta*u-Tb*v;moment_residual=(np.cross(point,F)-Ta*np.cross(adj,u)-Tb*np.cross(route[1],v))/1000
  rows.append(dict(ASSUMED_incoming_tension_N=Ta,ASSUMED_outgoing_tension_N=Tb,force_N=F.tolist(),force_norm_N=float(np.linalg.norm(F)),moment_about_PAD_GEOMETRY_DATUM_Nm=M.tolist(),moment_norm_Nm=float(np.linalg.norm(M)),ideal_route_force_balance_residual_N=force_residual.tolist(),ideal_route_moment_balance_residual_Nm=moment_residual.tolist()))
 with (out/'conditional_guide_wrench.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['T_in_N','T_out_N','Fx_N','Fy_N','Fz_N','Mx_Nm','My_Nm','Mz_Nm']);w.writeheader()
  for r in rows:w.writerow(dict(zip(w.fieldnames,[r['ASSUMED_incoming_tension_N'],r['ASSUMED_outgoing_tension_N'],*r['force_N'],*r['moment_about_PAD_GEOMETRY_DATUM_Nm']])))
 result=dict(status='CONDITIONAL_IDEAL_GUIDE_LOAD_REFERENCE_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(f.relative_to(BASE)):sha(f) for f in (Path(__file__),src,routefile,BASE/'cad/manufacturing_assembly.py')},CAD_geometry_mm=dict(guide_geometric_centre=point.tolist(),next_guide_geometric_centre=adj.tolist(),next_Root_path_point=route[1].tolist(),pressure_pad_GEOMETRY_DATUM=datum.tolist()),guide_route_origin_gap_mm=gap,records=rows,runtime_s=time.monotonic()-start,actual_preload_N=None,actual_friction=None,actual_clamp_capacity_N=None,physical_tests_executed=0,fabrication_ready=False,scope='RESTCADonly,idealtautmasslesstwoleg point application atboregeometriccentre. Incoming/outgoingtensions INDEPENDENTresearchinputs,notactualmotorrating/equalizer/frictionlaw. Padcentroid isREFERENCEdatum,NOT measuredpressurecentre/contactarea. Distributedbore/frictioncouple,wirebending,hardwareweight/contact/slip/preload/compliance omitted. Routeforce/momentidentity isNOT actualSOFA/jointcapacity/holdingapproval. Use only toplaninstrumentloads,not assignmaterialstrength.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],origin_gap_mm=gap,max_conditional_force_N=max(r['force_norm_N'] for r in rows),max_conditional_moment_Nm=max(r['moment_norm_Nm'] for r in rows)),indent=2))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--worker',action='store_true');a=p.parse_args()
 if Path(a.tag).name!=a.tag:p.error('local tag required')
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--worker'];proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_GUIDE_LOAD_REFERENCE_CHILD',process=proc),indent=2))
 print((out/'summary.json').read_text())
if __name__=='__main__':main()
