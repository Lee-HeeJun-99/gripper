"""Actual SOFA whole-scene rigid-frame covariance regression (not only kernel)."""
import math
import argparse
from pathlib import Path
import xml.etree.ElementTree as ET
from research_trial import scene,FINITE
from trial_validation import read_states
from run_trial import execute_process
from verification_common import ROOT,SOFA,BUILD,sha,write_json,provenance,assert_build_current

def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def rotate(q,v):
    a=q[:3];c=cross(a,v);cc=cross(a,c);return [v[i]+2*(q[3]*c[i]+cc[i]) for i in range(3)]
def multiply(a,b):
    c=cross(a[:3],b[:3]);return [a[3]*b[i]+b[3]*a[i]+c[i] for i in range(3)]+[a[3]*b[3]-sum(a[i]*b[i] for i in range(3))]

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'results/next_phase/finite_objectivity');p.add_argument('--reference',type=Path,default=ROOT/'results/next_phase/sofa/finite_L30');a=p.parse_args()
    assert_build_current();out=a.out;out.mkdir(parents=True,exist_ok=False)
    manifest=__import__('json').loads((FINITE.parent/'manifest.json').read_text())
    if sha(FINITE)!=manifest['binary']:raise RuntimeError('binary mismatch')
    for path,digest in manifest['sources'].items():
        if sha(ROOT/path)!=digest:raise RuntimeError('source mismatch')
    scene(out,30,11,1,1e-4,.0005,True,None)
    axis=[.3,.4,.5];angle=math.sqrt(sum(x*x for x in axis));q=[x*math.sin(angle/2)/angle for x in axis]+[math.cos(angle/2)]
    translation=[2.,-3.,1.];tree=ET.parse(out/'scene.scn')
    for obj in tree.getroot().iter('MechanicalObject'):
        width=7 if obj.get('template')=='Rigid3d' else 3;values=list(map(float,obj.get('position').split()))
        for i in range(0,len(values),width):
            p=rotate(q,values[i:i+3]);values[i:i+3]=[p[j]+translation[j] for j in range(3)]
            if width==7:values[i+3:i+7]=multiply(q,values[i+3:i+7])
        obj.set('position',' '.join(map(str,values)))
    for ff in tree.getroot().iter('ConstantForceField'):
        v=list(map(float,ff.get('forces').split()))
        for i in range(0,len(v),3):v[i:i+3]=rotate(q,v[i:i+3])
        ff.set('forces',' '.join(map(str,v)))
    tree.write(out/'scene.scn',encoding='utf-8',xml_declaration=True)
    cmd=[str(SOFA/'bin/runSofa-26.06.00'),'--noautoload','--tmp','-g','batch','-a','-n','6000','--hideProgressBar',
        '-l',str(BUILD/'diagnostics/libReGripDiagnostics.so'),'-l',str(FINITE),str(out/'scene.scn')]
    write_json(out/'command.json',cmd);result=execute_process(cmd,out,120)
    log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text()
    base=a.reference;maximum={key:0. for key in ('position','velocity','quaternion','residual','interface')};passed=True
    for filename,width in [('rigid.txt',7),('interface.txt',3)]:
        a=read_states(base/filename);b=read_states(out/filename)
        if len(a)!=6001 or len(b)!=6001:raise RuntimeError('incomplete trace')
        for ref,actual in zip(a,b):
            if abs(ref['time']-actual['time'])>1e-12:raise RuntimeError('time mismatch')
            for i in range(0,len(ref['X']),width):
                expected=[x+y for x,y in zip(rotate(q,ref['X'][i:i+3]),translation)]
                key='position' if width==7 else 'interface'
                maximum[key]=max(maximum[key],max(abs(x-y) for x,y in zip(expected,actual['X'][i:i+3])))
                if width==7:
                    expectedq=multiply(q,ref['X'][i+3:i+7]);v=actual['X'][i+3:i+7]
                    maximum['quaternion']=max(maximum['quaternion'],min(max(abs(x-y) for x,y in zip(expectedq,v)),max(abs(x+y) for x,y in zip(expectedq,v))))
            for key,metric in [('V','velocity'),('R','residual')]:
                if key not in ref:continue
                if len(ref[key])!=len(actual.get(key,[])):raise RuntimeError('missing derivative')
                for i in range(0,len(ref[key]),3):
                    expected=rotate(q,ref[key][i:i+3]);maximum[metric]=max(maximum[metric],max(abs(x-y) for x,y in zip(expected,actual[key][i:i+3])))
    # Whole-engine covariance tolerances declared independently of legacy golden tolerance.
    tolerances=dict(position=1e-8,interface=1e-8,quaternion=1e-9,velocity=1e-8,residual=1e-8)
    passed=result['exit_code']==0 and '[ERROR]' not in log and '6000 iterations done' in log and all(maximum[k]<tolerances[k] for k in maximum)
    write_json(out/'summary.json',dict(status='PASS' if passed else 'FAIL',provenance=provenance(),process=result,
        maximum_absolute_errors=maximum,tolerances=tolerances,global_quaternion=q,translation=translation,
        binary_sha256=sha(FINITE),runner_sha256=sha(__file__),scene_sha256=sha(out/'scene.scn'),reference=str(base),
        artifacts={p.name:sha(p) for p in out.iterdir() if p.is_file() and p.name!='summary.json'}))
    print(passed,maximum)

if __name__=='__main__':main()
