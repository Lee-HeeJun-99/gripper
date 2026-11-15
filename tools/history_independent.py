"""Independent prescribed-contact and continuous-interface investigations."""
import argparse,json
import numpy as np
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve
from history_common import ROOT,OUT,write_json,sha
from closure_validation_suite import logged
from beam_common import material
def structural():
    out=OUT/'structural_interface';out.mkdir(exist_ok=False)
    m=material();EA,GA,EI=m['EA'],m['GAz'],m['EIy'];k=84.1732992010;records=[]
    for n in (11,21,41,81,161):
        h=100/(n-1);nd=6*n;K=lil_matrix((nd,nd));F=np.zeros(nd)
        bu=np.array([-1,0,0,1,0,0]);bs=np.array([0,-1,h/2,0,1,h/2]);bb=np.array([0,0,-1,0,0,1]);ke=EA/h*np.outer(bu,bu)+GA/h*np.outer(bs,bs)+EI/h*np.outer(bb,bb)
        for layer in (0,1):
            for i in range(n-1):
                ids=np.arange(3*(layer*n+i),3*(layer*n+i)+6)
                for a in range(6):
                    for b in range(6):K[ids[a],ids[b]]+=ke[a,b]
            F[3*((layer+1)*n-1)+1]=-5e-7
        locations=[i*(n-1)//10 for i in range(1,11)]
        for i in locations:
            ids=[3*i,3*i+2,3*(n+i),3*(n+i)+2];b=np.array([-1,-.2,1,-.2])
            for a in range(4):
                for c in range(4):K[ids[a],ids[c]]+=k*b[a]*b[c]
        K=K.tocsr();free=np.array([i for i in range(nd) if (i//3)%n]);u=np.zeros(nd);u[free]=spsolve(K[free][:,free],F[free]);slip=u[3*n::3]-u[:3*n:3]-.2*(u[3*n+2::3]+u[2:3*n:3]);res=float(abs((K@u-F)[free]).max()/5e-7)
        # Linear element u and theta imply piecewise affine slip: its supremum
        # on each closed element is EXACTLY at an endpoint. All endpoints count.
        records.append(dict(nodes=n,max_entire_interface_mm=float(abs(slip).max()),max_connector_only_mm=float(abs(slip[locations]).max()),maximum_location_mm=float(np.argmax(abs(slip))*h),tip_mm=float(-np.mean(u[[3*(n-1)+1,3*(2*n-1)+1]])),relative_residual=res,slip=list(map(float,slip))))
    for a,b in zip(records,records[1:]):b['relative_change_entire_interface']=abs(a['max_entire_interface_mm']/b['max_entire_interface_mm']-1)
    r=dict(status='PASS' if all(x['relative_residual']<1e-3 for x in records) else 'FAIL',candidate_approved=False,scope='INDEPENDENT LINEAR FEM; no fresh SOFA or Optuna trial',k=k,connector_locations_mm=list(range(10,101,10)),material=m,records=records,source_sha256=sha(ROOT/'tools/history_independent.py'),finding='connector-only objective is NOT substituted; coarse nodes omit between-connector maxima. Spatial refinement remains mandatory for actual SOFA candidates.')
    write_json(out/'metrics.json',r);print([(x['nodes'],x['max_entire_interface_mm'],x.get('relative_change_entire_interface')) for x in records])
def prescribed():
    out=OUT/'prescribed_reference';out.mkdir(exist_ok=False)
    r=logged([ROOT/'build/history_20261115/extra/history_prescribed'],out/'run',60)
    r.update(source_sha256=sha(ROOT/'tests/contact_history_extra/prescribed.cpp'),binary_sha256=sha(ROOT/'build/history_20261115/extra/history_prescribed'),status='PASS' if r['exit_code']==0 and 'PASS prescribed' in (out/'run/stdout.log').read_text() else 'FAIL')
    write_json(out/'metrics.json',r);print(r['status'])
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('task',choices=['structural','prescribed']);a=p.parse_args();globals()[a.task]()
