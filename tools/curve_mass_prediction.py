"""Record a falsifiable hypothesis before inspecting mass-control outcomes."""
import json
import numpy as np
from curve_common import OUT,write_json
def main():
    x=[];y=[]
    for n,name in((11,'n11'),(21,'fixed_n21'),(41,'fixed_n41')):
        r=json.loads((OUT/'grasp'/name/'metrics.json').read_text());s=np.linspace(0,1,n);phi=s*s*(3-s)/2;x.append(float(np.mean(phi**2)));y.append(r['hold_displacement_mm'])
    slope,intercept=np.polyfit(x,y,1);rows=[]
    for n in(11,21,41):
        s=np.linspace(0,1,n);phi=s*s*(3-s)/2;mass=float(np.trapz(phi**2,s));rows.append(dict(nodes=n,assumed_tributary_modal_mass=mass,predicted_peak_mm=float(intercept+slope*mass)))
    target=OUT/'mass_hypothesis_prediction.json'
    if target.exists():raise FileExistsError(target)
    write_json(target,dict(origin='empirical diagnostic fit to existing uniform-mass cases ONLY,NOT a SOFA measurement or physical force correction',assumption='prescribed cubic cantilever mode is a proxy,not a measured eigenmode',slope=float(slope),intercept=float(intercept),fit_residual_mm=(np.array(y)-(intercept+slope*np.array(x))).tolist(),predictions=rows,warning='never used to alter force,objective,gate or measured metrics;future actual mass-control runs can falsify it'))
    print(rows)
if __name__=='__main__':main()
