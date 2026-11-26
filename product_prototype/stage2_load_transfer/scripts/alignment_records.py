"""Conservative two-station rim reading reduction. No power-enable output.
Signed four-azimuth readings require a calibrated setup; no actual test here.
"""
import argparse,csv,json,math
import numpy as np
def evaluate(rows):
    if len(rows)!=2:return dict(status='NOT MEASURED',hardware_pass=False,reason='two complete station records required')
    fields=['y_m','r0_m','r90_m','r180_m','r270_m','uncertainty_m']
    try:
        for r in rows:
            if any(r.get(k) in (None,'') for k in fields+['calibration_ID','specimen_ID','timestamp']):return dict(status='NOT MEASURED',hardware_pass=False)
            if not all(math.isfinite(float(r[k])) for k in fields):raise ValueError('nonfinite input')
            if float(r['uncertainty_m'])<0:raise ValueError('negative uncertainty')
        if len({r['specimen_ID'] for r in rows})!=1 or len({r['calibration_ID'] for r in rows})!=1:raise ValueError('mixed setup')
        ys=np.array([float(r['y_m']) for r in rows]);dy=ys[1]-ys[0]
        if abs(dy)<.005:raise ValueError('station separation <5mm')
        centers=np.array([[(float(r['r0_m'])-float(r['r180_m']))/2,(float(r['r90_m'])-float(r['r270_m']))/2] for r in rows])
        target=-.026;weight=(target-ys[0])/dy
        if not 0<=weight<=1:raise ValueError('stations must bracket coupling datum Y=-26mm')
        c=(1-weight)*centers[0]+weight*centers[1];slope=(centers[1]-centers[0])/dy
        u=np.array([float(r['uncertainty_m']) for r in rows])*math.sqrt(2)
        bound=float(np.linalg.norm(c)+(1-weight)*u[0]+weight*u[1]+.01075*(np.linalg.norm(slope)+sum(u)/abs(dy)))
        return dict(status='WITHIN PROVISIONAL ALIGNMENT BUDGET' if bound<=5e-6 else 'FAIL',
            combined_offset_bound_m=bound,maximum_m=5e-6,hardware_pass=False,power_authorized=False,
            warning='Motor material/contact/bearing/plate compliance and actual setup calibration still required; this is NOT a powered release')
    except (ValueError,TypeError) as e:return dict(status='INVALID',hardware_pass=False,reason=str(e))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('csv');a=p.parse_args();result=evaluate(list(csv.DictReader(open(a.csv))))
    print(json.dumps(result,indent=2));raise SystemExit(0 if result['status']=='WITHIN PROVISIONAL ALIGNMENT BUDGET' else 2)
