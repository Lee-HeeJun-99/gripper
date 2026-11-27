"""Independent saved-interface reimport, mesh topology and route checks.
Does not call either producer's geometry or requirement functions.
"""
import collections,itertools,json,math,shutil,sys
import numpy as np
from scipy.spatial.transform import Rotation
from baseline_registry import ROOT,REPO,S1,S2,sha,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,common,bounds,overlap,solid_count,volume,cyl,rotate,translate,export
from OCP.BRepCheck import BRepCheck_Analyzer

def mesh_check(p):
    verts=[]
    for line in p.read_text().splitlines():
        t=line.split()
        if t and t[0]=='vertex':verts.append(tuple(map(float,t[1:])))
    assert len(verts)%3==0 and verts
    edges=collections.Counter();oriented=collections.Counter();v=0
    for k in range(0,len(verts),3):
        a,b,c=np.array(verts[k:k+3]);v+=float(a@np.cross(b,c))/6
        ids=[tuple(round(x,11) for x in q) for q in (a,b,c)]
        for x,y in zip(ids,ids[1:]+ids[:1]):
            assert x!=y
            edge=tuple(sorted((x,y)));edges[edge]+=1;oriented[edge]+=1 if x<y else -1
    return dict(triangles=len(verts)//3,closed=all(v==2 for v in edges.values()),oriented=all(v==0 for v in oriented.values()),signed_volume_mm3=v)

def geometry(theta):
    # Independent vector rotation and tangent-length formula. No wm.path,
    # route(), tip_position() or producer finite differences are invoked.
    if theta==0:tip=np.array([50.,0,-100.])
    else:tip=np.array([50-88/theta*2*math.sin(theta/2)**2,0,-7-88*math.sin(theta)/theta-5*math.cos(theta)])-np.array([5*math.sin(theta),0,0])
    R=Rotation.from_rotvec([0,theta,0]).as_matrix();P=tip+R@np.array([-7.,0,8.])
    dv=np.array([44.,0,25.])-P;D=np.linalg.norm(dv);beta=-(math.atan2(dv[2],dv[0])-math.acos(11.25/D))
    end=math.atan2(math.sin(beta),-math.cos(beta));phi=math.atan2(66,5)
    while end<phi:end+=2*math.pi
    length=(math.hypot(66,5)+11.25*(end-phi)+math.sqrt(D*D-11.25**2)-16)*.001
    return length,(50-tip[0])*.001

def main():
    assert not (ROOT/'runtime/STOP').exists()
    out=ROOT/'validation/transmission/batch6_micro_verify1';out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    cp=ROOT/'cad/exports/revAV_micro_interface1/summary.json';op=ROOT/'validation/transmission/batch6_operating1/summary.json'
    cd=json.loads(cp.read_text());od=json.loads(op.read_text());pd=json.loads((REPO/cd['parent']['path']).read_text())
    dump(out/'inputs.json',dict(candidate=ref(cp),operating=ref(op),producer=ref(out/'producer.py'),checks=dict(mesh_volume_relative_max=.001,saved_route_absolute_m_max=1e-10,derivative_relative_max=1e-6,independent_work_relative_max=1e-6,intersection_mm3_max=1e-8),mesh_vertex_key_round_decimal_mm=11,rounding_scope='mesh topology identity only; no geometric intersection/gap acceptance change'))
    parts={};quality=[];errors=[];fingerprints=[]
    for doc in (cd,od):
        inp=json.loads((REPO/doc['inputs']['path']).read_text())
        for r in inp['dependencies']+[inp['producer']]:
            ok=sha(REPO/r['path'])==r['SHA256'];fingerprints.append(dict(**r,match=ok))
            if not ok:errors.append('input hash '+r['path'])
    for row in cd['parts']:
        assert not (ROOT/'runtime/STOP').exists()
        n=row['part_ID'];p=REPO/row['STEP']['path'];s=read(p);parts[n]=s
        stl=REPO/row['STL']['path'];m=mesh_check(stl)
        valid=BRepCheck_Analyzer(s).IsValid() and solid_count(s)==1 and volume(s)>0
        mrel=abs(m['signed_volume_mm3']/volume(s)-1)
        ok=valid and m['closed'] and m['oriented'] and m['signed_volume_mm3']>0 and mrel<=.001 and sha(p)==row['STEP']['SHA256'] and sha(stl)==row['STL']['SHA256']
        quality.append(dict(part_ID=n,valid_single_solid=valid,mesh=m,mesh_volume_relative_error=mrel,passed=ok))
        if not ok:errors.append('quality '+n)
    # Exact independent dimension/volume controls at sector0.
    spool_expected=math.pi*(11**2*2+(12**2-11**2)-1.6**2*2-4*1.65**2*2)
    D_area=math.pi*1.5**2-(1.5**2*math.acos(1/1.5)-math.sqrt(1.5**2-1))
    motor_expected=10*12*25.6+math.pi*2**2*.7+D_area*8.3
    dimension_checks=dict(spool_volume_relative=abs(volume(parts['F0_SPOOL'])/spool_expected-1),motor_volume_relative=abs(volume(parts['F0_MICRO_MOTOR'])/motor_expected-1),hub_bounds_mm=bounds(parts['F0_STOCK_HUB']))
    if max(dimension_checks['spool_volume_relative'],dimension_checks['motor_volume_relative'])>1e-8:errors.append('independent volume')
    hub_b=np.array(bounds(parts['F0_STOCK_HUB']));
    if np.max(abs(hub_b-np.array([101.25,-6,11.25,118.75,-1,28.75])))>1e-8:errors.append('hub dimensions')
    retained={n:read(REPO/r['path']) for n,r in pd['part_references'].items() if n not in cd['context_replacement_IDs']}
    allparts={**retained,**parts};bb={n:bounds(s) for n,s in allparts.items()};hits=[];pairs=0
    for n,m in itertools.combinations(allparts,2):
        if n not in parts and m not in parts:continue
        assert not (ROOT/'runtime/STOP').exists()
        if overlap(bb[n],bb[m]):
            pairs+=1;v=common(allparts[n],allparts[m])
            if v>1e-8:hits.append(dict(a=n,b=m,common_mm3=v))
    tools=[];toolhits=[]
    for i in range(3):
        local=[('SET',cyl(1,(119,-3.5,20),20,(1,0,0)))]
        for j in range(4):
            a=math.pi/4+j*math.pi/2;local.append((f'FACE{j}',cyl(1.5,(110+6.35*math.cos(a),4,20+6.35*math.sin(a)),20,(0,1,0))))
        for name,s in local:
            n=f'F{i}_{name}_DRIVER';s=rotate(s,120*i);export(s,out/n);tools.append(ref(out/(n+'.step')))
            for m,t in allparts.items():
                if overlap(bounds(s),bb[m]):
                    v=common(s,t)
                    if v>1e-8:toolhits.append(dict(tool=n,part=m,common_mm3=v))
    if hits or toolhits:errors.append('retained geometry or tool intersection')
    # A real misplaced interface must be rejected by the same exact test.
    negative_volume=common(translate(parts['F0_STOCK_HUB'],.2,0,0),parts['F0_MICRO_MOTOR'])
    if negative_volume<=1e-8:errors.append('misplaced hub control not detected')
    # Independent central differences and midpoint summation of T ds.
    facts=json.loads((ROOT/'models/standard_drive/batch6_sources1/reviewed.json').read_text())
    ep=507000*6894.757293168;er=193e9;Lp=.0862
    average_width=(.024-.12*.007+.024-.12*(Lp+.007))/2
    k=2*er*.003*.0002**3/(12*.088)+ep*average_width*.0003**3/(12*Lp)
    route_errors=[];derivative_errors=[];force_errors=[]
    for row in od['rows']:
        x=math.radians(row['angle_deg']);h=1e-5
        L,X=geometry(x);lm,xm=geometry(x-h);lp,xp=geometry(x+h);ds=(lm-lp)/(2*h);dx=(xp-xm)/(2*h)
        route_errors.append(abs((geometry(0)[0]-L)-row['stroke_m']))
        derivative_errors.extend([abs(ds/row['stroke_derivative_m_rad']-1),abs(dx/row['inward_derivative_m_rad']-1)])
        normal=.1*9.80665/(3*row['assumed_mu']);T=(normal*dx+k*x)/ds
        force_errors.append(abs(T/row['conditional_tension_N']-1))
    work=[]
    for mu in (.2,.4,.8):
        nn=.1*9.80665/(3*mu);expected=nn*geometry(math.pi/3)[1]+.5*k*(math.pi/3)**2
        refinements=[]
        for count in (500,1000):
            xs=np.linspace(0,math.pi/3,count+1);W=0
            for a,b in zip(xs[:-1],xs[1:]):
                x=(a+b)/2;h=1e-5;la,xa=geometry(x-h);lb,xb=geometry(x+h)
                T=(nn*(xb-xa)/(2*h)+k*x)/((la-lb)/(2*h));W+=T*(geometry(a)[0]-geometry(b)[0])
            refinements.append(dict(intervals=count,work_J=W,relative_error=abs(W/expected-1)))
        work.append(dict(mu=mu,expected_J=expected,refinements=refinements))
    if max(route_errors)>1e-10 or max(derivative_errors+force_errors)>1e-6:errors.append('independent route/force reconstruction')
    if max(r['relative_error'] for w in work for r in w['refinements'])>1e-6:errors.append('independent tendon work')
    recommendation_failures=sum(row['ideal_linear_motor_current_A']>.25*facts['motor']['extrapolated_stall_current_A'] for row in od['rows'])
    result=dict(status='PASS' if not errors else 'FAIL',scope='INDEPENDENT ACTUAL SAVED DRIVE INTERFACE / CONDITIONAL REQUIREMENT VERIFICATION ONLY',candidate=ref(cp),operating=ref(op),producer=ref(out/'producer.py'),inputs=ref(out/'inputs.json'),errors=errors,quality=quality,dimension_checks=dimension_checks,input_hashes=fingerprints,exact_intersection_pairs=pairs,intersections=hits,tool_intersections=toolhits,tools=tools,misplaced_hub_control_intersection_mm3=negative_volume,route_absolute_errors_m=route_errors,derivative_relative_errors=derivative_errors,force_relative_errors=force_errors,work=work,recommendation_failures=recommendation_failures,
        motor_operating_acceptance='NOT QUALIFIED;7/15 conditional scenarios exceed general current recommendation; nominal geometry PASS does not resolve duty or rating',actual_capacity_qualified=False,whole_system_release=False)
    dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],errors=errors,quality=len(quality),pairs=pairs,toolhits=toolhits,recommendation_failures=recommendation_failures)))
    raise SystemExit(2 if errors else 0)
if __name__=='__main__':main()
