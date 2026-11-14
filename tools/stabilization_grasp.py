"""Opposing planar-guided 100mm multilayer fingers and a genuinely free Rigid3 object.

Research assumptions explicit. Velocity-regularized kinetic friction creeps; it
does not certify static stick or practical grasp capacity. No object constraints.
"""
import argparse
import csv
from dataclasses import asdict
import json
import math
import xml.etree.ElementTree as ET
import numpy as np
from integrated_trial import Config,scene,sequence
from stabilization_common import ROOT,SOFA,OUT,BUILD,write_json,sha,provenance
from trial_validation import read_states
from run_trial import execute_process

def run(name,shape=0,axis=0,load=1e-6,dt=.0005,duration=12,nodes=11,samples=8,mu=.3,hold_until=8,rayleigh_mass=.2):
    c=Config(k=1,mode=1,load=0,nodes=nodes,dt=dt,duration=duration);c.validate()
    if not all(math.isfinite(v) for v in (load,mu)) or mu<0 or shape not in (0,1,2) or axis not in (0,1,2) or type(samples) is not int or not 1<=samples<=32:raise ValueError('invalid grasp configuration')
    if not 8<=hold_until<=18 or not math.isfinite(rayleigh_mass) or not 0<=rayleigh_mass<=5:raise ValueError('bounded schedule/damping')
    out=OUT/'grasp'/name;out.mkdir(parents=True,exist_ok=False)
    scene(out,c);tree=ET.parse(out/'scene.scn');root=tree.getroot();root.find('EulerImplicitSolver').set('rayleighMass',str(rayleigh_mass));body=root.find('Node');n=nodes;per=2*n;obj=2*per
    for node in list(body):body.remove(node)
    poses=[]
    for finger in (0,1):
        base=5.305 if finger==0 else -5.305
        for layer in range(2):
            for i in range(n):poses.append([100*i/(n-1),0,base+(layer-.5)*.4,0,0,0,1])
    poses.append([95,0,0,0,0,0,1])
    ET.SubElement(body,'MechanicalObject',name='dofs',template='Rigid3d',position=sequence(v for p in poses for v in p))
    edges=[(finger*per+layer*n+i,finger*per+layer*n+i+1) for finger in range(2) for layer in range(2) for i in range(n-1)]
    ET.SubElement(body,'MeshTopology',name='edges',lines=sequence(v for e in edges for v in e))
    inertia=10 if shape==0 else (25/2+100/12 if shape==1 else 50/3)
    masses=[[.00004/obj,1,1,0,0,0,1,0,0,0,1] for _ in range(obj)]+[[.0001,4*math.pi*125/3,inertia,0,0,0,inertia,0,0,0,inertia]]
    ET.SubElement(body,'DiagonalMass',name='all_masses',template='Rigid3d,Rigid3d',mstate='@dofs',geometryState='@dofs',topology='@edges',vertexMass=sequence(v for row in masses for v in row))
    r=(4*(8*.4**3/12)/math.pi)**.25
    ET.SubElement(body,'BeamFEMForceField',radius=str(r),youngModulus='250',poissonRatio='.32')
    ET.SubElement(body,'FixedProjectiveConstraint',indices=sequence([0,n,per,per+n]))
    ET.SubElement(body,'PartialFixedProjectiveConstraint',indices=sequence(range(obj)),fixedDirections='0 1 0 1 0 1')
    for finger in range(2):
        ET.SubElement(body,'LayerNetwork',name='layer'+str(finger),startIndex=str(finger*per),nodesPerLayer=str(n),layers='2',mode='1',stiffness='1',height='.4',normalStiffness='.001',width='8',length='100',pressure='0',mu='.3',pressureTimes=sequence([0,3,hold_until+1]),pressureValues='0 .001 0')
        for layer in range(2):ET.SubElement(body,'RoutedCable',name=f'cable{finger}_{layer}',route=sequence(range(finger*per+layer*n,finger*per+(layer+1)*n)),offsetZ=str(-.2 if finger==0 else .2),commandTimes=sequence([0,.5,hold_until+2]),commandValues='0 .001 0')
    ET.SubElement(body,'DistributedContact',name='contact',segments=sequence(v for e in edges for v in e),objectIndex=str(obj),shape=str(shape),radius='5',pointRadius='.1',lineStiffness='.001',mu=str(mu),speed='0.00001',samples=str(samples))
    ET.SubElement(body,'ScheduledLoad',name='disturbance',indices=str(obj),axis=str(axis),times=sequence([0,6,hold_until]),values=sequence([0,load,0]))
    ET.SubElement(body,'IntegratedRecorder',filename=str(out/'state.txt'),stride='20')
    ET.SubElement(body,'ContactHistory',filename=str(out/'contact.csv'),stride='20')
    root.set('dt',str(dt));tree.write(out/'scene.scn',encoding='utf-8',xml_declaration=True)
    plugin=BUILD/'contact_v2/libReGripDistributed.so';command=[str(SOFA/'bin/runSofa-26.06.00'),'--noautoload','--tmp','-g','batch','-a','-n',str(round(duration/dt)),'--hideProgressBar','-l',str(plugin),str(out/'scene.scn')]
    config=dict(shape=shape,axis=axis,load=load,dt=dt,duration=duration,nodes=nodes,samples=samples,mu=mu,fingers=2,layers=2,length=100,base_z=[5.305,-5.305],object_index=obj,object_mass=.0001,object_inertia_per_mass=inertia,
        object_constraints=[],finger_guided_planar=True,friction='smooth kinetic Coulomb; NO exact static stick',hold_limit_mm=.05,hold_limit_rationale='1% of 5mm research-object radius; not original negative-control .001mm benchmark; velocity/force gates also mandatory',tension_per_layer=.001,pressure_on=.001,hold_until=hold_until,rayleigh_mass=rayleigh_mass,pressure_off=hold_until+1,tendon_off=hold_until+2)
    write_json(out/'config.json',config);write_json(out/'command.json',command);p=execute_process(command,out,180)
    report=dict(config=config,provenance=provenance(),binary_sha256=sha(plugin),process=p,status='FAIL',grasp_certified=False)
    try:
        log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text()
        if p['exit_code'] or '[ERROR]' in log or 'behavior is undefined' in log or 'Only one BaseMass' in log or f'{round(duration/dt)} iterations done' not in log:raise ValueError('SOFA execution/log/undefined-component failure')
        raw=read_states(out/'state.txt')
        if len(raw)!=round(duration/dt)//20+1:raise ValueError('incomplete raw states')
        rows=[]
        for r0 in raw:
            x=np.array(r0['X']).reshape(-1,7);v=np.array(r0['V']).reshape(-1,6)
            if x.shape!=(obj+1,7) or not np.isfinite(x).all() or not np.isfinite(v).all():raise ValueError('state dimensions/nonfinite')
            if max(np.max(abs(x[:obj,3])),np.max(abs(x[:obj,5])))>1e-8 or np.max(2*np.arctan2(abs(x[:obj,4]),abs(x[:obj,6])))>=.005:raise ValueError('planar finger domain exceeded')
            rows.append(dict(time=r0['time'],object_x=x[obj,0],object_y=x[obj,1],object_z=x[obj,2],object_speed=float(np.max(abs(v[obj,:3]))),object_angle=float(2*math.atan2(np.linalg.norm(x[obj,3:6]),abs(x[obj,6])))))
        with (out/'contact.csv').open() as stream:contact=list(csv.DictReader(stream))
        before=min(rows,key=lambda r:abs(r['time']-6));hold=[r for r in rows if 6-1e-8<=r['time']<=hold_until+1e-8];displacement=max(math.sqrt(sum((r['object_'+a]-before['object_'+a])**2 for a in 'xyz')) for r in hold) if hold else None
        D=[float(r['friction_dissipation']) for r in contact];power=[float(r['friction_power']) for r in contact];contacts=[float(r['contacts']) for r in contact]
        if min(D)<-1e-15 or min(power)<-1e-15 or any(b<a-1e-15 for a,b in zip(D,D[1:])):raise ValueError('friction dissipation failure')
        report.update(status='EXPERIMENTAL',execution_completed=True,hold_displacement_mm=displacement,declared_translation_benchmark_pass=displacement is not None and displacement<.05,max_contacts=max(contacts),friction_dissipation=D[-1],peak_object_angle=max(r['object_angle'] for r in rows),
            limitation='not certified: kinetic friction creep, guided-planar fingers, static friction/enclosure/torque envelope and convergence gates still required')
        with (out/'object.csv').open('x') as stream:writer=csv.DictWriter(stream,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
    except (ValueError,OSError,KeyError) as e:report['failure_reason']=str(e)
    report['artifacts']={f.name:sha(f) for f in out.iterdir() if f.is_file() and f.name!='metrics.json'};write_json(out/'metrics.json',report);print(name,report['status'],report.get('hold_displacement_mm'),report.get('failure_reason'),flush=True);return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('--shape',type=int,default=0,choices=[0,1,2]);p.add_argument('--axis',type=int,default=0,choices=[0,1,2]);p.add_argument('--load',type=float,default=1e-6);p.add_argument('--duration',type=float,default=12);p.add_argument('--dt',type=float,default=.0005);p.add_argument('--nodes',type=int,default=11);p.add_argument('--samples',type=int,default=8);p.add_argument('--mu',type=float,default=.3);a=p.parse_args()
    if a.duration>12 or a.dt<.00025 or a.nodes>21 or a.samples>32:raise ValueError('bounded research campaign')
    run(a.name,a.shape,a.axis,a.load,a.dt,a.duration,a.nodes,a.samples,a.mu)
