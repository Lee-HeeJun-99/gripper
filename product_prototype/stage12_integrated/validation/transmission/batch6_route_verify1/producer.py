"""Independent reimport/mesh/analytic verification of actual route rejection."""
import json,math,sys,collections
import numpy as np
from baseline_registry import ROOT,REPO,S1,ref,dump,sha
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,common,volume,solid_count,translate,bounds
from OCP.BRepCheck import BRepCheck_Analyzer

def mesh(path):
    vertices=[tuple(map(float,line.split()[1:])) for line in path.read_text().splitlines() if line.strip().startswith('vertex ')]
    t=np.array(vertices).reshape((-1,3,3));origin=t.mean(axis=(0,1));q=t-origin
    signed=float(np.einsum('ij,ij->i',q[:,0],np.cross(q[:,1],q[:,2])).sum()/6)
    # Numerical vertex identity only (1nm), NOT geometric acceptance/clearance.
    ids={};edges=collections.Counter();directed=collections.Counter()
    for tri in t:
        ii=[]
        for p in tri:
            key=tuple(np.round(p,9));ii.append(ids.setdefault(key,len(ids)))
        for a,b in zip(ii,ii[1:]+ii[:1]):edges[tuple(sorted((a,b)))]+=1;directed[(a,b)]+=1
    closed=all(v==2 for v in edges.values())
    oriented=all(directed[(a,b)]==directed[(b,a)]==1 for a,b in edges)
    return dict(triangles=len(t),closed=closed,oriented=oriented,signed_volume_mm3=signed)
def main():
    assert not (ROOT/'runtime/STOP').exists()
    src=ROOT/'cad/exports/revAW_direct_route2/summary.json';d=json.loads(src.read_text());inp=json.loads((REPO/d['inputs']['path']).read_text())
    out=ROOT/'validation/transmission/batch6_route_verify1';out.mkdir(parents=True,exist_ok=False)
    import shutil;shutil.copyfile(__file__,out/'producer.py')
    checks=[]
    for r in [d['inputs'],d['producer'],d['BOM_delta'],inp['AO'],inp['AV'],inp['contract'],*inp['parts'].values()]:assert sha(REPO/r['path'])==r['SHA256']
    palm=read(REPO/inp['parts']['PALM']['path']);pb=bounds(palm);wire_shapes={};lengths=[];errors=[]
    for row in d['rows']:
        for kind in ('STEP','STL'):assert sha(REPO/row[kind]['path'])==row[kind]['SHA256']
        s=read(REPO/row['STEP']['path']);wire_shapes[row['part_ID']]=s;m=mesh(REPO/row['STL']['path'])
        valid=BRepCheck_Analyzer(s).IsValid() and solid_count(s)==1 and volume(s)>0
        assert valid and m['closed'] and m['oriented'] and m['signed_volume_mm3']>0
        assert abs(m['signed_volume_mm3']/volume(s)-1)<.01
        P,Q,E=[np.array(row[k]) for k in ('P_mm','Q_mm','E_mm')];C=np.array([110.,0,20]);n=Q-C
        assert abs(np.linalg.norm(n)-11.25)<1e-9
        assert abs(np.dot(n,Q-E))<1e-8
        assert abs(np.linalg.norm(E-P)-16)<1e-9
        assert np.linalg.norm(np.cross(E-P,Q-P))<1e-8 and np.dot(E-P,Q-P)>0
        # Derive route length from geometry and winding, independent of producer.
        phi=math.atan2(n[2],n[0]);L=11.25*(phi+math.pi/2+row['rotor_angle_rad'])+np.linalg.norm(Q-E)
        lengths.append(L);assert abs(volume(s)/(math.pi*.25**2*L)-1)<1e-6
        actual=common(s,palm);assert actual>1e-8
        stored=next(h['common_mm3'] for h in d['hits'] if h['wire']==row['part_ID'] and h['part']=='PALM')
        assert abs(actual-stored)<1e-8
        # Straight segment crosses a Palm-height plane. This is a locator,
        # not a substitute for the exact imported-BRep intersection above.
        z=(pb[2]+pb[5])/2;u=(z-E[2])/(Q[2]-E[2]);cross=E+u*(Q-E)
        checks.append(dict(part=row['part_ID'],valid_single_solid=bool(valid),mesh=m,independent_length_mm=float(L),palm_intersection_mm3=actual,palm_midheight_crossing_F0_mm=cross.tolist(),crossing_on_straight_span=bool(0<u<1)))
    assert max(lengths)-min(lengths)<1e-8
    # Actual rejection machinery must distinguish disjoint and colliding solids.
    control=common(translate(wire_shapes[d['rows'][0]['part_ID']],0,0,500),palm);assert control<=1e-8
    corrupted=d['rows'][0].copy();corrupted['Q_mm']=[x+1 for x in corrupted['Q_mm']]
    radius_error=abs(np.linalg.norm(np.array(corrupted['Q_mm'])-np.array([110.,0,20]))-11.25);assert radius_error>1e-9
    dump(out/'summary.json',dict(status='PASS',scope='Independent verification of DIRECT_ROUTE_INTERFERENCE_FAIL, NOT product PASS',source=ref(src),producer=ref(out/'producer.py'),checks=checks,input_hashes_verified=True,constant_length_range_mm=max(lengths)-min(lengths),translated_disjoint_control_mm3=control,corrupt_tangent_control_radius_error_mm=float(radius_error),palm_bounds_mm=pb,whole_system_release=False))
    print(json.dumps(dict(status='PASS',verified_routes=len(checks),max_intersection_mm3=max(x['palm_intersection_mm3'] for x in checks),min_intersection_mm3=min(x['palm_intersection_mm3'] for x in checks),constant_length_range_mm=max(lengths)-min(lengths))))
if __name__=='__main__':main()
