"""Locate peak versus settled motion without changing the existing peak gate."""
import json
import numpy as np
from curve_common import OUT,write_json
def audit(path):
    rows=[];time=0
    with(path/'state.txt').open()as f:
        for line in f:
            if line.startswith('T='):time=float(line[2:])
            elif line.startswith('X='):rows.append((time,np.fromstring(line[2:],sep=' ')[-7:-4]))
    t=np.array([r[0]for r in rows]);x=np.array([r[1]for r in rows]);origin=x[np.argmin(abs(t-6))];d=np.linalg.norm(x-origin,axis=1);hold=(t>=6-1e-8)&(t<=14+1e-8);ids=np.flatnonzero(hold);peak=ids[np.argmax(d[hold])];tail=(t>=13.9-1e-8)&(t<14-1e-8)
    c=json.loads((path/'config.json').read_text());n=c['nodes'];s=np.linspace(0,1,n);phi=s*s*(3-s)/2
    uniform=float(np.mean(phi**2));trapezoid=float(np.trapz(phi**2,s));analytic=33/140
    return dict(peak_time_s=float(t[peak]),peak_translation_mm=float(d[peak]),peak_vector_mm=(x[peak]-origin).tolist(),tail_translation_mm=float(d[tail].mean()),tail_vector_mm=(x[tail].mean(axis=0)-origin).tolist(),mass_quadrature_diagnostic=dict(assumed_test_mode='prescribed cubic cantilever phi(s)=s^2(3-s)/2,not actual solved eigenmode',uniform_nodal_modal_mass_over_total=uniform,trapezoid_modal_mass_over_total=trapezoid,analytic_modal_mass_over_total=analytic,uniform_relative_error=abs(uniform-analytic)/analytic,trapezoid_relative_error=abs(trapezoid-analytic)/analytic))
def main():
    records={p.parent.name:audit(p.parent)for p in(OUT/'grasp').glob('*/metrics.json')if not json.loads(p.read_text())['config']['profile_only']}
    result=dict(status='EXPERIMENTAL',origin='actual SOFA trajectory diagnosis plus independent mass quadrature calculation;peak1percent gate unchanged',cases=records)
    write_json(OUT/'motion_audit.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
