"""Re-run affected positive scenes after invalid-input hardening, keep v1 immutable."""
import json
from dataclasses import replace
from integrated_trial import Config,run
from integrated_common import OUT,write_json

def main():
    out=OUT/'hardening_regression';out.mkdir(parents=True,exist_ok=False);rows={};checks={}
    contact=Config(mode=1,k=1,pressure=1e-8,cable_tension=1e-5,normal_k=.001,object_x=100,object_z=-5.305,object_shape=0)
    for name,c,reference in [('planar',Config(k=100),'multilayer/L2_k100'),
                             ('finite',Config(mode=2,k=100),'objective_connector/small'),
                             ('contact_wire_pressure',contact,'contact/sphere')]:
        r=run(out/name,c);rows[name]=r;old=json.loads((OUT/reference/'metrics.json').read_text())
        checks[name]=r['status']=='PASS' and abs(r['tip_deflection_mm']-old['tip_deflection_mm'])<1e-10
        write_json(out/'summary.json',dict(records=rows,checks=checks,passed=all(checks.values()),scope='v2 positive regression against separately preserved v1, not result mixing'))
    if not all(checks.values()):raise RuntimeError('hardening regression failed')

if __name__=='__main__':main()
