"""Actual drum BRep against a taut, zero-bending-stiffness wire envelope.
Full torus is a conservative superset of any seated wrap arc; NOT dynamics.
"""
import argparse,json,math,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/'stage1_manufacturing/scripts'))
from incremental_stage1 import read,sha,common,cyl
from OCP.BRepPrimAPI import BRepPrimAPI_MakeTorus
from OCP.gp import gp_Ax2,gp_Pnt,gp_Dir
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'validation/tendon'/a.tag;out.mkdir(parents=True,exist_ok=False)
    source=ROOT.parent/'stage1_manufacturing/cad/parts/revAA_mbd1'
    names=['F0_DRUM','F0_DRUM_NIPPLE_CAP','F0_DRUM_PIN','F0_DRUM_PIN_PLUG_L','F0_DRUM_PIN_PLUG_R']
    shapes={n:read(source/(n+'.step')) for n in names};rows=[]
    for diameter in (.48,.50,.52):
        rwire=diameter/2;rcentre=10.93+rwire;ra=11.25
        alpha=math.acos(rcentre/ra)
        p0=np.array([80.,0,20-ra]);p1=np.array([80+rcentre*math.sin(alpha),0,20-rcentre*math.cos(alpha)])
        direction=p1-p0
        tangent=cyl(rwire,p0.tolist(),float(np.linalg.norm(direction)),direction.tolist())
        torus=BRepPrimAPI_MakeTorus(gp_Ax2(gp_Pnt(80,0,20),gp_Dir(0,1,0)),rcentre,rwire).Shape()
        for label,wire in [('full_seated_circle_superset',torus),('anchor_to_floor_tangent',tangent)]:
            for name,s in shapes.items():
                v=common(wire,s)
                rows.append(dict(wire_diameter_mm=diameter,seated_radius_mm=rcentre,
                    initial_tangent_deflection_deg=math.degrees(alpha),wire_region=label,part=name,signed_common_mm3=v,
                    status='PASS' if abs(v)<1e-8 else 'FAIL'))
    result=dict(status='PASS' if all(r['status']=='PASS' for r in rows) else 'FAIL',
        scope='NOMINAL DRUM TAUT-SEATING LIMIT GEOMETRY ONLY',rows=rows,
        source_SHA256=sha(Path(__file__)),STEP_SHA256={n:sha(source/(n+'.step')) for n in names},
        exclusions=['actual wire bending stiffness/strain','factory swage internals','contact force','tracking under axial play','fatigue','actual entry transition curvature','idler-to-Finger route'],
        command='PYTHONPATH=/tmp/regrip_stage1_ocp python scripts/seated_wire.py --tag '+a.tag)
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
