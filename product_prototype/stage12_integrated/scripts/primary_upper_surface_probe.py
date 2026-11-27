import json,sys,gmsh,shutil
from baseline_registry import ROOT,REPO,ref,dump
out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');src=ROOT/'cad/exports/primaryP1_interfaces18/summary.json';d=json.loads(src.read_text());gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);v=gmsh.model.occ.importShapes(str(REPO/d['part_references']['F0_ROOT_BACK']['path']));gmsh.model.occ.synchronize();rows=[]
for _,t in gmsh.model.getBoundary(v,oriented=False):rows.append(dict(tag=t,bounds=gmsh.model.getBoundingBox(2,t),area=gmsh.model.occ.getMass(2,t),COM=gmsh.model.occ.getCenterOfMass(2,t)))
gmsh.finalize();dump(out/'summary.json',dict(status='ACTUAL_ROOT_SURFACE_INVENTORY_NOT_RELEASE',candidate=ref(src),producer=ref(out/'producer.py'),faces=rows));print(json.dumps(rows))
