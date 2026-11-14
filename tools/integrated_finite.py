"""Finite-rotation BeamFEM validation against exact pure-moment elastica.

Uncoupled beam structural check, independent of connector-kernel certification.
No geometry/material change to any certified scene. No physical PET claim.
"""
import json
import math
import xml.etree.ElementTree as ET
from integrated_trial import Config,scene,analyze
from integrated_common import ROOT,SOFA,OUT,BUILD,write_json,sha,provenance
from run_trial import execute_process
from trial_validation import read_states

def main():
    root=OUT/'finite_beam';root.mkdir(parents=True,exist_ok=False);results={}
    for name,theta,n,dt in [('small',.004,11,.001),('medium',.1,11,.001),('large',.5,11,.001),('large_mesh',.5,21,.001),('large_halfdt',.5,11,.0005)]:
        out=root/name;out.mkdir();I=8*.4**3/12;M=2*250*I*theta/100
        c=Config(k=0,mode=2,load=0,moment=M,nodes=n,dt=dt,duration=30,stride=20)
        g=scene(out,c);tree=ET.parse(out/'scene.scn');body=tree.getroot().find('Node');body.remove(body.find('LayerNetwork'));tree.write(out/'scene.scn',encoding='utf-8',xml_declaration=True)
        plugin=BUILD/'plugin/libReGripIntegrated.so'
        cmd=[str(SOFA/'bin/runSofa-26.06.00'),'--noautoload','--tmp','-g','batch','-a','-n',str(round(c.duration/c.dt)),'--hideProgressBar','-l',str(plugin),str(out/'scene.scn')]
        from dataclasses import asdict
        write_json(out/'config.json',asdict(c));write_json(out/'command.json',cmd)
        process=execute_process(cmd,out,180);log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text();r=dict(config=asdict(c),provenance=provenance(),process=process,binary_sha256=sha(plugin),scope='SOFA pure end-moment BeamFEM vs exact static circular-arc elastica')
        try:
            r.update(analyze(out,c,g,process,log));last=read_states(out/'state.txt')[-1]['X'];tip=n-1;actualx=last[7*tip];actualtheta=2*math.atan2(last[7*tip+4],last[7*tip+6]);exactx=100*math.sin(theta)/theta;exactz=100*(1-math.cos(theta))/theta
            r.update(exact_tip_x=exactx,actual_tip_x=actualx,exact_tip_deflection=exactz,actual_tip_angle=actualtheta,
                elastica_relative_error=abs(r['tip_deflection_mm']/exactz-1),angle_relative_error=abs(actualtheta/theta-1))
            r['elastica_passed']=r['status']=='PASS' and r['elastica_relative_error']<.01 and r['angle_relative_error']<.01
        except (ValueError,KeyError,OSError) as e:r.update(status='FAIL',reason=str(e),elastica_passed=False)
        r['artifacts']={p.name:sha(p) for p in out.iterdir() if p.is_file() and p.name!='metrics.json'};write_json(out/'metrics.json',r);results[name]=r;write_json(root/'summary.json',results)
        print(name,r['status'],r.get('tip_deflection_mm'),r.get('elastica_relative_error'),flush=True)

if __name__=='__main__':main()
