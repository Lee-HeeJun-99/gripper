import sys,json,shutil
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'product_prototype/stage12_integrated/scripts'))
import numpy as np
from baseline_registry import ROOT,REPO,ref,dump,S1
from verify_primary_finger_v3 import sectors
from primary_module_design import tr,Ry
from incremental_stage1 import read,bounds,box,volume
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
out=ROOT/'validation/finger/primaryP1_overlap_witness1';out.mkdir();shutil.copyfile(__file__,out/'producer.py');src=ROOT/'validation/finger/primaryP1_operating2/cases.json';row=next(r for r in json.loads(src.read_text()) if r['n']==32 and r['T_N']==1);s=sectors(row)[30];a=row['rail_angles_rad'][-1];R=Ry(a);end=np.array([row['rail_tip_m'][0]*1000,0,row['rail_tip_m'][1]*1000]);shift=end-R@np.array([50.4,0,-84]);local=tr(s,R.T,-R.T@shift);cad=json.loads((ROOT/'cad/exports/primaryP1_open9/summary.json').read_text());f=REPO/cad['part_references']['F0_TERMINAL_FRONT']['path'];front=read(f);inter=BRepAlgoAPI_Common(local,front).Shape();g=GProp_GProps();BRepGProp.VolumeProperties_s(inter,g,1e-11)
rows=[]
# Clip same-sector witness to constant minimum physical half-width; lower bound.
lo,hi=30*.0862/32,31*.0862/32
for kind,w in [('outer',12-.06*(7+lo*1000)),('inner',12-.06*(7+hi*1000))]:
 clip=BRepAlgoAPI_Common(local,box(-200,-w,-200,400,2*w,400)).Shape();q=BRepAlgoAPI_Common(clip,front).Shape();rows.append(dict(kind=kind,halfwidth_mm=w,overlap_mm3=volume(q),bounds_mm=bounds(q)))
dump(out/'summary.json',dict(status='ACTUAL_P1_LOADED_OVERLAP_WITNESS',source=ref(src),front=ref(f),segment=30,n=32,tendon_N=1,common_mm3=volume(inter),bounds_mm=bounds(inter),centroid_mm=[g.CentreOfMass().X(),g.CentreOfMass().Y(),g.CentreOfMass().Z()],width_bounds=rows,scope='Exact finite arc sector and true Terminal, outer/inner tapered-width bounds, no state acceptance or strength',whole_system_release=False));print((out/'summary.json').read_text())
