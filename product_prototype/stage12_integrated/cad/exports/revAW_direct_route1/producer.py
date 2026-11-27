"""Finite idler-removal counterfactual on actual AO/AV parts; no powered motion."""
import json,math,shutil,sys
import numpy as np
from baseline_registry import ROOT,REPO,S1,ref,dump,sha
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,cyl,rotate,export,common,bounds,overlap,volume,solid_count
from OCP.gp import gp_Pnt,gp_Dir,gp_Ax2,gp_Trsf
from OCP.BRepPrimAPI import BRepPrimAPI_MakeTorus
from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepCheck import BRepCheck_Analyzer

def Ry(a):
    c,s=math.cos(a),math.sin(a);return np.array([[c,0,s],[0,1,0],[-s,0,c]])
def pose(deg):
    a=math.radians(deg);base=np.array([50.,0,-100]);r=Ry(a)
    end=base if not a else np.array([50-88/a*(1-math.cos(a))-5*math.sin(a),0,-7-88/a*math.sin(a)-5*math.cos(a)])
    shift=end-r@base;P=r@np.array([43.,0,-92])+shift
    C=np.array([110.,0,20]);u=(P-C)/np.linalg.norm(P-C);k=11.25/np.linalg.norm(P-C)
    # Upper/left tangent, continuous with an increasing drum wrap.
    v=np.array([u[2],0,-u[0]]);n=k*u+math.sqrt(1-k*k)*v
    Q=C+11.25*n;t=(Q-P)/np.linalg.norm(Q-P);E=P+16*t
    phi=math.atan2(n[2],n[0]);b=math.atan2(t[0],t[2])
    free=11.25*(phi+math.pi/2)+np.linalg.norm(Q-E)
    return dict(P=P,Q=Q,E=E,t=t,b=b,phi=phi,free=free,r=r,shift=shift)
def tr(s,r,d):
    m=np.column_stack((r,d));t=gp_Trsf();t.SetValues(*map(float,m.ravel()));return BRepBuilderAPI_Transform(s,t,True).Shape()
