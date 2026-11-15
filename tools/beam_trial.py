"""Small independent rod verification; no grasp success inferred from exit code."""
import json,math,argparse
import xml.etree.ElementTree as ET
import numpy as np
from beam_common import ROOT,OUT,SDK,PLUGIN,FRAME,write_json,sha,identity,material
from native_scene import PLUGINS
from run_trial import execute_process
from trial_validation import read_states
def run(name,nodes=11,dt=.0005,duration=3.,axis=2,load=-1e-6,rotation=0.,inherited=False):
    if not name.replace('_','').isalnum() or nodes not in (3,11,21,41) or axis not in range(6) or not math.isfinite(load) or not .000125<=dt<=.001 or not 0<duration<=24:raise ValueError('bounded beam input')
    steps=round(duration/dt)
    if steps>120000 or steps%20 or abs(steps*dt-duration)>1e-10:raise ValueError('steps')
    out=OUT/'single'/name;out.mkdir(parents=True,exist_ok=False);root=ET.Element('Node',name='ConservativeBeamResearch',dt=str(dt),gravity='0 0 0')
    for i,p in enumerate(PLUGINS):ET.SubElement(root,'RequiredPlugin',name='p'+str(i),pluginName='Sofa.Component.'+p)
    ET.SubElement(root,'DefaultAnimationLoop');ET.SubElement(root,'EulerImplicitSolver',rayleighMass='.2',rayleighStiffness='.1');ET.SubElement(root,'EigenSparseLU',name='solver',template='CompressedRowSparseMatrixMat3x3d');body=ET.SubElement(root,'Node',name='Multilayer');n=nodes;co,si=math.cos(rotation),math.sin(rotation)
    poses=[[100*i/(n-1)*co,100*i/(n-1)*si,0,0,0,math.sin(rotation/2),math.cos(rotation/2)] for i in range(n)];seq=lambda vals:' '.join(map(str,vals));edges=[j for i in range(n-1) for j in (i,i+1)]
    ET.SubElement(body,'MechanicalObject',name='dofs',template='Rigid3d',position=seq(v for p in poses for v in p));ET.SubElement(body,'MeshTopology',name='edges',lines=seq(edges));ET.SubElement(body,'UniformMass',totalMass='1e-5');m=material()
    if inherited:ET.SubElement(body,'BeamFEMForceField',radius=str((4*(8*.4**3/12)/math.pi)**.25),youngModulus='250',poissonRatio='.32')
    else:ET.SubElement(body,'ConservativeBeam',edges=seq(edges),**{k:str(v) for k,v in m.items()})
    ET.SubElement(body,'FixedProjectiveConstraint',indices='0');f=[0.]*6;f[axis]=load;ET.SubElement(body,'ConstantForceField',indices=str(n-1),forces=seq(f));ET.SubElement(body,'IntegratedRecorder',filename=str(out/'state.txt'),stride='20');ET.ElementTree(root).write(out/'scene.scn',encoding='utf-8',xml_declaration=True)
    config=dict(nodes=n,dt=dt,duration=duration,axis=axis,load=load,rotation=rotation,length=100.,mass=1e-5,material=m,section='unchanged circular A and equal circular Iy=Iz=8*.4^3/12; GJ=2GI; effective shear5/6 is explicit research assumption',solver='EigenSparseLU nonsymmetric',inherited=inherited)
    command=[str(SDK/'bin/graph_probe'),str(SDK),str(out/'scene.scn'),str(steps),'0',str(FRAME),str(PLUGIN)];write_json(out/'config.json',config);write_json(out/'command.json',command);record=dict(config=config,identity=identity(),status='FAIL');process=execute_process(command,out,480);record['process']=process
    try:
        log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text()
        if process['exit_code'] or '[ERROR]' in log or f'{steps} iterations done' not in log:raise ValueError('engine incomplete/error')
        raw=read_states(out/'state.txt');x=np.array([r['X'] for r in raw]).reshape(-1,n,7);v=np.array([r['V'] for r in raw]).reshape(-1,n,6);R=np.array([r['R'] for r in raw]).reshape(-1,n,6);t=np.array([r['time'] for r in raw]);tail=(t>=duration-.1-1e-8)
        if len(raw)!=steps//20+1 or not all(np.isfinite(a).all() for a in (x,v,R,t)):raise ValueError('nonfinite/incomplete state')
        scale=abs(load)/(100 if axis>=3 else 1) if load else 1e-6;fr=float(abs(R[tail,1:,:3]).max()/scale);mr=float(abs(R[tail,1:,3:]).max()/(scale*100));speed=float(abs(v[tail]).max());reaction=-R[-1,0];origin=x[-1,-1,:3];total=np.r_[reaction[:3]+np.array(f[:3]),reaction[3:]+np.cross(x[-1,0,:3]-origin,reaction[:3])+np.array(f[3:])];global_res=max(abs(total[:3]).max()/scale,abs(total[3:]).max()/(scale*100));tip=x[-1,-1,:3]-x[0,-1,:3];angle=2*np.arctan2(np.linalg.norm(x[-1,-1,3:6]),abs(x[-1,-1,6]));drift=float(np.linalg.norm(x[tail,-1,:3]-x[tail,-1,:3][0],axis=1).max());disp=float(np.linalg.norm(tip));equilibrium=fr<1e-3 and mr<1e-3 and speed<1e-5 and (drift/(disp or 1)<1e-4)
        record.update(status='PASS' if equilibrium and global_res<1e-3 else 'FAIL',execution_completed=True,equilibrium=equilibrium,tip_displacement=tip.tolist(),tip_angle_rad=float(angle),force_residual=fr,moment_residual=mr,global_balance=float(global_res),speed=speed,drift=drift,final_reaction=reaction.tolist(),full_grasp_certified=False)
    except (ValueError,OSError,KeyError) as e:record['failure_reason']=str(e)
    record['artifacts']={p.name:sha(p) for p in out.iterdir() if p.is_file()};write_json(out/'metrics.json',record);print(name,record['status'],record.get('tip_displacement'),record.get('force_residual'),process['runtime_s'],flush=True);return record
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('--nodes',type=int,default=11);p.add_argument('--duration',type=float,default=3);p.add_argument('--dt',type=float,default=.0005);p.add_argument('--axis',type=int,default=2);p.add_argument('--load',type=float,default=-1e-6);args=p.parse_args();run(args.name,nodes=args.nodes,duration=args.duration,dt=args.dt,axis=args.axis,load=args.load)
