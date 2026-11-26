"""Conditional per-tendon transmission demands, not certified capacities.
Rolling plain-journal idler: do NOT apply fixed-capstan exp(mu*wrap).
"""
import argparse,json,math
from pathlib import Path
import numpy as np
from scipy.optimize import brentq
from load_requirements import ROOT,path,sha
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--tag',required=True);a=ap.parse_args()
    out=ROOT/'validation/integrated'/a.tag;out.mkdir(parents=True,exist_ok=False)
    elastica=ROOT/'validation/finger/elastica1/summary.json'
    rows=[]
    for pose in json.loads(elastica.read_text())['rows']:
        if not (pose['locked'] and pose['n']==64 and pose['within_Stage1_0_60_deg']):continue
        tf=pose['tension_N'];p=np.array(pose['pivot_m']);q=np.array([.044,.025])
        r=.01118;d=p-q;b=-(math.atan2(-d[1],-d[0])-math.acos(r/np.linalg.norm(d)))
        tangent=q-r*np.array([math.cos(b),-math.sin(b)])
        uout=(p-tangent)/np.linalg.norm(p-tangent)
        ulead=np.array([.036,-.005]);ulead/=np.linalg.norm(ulead)
        for journal_mu in (0.,.1,.3):
            # Stationary washer axial drag is NOT invented as zero; omitted
            # from this isolated radial-journal sensitivity and remains a gate.
            f=lambda td:td-tf-journal_mu*.0015/r*np.linalg.norm(td*ulead+tf*uout)
            td=brentq(f,tf,tf*2)
            reaction=-(td*ulead+tf*uout)
            tau=td*r
            # Cable resultant at Y=0; actual bearing centres -6 and +11.5.
            rl=td*11.5/17.5;rr=td*6/17.5
            # Simplified pin bearing at two drum bore edges +/-4.05mm.
            pin_force=tau/(2*.00405);pin_area=math.pi*.00149**2/4
            nominal_pin_shear=pin_force/pin_area
            idler_load=np.linalg.norm(reaction)
            moment=idler_load*.00275 # root runout to nominal pulley midplane
            idler_sigma=32*moment/(math.pi*.00155**3)
            balance=np.array([-td,0,td-rl-rr])
            rows.append(dict(finger_tension_N=tf,assumed_journal_mu=journal_mu,
                motion_angle_deg=pose['tip_rotation_deg'],drum_tension_N=td,drum_torque_Nm=tau,
                idler_reaction_N=reaction.tolist(),idler_radial_load_N=float(idler_load),
                left_bearing_radial_N=rl,right_bearing_radial_N=rr,
                force_balance_N=abs(td-rl-rr),moment_balance_Nm=abs(rl*.006-rr*.0115),
                journal_torque_balance_Nm=abs((td-tf)*r-journal_mu*.0015*idler_load),
                nominal_pin_double_shear_Pa=nominal_pin_shear,
                nominal_idler_runout_bending_Pa=float(idler_sigma),
                required_coupling_normal_force_at_assumed_mu_0_1_N=tau/(.1*.002195),
                motor_holding_torque_fraction=tau/.45,
                supplier_running_torque_margin=None,
                qualifiers=['NO pin notch/bending/contact strength approval','NO axle preload/notch/fatigue approval','NO axial washer drag included','mu sensitivity, not measured bounds','bearing alignment/preload/ratings not qualified','motor running/acceleration losses unresolved']))
    assert all(x['force_balance_N']<1e-8 and x['moment_balance_Nm']<1e-10 and x['journal_torque_balance_Nm']<1e-10 for x in rows)
    result=dict(status='PASS',scope='CONDITIONAL DEMAND / EQUILIBRIUM ONLY; NOT CONTINUOUS LOAD-PATH QUALIFICATION',
        case='revAA_heel_relief2',rows=rows,source_SHA256=sha(Path(__file__)),input_SHA256=sha(elastica),
        actual_required_tension='UNRESOLVED: these are bounded model inputs, not grasp demand',
        command='python scripts/transmission_map.py --tag '+a.tag)
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