def main():
    assert not (ROOT/'runtime/STOP').exists()
    out=ROOT/'cad/exports/revAW_direct_route1';out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    ao=ROOT/'cad/exports/revAO_root2/summary.json';av=ROOT/'cad/exports/revAV_micro_interface1/summary.json'
    a=json.loads(ao.read_text());v=json.loads(av.read_text());replaced=set(v['context_replacement_IDs'])
    removed=[n for n in a['part_references'] if 'IDLER' in n]
    refs={n:r for n,r in a['part_references'].items() if n not in replaced and n not in removed and not n.endswith('TENDON_WIRE')};refs.update(v['part_references'])
    assert all(sha(REPO[r['path']])==r['SHA256'] for r in refs.values())
    dump(out/'inputs.json',dict(producer=ref(out/'producer.py'),AO=ref(ao),AV=ref(av),contract=ref(ROOT/'models/standard_drive/batch6_contract1.json'),parts=refs,removed_idler_IDs=removed,exact_intersection_mm3_max=1e-8,poses_deg=[0,15,30,45,60],wire_diameter_mm=.5,limitations='Nominal rigid hardware only; no flexible PET/Rail geometry, no CCD, no capacity. Terminal swivel redirects to drum; seating/limits not qualified. AV motor not accepted for operation.'))
    shapes={n:read(REPO[r['path']]) for n,r in refs.items()};rows=[];hits=[];pairs=0;g0=pose(0)
    oldb=-(math.atan2(117,1)-math.acos(11.25/math.hypot(117,1)))
    for deg in (0,15,30,45,60):
        assert not (ROOT/'runtime/STOP').exists()
        g=pose(deg);eta=(g0['free']-g['free'])/11.25;start=-math.pi/2-eta;assert 0<g['phi']-start<2*math.pi
        ax=gp_Ax2(gp_Pnt(110,0,20),gp_Dir(0,-1,0),gp_Dir(math.cos(start),0,math.sin(start)))
        arc=BRepPrimAPI_MakeTorus(ax,11.25,.25,g['phi']-start).Shape();d=g['E']-g['Q'];lead=cyl(.25,tuple(g['Q']),float(np.linalg.norm(d)),tuple(d/np.linalg.norm(d)))
        f=BRepAlgoAPI_Fuse(arc,lead);f.SetFuzzyValue(1e-7);f.Build();assert f.IsDone();wire=f.Shape()
        assert BRepCheck_Analyzer(wire).IsValid() and solid_count(wire)==1
        assert abs(volume(wire)/(math.pi*.25**2*g0['free'])-1)<1e-6
        targets={}
        for n,s in shapes.items():
            if n.endswith(('SKIN','RAIL_L','RAIL_R')):continue
            if n.startswith(('F0_','F1_','F2_')):
                sec=int(n[1]);suffix=n[3:];local=rotate(s,-120*sec)
                if suffix.startswith(('SWIVEL_LOWER','SWIVEL_UPPER','SWIVEL_BOLT','SWIVEL_NUT','TIP_FACTORY_NIPPLE')):
                    rr=Ry(g['b']-oldb);local=tr(local,rr,g['P']-rr@np.array([43.,0,-92]))
                elif 'TERMINAL' in suffix or suffix.startswith(('SWIVEL_AXLE','SWIVEL_SLEEVE','SWIVEL_SPACER_')):local=tr(local,g['r'],g['shift'])
                # AV spool is axisymmetric in the wire plane, but bolt holes rotate.
                elif suffix.startswith(('SPOOL','STOCK_HUB','SET_SCREW')):local=tr(local,Ry(eta),np.array([110.,0,20])-Ry(eta)@np.array([110.,0,20]))
                s=rotate(local,120*sec)
            targets[n]=s
        for sec in range(3):
            n=f'F{sec}_DIRECT_WIRE_{deg}';w=rotate(wire,120*sec);export(w,out/n);bb=bounds(w)
            for m,s in targets.items():
                if overlap(bb,bounds(s)):
                    pairs+=1;vol=common(w,s)
                    if vol>1e-8:hits.append(dict(pose_deg=deg,wire=n,part=m,common_mm3=vol))
            rows.append(dict(part_ID=n,pose_deg=deg,sector=sec,STEP=ref(out/(n+'.step')),STL=ref(out/(n+'.stl')),volume_mm3=volume(w),length_mm=g0['free'],rotor_angle_rad=eta,swivel_angle_rad=g['b'],P_mm=g['P'].tolist(),Q_mm=g['Q'].tolist(),E_mm=g['E'].tolist(),tangent_dot_mm=float(np.dot(g['Q']-np.array([110,0,20]),g['Q']-g['E'])),free_reference_mm=float(g['free'])))
    dump(out/'BOM_delta.json',dict(scope='REJECTABLE ROUTE SPECIMEN, not whole product BOM',removed_if_adopted=removed,replaced_wires=[f'F{i}_TENDON_WIRE' for i in range(3)],new_parts=[r['part_ID'] for r in rows if r['pose_deg']==0],custom_process_removed_if_accepted='All Idler axle retention including special pin/rivet forming; no new part beyond rerouted purchased cable',adopted=False))
    dump(out/'summary.json',dict(status='DIRECT_ROUTE_INTERFERENCE_FAIL' if hits else 'DIRECT_ROUTE_RIGID_SCREEN_PASS',scope='Finite nominal direct tendon removal specimen against actual retained AO and AV rigid parts at five prescribed poses; not actual equilibrium or Stage3',inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),BOM_delta=ref(out/'BOM_delta.json'),rows=rows,hits=hits,exact_pairs=pairs,removed_idler_count=len(removed),stroke_0_to_60_mm=float(g0['free']-pose(60)['free']),whole_system_release=False,adopted=False,capacity_qualified=False))
    print(json.dumps(dict(hits=hits,pairs=pairs,removed_idler_count=len(removed)),indent=2));raise SystemExit(2 if hits else 0)
if __name__=='__main__':main()
