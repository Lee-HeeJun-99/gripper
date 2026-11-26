"""Independent solid-volume witness and rigid-wrench audit."""
import json,sys,shutil
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,common

def main():
    assert not (ROOT/'runtime/STOP').exists()
    out=ROOT/'validation/finger/AK_root_pressure_verify1';out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    source=ROOT/'validation/finger/AK_root_pressure1/summary.json';d=json.loads(source.read_text());inp=json.loads((REPO/d['inputs']['path']).read_text());old=json.loads((REPO/inp['source']['path']).read_text())
    for r in [d['inputs'],inp['source'],inp['producer'],*inp['parts'].values(),*inp['dependencies'],*[p['shape'] for p in d['patches']]]:assert sha(REPO/r['path'])==r['SHA256']
    ss={n:read(REPO/r['path']) for n,r in inp['parts'].items() if 'BOLT' not in n};rows=[]
    for side,lo in [('L',-11.5),('R',8.5)]:
        rail='F0_RAIL_'+side
        for a,b in [('F0_ROOT_FRONT','F0_SKIN'),('F0_SKIN',rail),(rail,'F0_ROOT_BACK')]:
            c=next(c for c in old['contacts'] if c['a']==a and c['b']==b);x=c['centroid_mm'][0]
            for h in [.001,.002]:
                # Solid interiors independently test both sides of every interface.
                va=common(ss[a],box(x-h,lo,4,h,3,2))/h
                vb=common(ss[b],box(x,lo,4,h,3,2))/h
                rows.append(dict(side=side,a=a,b=b,width_mm=h,areas_mm2=[va,vb],passed=max(abs(va-6),abs(vb-6))<1e-5))
    # Direct moments and work of two unit-normal contact resultants vs bolts.
    points=[(0,-10,5),(0,10,5)];bolts=[(0,*b['axis_yz_mm']) for b in old['bolts']]
    def moment(points):return [0,sum(.5*p[2] for p in points),-sum(.5*p[1] for p in points)]
    residual=max(abs(a-b) for a,b in zip(moment(points),moment(bolts)))
    delta=[.03,-.02,.01,.002,-.004,.003]
    def work(points):return sum(.5*(delta[0]+delta[4]*p[2]-delta[5]*p[1]) for p in points)
    corrupt=[(x,y,z+.1) for x,y,z in points]
    checks=dict(all24solid_slices=len(rows)==12 and all(r['passed'] for r in rows),saved_patch_area=all(abs(p['area_mm2']-6)<1e-8 for p in d['patches']),saved_centroids=all(max(abs(a-b) for a,b in zip(p['centroid_mm'],q))<1e-8 for p,q in zip(d['patches'],points)),normal_moment=residual<1e-6,virtual_work=abs(work(points)-work(bolts))<1e-12,shifted_pressure_rejected=abs(moment(corrupt)[1]-moment(bolts)[1])>1e-6)
    ok=all(checks.values());dump(out/'summary.json',dict(status='INDEPENDENT_PRESSURE_WITNESS_PASS' if ok else 'FAIL',source=ref(source),producer=ref(out/'producer.py'),dependencies=[ref(S1/'scripts/incremental_stage1.py'),ref(S1/'scripts/build_stage1.py')],checks=checks,rows=rows,moment_residual_Nmm=residual,virtual_work_error_Nmm=abs(work(points)-work(bolts)),whole_system_release=False));print(json.dumps(checks));raise SystemExit(0 if ok else 2)
if __name__=='__main__':main()
