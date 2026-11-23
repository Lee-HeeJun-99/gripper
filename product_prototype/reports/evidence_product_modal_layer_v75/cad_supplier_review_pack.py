"""Publish already generated actual CAD review artifacts;NOT a fabrication release."""
import argparse,importlib.util,json,shutil,subprocess
from pathlib import Path
from manufacturing_assembly import BASE,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--name',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);draw=BASE/'drawings'/a.name;draw.mkdir(exist_ok=False)
 inputs=[BASE/'results/product_supplier_review865'/x for x in ('supplier_root_sections.png','supplier_root_sections.svg','instance_BOM.csv')]+[BASE/'meshes/b3_supplier_eyelet_seat_v43/full_assembly_recipe.json',BASE/'config/wire_bend_supplier_v40.json',BASE/'reports/SUPPLIER_BEND_AND_ROOT_REDESIGN_20261121.md']
 for source in inputs:shutil.copy2(source,draw/source.name)
 environment=dict(executables={x:shutil.which(x) for x in ('FreeCADCmd','freecadcmd')},python_modules={x:importlib.util.find_spec(x) is not None for x in ('FreeCAD','OCP','OCC','cadquery')})
 d=dict(status='CAD_REVIEW_PACK_NOT_FABRICATION_RELEASE',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),input_hashes={str(x.relative_to(BASE)):sha(x) for x in inputs},outputs={x.name:sha(x) for x in draw.iterdir() if x.is_file()},CAD_environment=environment,STEP_generated=False,fabrication_ready=False,scope='Actual saved sections/293instanceBOM/parametricrecipe/sourcefacts andfailure report copied asareviewpack. OnlyONE Rootunit updated;allotherundersizedturns,service,motion,retention/material/bond/physicalGates remainunqualified. NoSOFA execution orpurchases.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));(draw/'REVIEW_STATUS.json').write_text(json.dumps(d,indent=2));print(json.dumps(dict(status=d['status'],directory=str(draw),environment=environment),indent=2))
if __name__=='__main__':main()
