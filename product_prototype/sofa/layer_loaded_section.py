"""Loaded section contrast in the existing independent linear reference."""
import argparse,json,subprocess,sys
from pathlib import Path
from analyse import BASE,sha
from native_bending_coupon import guarded
from layer_section_reference import mesh
from layer_face_load import tip_load
from layer_bending_reference import reference
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--worker',action='store_true');a=p.parse_args();out=BASE/'results'/a.tag
 if not a.worker:
  out.mkdir(exist_ok=False)
  for name in ('layer_loaded_section.py','layer_section_reference.py','layer_face_load.py','layer_bending_reference.py'):(out/name).write_bytes((BASE/'sofa'/name).read_bytes())
  print(json.dumps(guarded([sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--worker'],out/'process',60)));return
 records=[]
 for dims in ((33,2,2),(33,5,2),(33,2,5),(33,5,5),(65,5,5)):
  q,t=mesh(*dims);F,A,_=tip_load(q,t,[0,0,-5e-5]);r=reference(q,t,F)
  records.append(dict(resolution=dims,tip_m=r['reference_tip_m'],energy_J=r['reference_energy_J'],shear_fraction=r['reference_tip_shear_energy_fraction'],volume_m3=r['volume_m3'],free_residual_N=r['reference_free_residual_N'],root_reaction_N=r['reference_root_reaction_N']))
 base=records[0]['tip_m']
 for r in records:r['relative_tip_difference_from_base']=abs(r['tip_m']-base)/max(abs(r['tip_m']),abs(base))
 d=dict(status='REFERENCE_SECTION_DIFFERENCES_NOT_CONVERGED',records=records,scope='Existing independent static CST algebra only,not Native execution. Consistent face traction,unchanged geometry,material,root;section and length contrasts separate. No assumption y-independent interpolation proves width-independent loaded solution.',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),physical_validation='NOT QUALIFIED');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
