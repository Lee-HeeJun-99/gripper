"""Actual front collet geometry -> necessary coupled friction demand.
No bolt-preload-to-contact-force law, friction value or actual capacity guessed.
"""
import argparse,ast,json,math,shutil,sys
from baseline_registry import ROOT,S1,REPO,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read
from fastener_joint_contract import cylinders,project_interval
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--candidate',default='revAJ_idler1');a=p.parse_args()
    out=ROOT/'validation/transmission'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    specfile=S1/'scripts/sourced_motor_stage1.py';tree=ast.parse(specfile.read_text())
    expr=next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='MOTOR_SPEC' for t in n.targets))
    assert isinstance(expr,ast.Call) and isinstance(expr.func,ast.Name) and expr.func.id=='dict' and not expr.args
    spec={k.arg:ast.literal_eval(k.value) for k in expr.keywords}
    src=ROOT/'cad/exports'/a.candidate/'summary.json';d=json.loads(src.read_text());drive=src if d.get('integrated_motor_support') else REPO/d['drive_definition']['path'];dd=json.loads(drive.read_text())
    part=d['part_references']['F0_CLUTCH_INPUT_HUB'];s=read(REPO/part['path']);bores=[project_interval(c,[0,1,0]) for c in cylinders(s) if abs(c['r']-2.52)<1e-6];assert bores
    start=min(v[0] for v in bores);end=max(v[1] for v in bores)
    # Actual relocated motor flange=-14mm. Supplier shaft length23..25mm.
    flange=dd.get('motor_flange_Y_mm',-14);shaft_tip=[flange+x for x in spec['shaft_length_mm']];grip=[min(x,end)-start for x in shaft_tip]
    rmax=spec['shaft_diameter_mm'][1]/2000
    rmin=(spec['D_flat_across_mm'][0]-spec['shaft_diameter_mm'][1]/2)/1000
    face=d['torque_model'];radius=face['nominal_drum_wire_radius_mm']/1000;face_r=[face['annulus_inner_mm']/1000,face['annulus_outer_mm']/1000]
    demand=dict(pure_torque_muNs_per_N_tendon=[radius/rmax,radius/rmin],face_muN_per_N_tendon=[radius/face_r[1],radius/face_r[0]])
    gaps=[5.04-x for x in reversed(spec['shaft_diameter_mm'])];perimeter=[math.pi*x for x in gaps]
    expected=d.get('actual_shaft_grip_range_mm',[4.2,6.2]);assert max(abs(v-w) for v,w in zip(grip,expected))<1e-6 and abs(demand['pure_torque_muNs_per_N_tendon'][0]-4.5)<1e-12
    # A dimensionless mathematical control, NOT an assigned material mu.
    def bound(T,mu_face,r):return math.hypot(T*radius/r,T*radius/(mu_face*face_r[0]))
    assert abs(bound(2,1,rmin)-2*bound(1,1,rmin))<1e-12
    assert bound(1,1,rmin)>bound(1,2,rmin)>1*radius/rmin
    result=dict(status='COLLET_REQUIREMENT_GEOMETRY_PASS_CAPACITY_UNQUALIFIED',scope='Actual CAD bore/grip and normalized torque+axial reaction requirements only',candidate=ref(src),input_hub=part,drive_definition=ref(drive),motor_specification=ref(specfile),producer=ref(out/'producer.py'),
        actual_bore_Y_mm=[start,end],shaft_tip_Y_mm=shaft_tip,actual_engagement_mm=grip,clamp_bolt_Y_mm=dd['clamp_bolt_Y_mm'],clamp_bolt_ahead_of_shaft_tip_mm=[dd['clamp_bolt_Y_mm']-v for v in shaft_tip],
        minimum_contact_radius_bound_m=rmin,maximum_contact_radius_bound_m=rmax,unit_tendon_requirements=demand,diametral_gap_mm=gaps,uniform_bore_perimeter_contraction_mm=perimeter,
        coupled_law='mu_shaft*N_shaft must cover sqrt((tau/r_eff)^2 + N_spring^2). One-face clutch N_spring=tau/(mu_face*r_face) is conditional on friction/contact assumptions.',
        shaft_coverage_of_clamp_zone_mm=min(shaft_tip)-(dd['clamp_bolt_Y_mm']+1.6),
        remaining=['Actual collet pressure/contact and minimum grip under bolt preload','Do not equate bolt preload to shaft normal force; nominal coverage is not loaded closure proof','Real D-flat contact/load distribution and torsional/axial slip','Actual material, bolt proof, motor axial bearing limit','Rated/calibrated spring/friction and protected transient maximum'],actual_capacity_qualified=False,whole_system_release=False)
    dump(out/'summary.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
