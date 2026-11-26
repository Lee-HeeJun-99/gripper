"""Actual RevAF drive full-turn and slip-pose interference screen.

Prescribed geometric poses ONLY; no dynamic, strength or cable sliding claim.
Wire is excluded ONLY from this rotor/structure screen: the moving coil must
be independently regenerated, not treated as the immobile installed CAD wire.
"""
import argparse,json,math,shutil,sys
from baseline_registry import ROOT,S1,REPO,ref,dump,sha
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds,overlap,common
from mechanisms_stage1 import pitch_at

def main():
    p=argparse.ArgumentParser();p.add_argument('--candidate',required=True);p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'validation/stage1'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    src=ROOT/'cad/exports'/a.candidate/'summary.json';d=json.loads(src.read_text());shapes={}
    for n,r in d['part_references'].items():
        path=REPO/r['path'];assert sha(path)==r['SHA256'];shapes[n]=read(path)
    rotor=[n for n in shapes if n.startswith(('F0_DRUM','F0_CLUTCH')) and n!='F0_CLUTCH_BEARING']
    input_only=[n for n in rotor if n.startswith('F0_CLUTCH')]
    base={n:s for n,s in shapes.items() if n not in rotor and not n.endswith('TENDON_WIRE')}
    hits=[];comparisons=0;poses=[]
    for mode,moving_names in [('co_rotation',rotor),('jam_slip',input_only)]:
        fixed=dict(base)
        if mode=='jam_slip':fixed.update({n:shapes[n] for n in rotor if n not in input_only})
        bb={n:bounds(s) for n,s in fixed.items()}
        for deg in range(0,360,15):
            for n in moving_names:
                s=pitch_at(shapes[n],math.radians(deg),(110,0,20));b=bounds(s)
                for k,t in fixed.items():
                    if overlap(b,bb[k]):
                        comparisons+=1;v=common(s,t)
                        if abs(v)>1e-8:hits.append(dict(mode=mode,angle_deg=deg,a=n,b=k,common_mm3=v))
            poses.append(dict(mode=mode,angle_deg=deg))
    result=dict(status='SAMPLED_DRIVE_CLEARANCE_PASS' if not hits else 'SAMPLED_DRIVE_CLEARANCE_FAIL',candidate=ref(src),producer=ref(out/'producer.py'),poses=poses,comparisons=comparisons,hits=hits,
        scope='F0 actual full-turn drive and clutch slip geometry, 24 poses each; no continuous collision proof. Retained other-sector hardware included.',
        limitations=['No full Finger movement or deformed PET','No winding/fixed-wire reinterpretation','No drive/cap/clamp strength or torque-limit rating','No powered operation or integrated release'],whole_system_release=False)
    dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],comparisons=comparisons,hits=hits),indent=2))
if __name__=='__main__':main()
