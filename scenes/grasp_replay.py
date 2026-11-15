"""Recorded SOFA states only: visualization, NOT a new physics simulation."""
import json,os
from pathlib import Path
import Sofa.Core

def seq(values):return ' '.join(map(str,values))
def createScene(root):
    data=json.loads(Path(os.environ['REGRIP_REPLAY_DATA']).read_text());frames=data['frames'];c=data['config'];n=c['nodes'];obj=c['object_index'];root.dt=frames[1]['time']-frames[0]['time'];root.gravity=[0,0,0]
    for i,name in enumerate(('AnimationLoop','StateContainer','Topology.Container.Constant','Mapping.NonLinear','Visual')):root.addObject('RequiredPlugin',name='r'+str(i),pluginName='Sofa.Component.'+name)
    root.addObject('RequiredPlugin',name='render',pluginName='Sofa.GL.Component.Rendering3D');root.addObject('DefaultAnimationLoop');root.addObject('VisualStyle',displayFlags='showVisualModels showBehaviorModels')
    body=root.addChild('Recorded');dofs=body.addObject('MechanicalObject',name='dofs',template='Rigid3d',position=seq(frames[0]['X']),showObject=True,showObjectScale=.06)
    finger_visuals=[]
    for tag,wire in [('finger_centerlines',False),('actual_wire_guides',True)]:
        node=body.addChild(tag);positions=[];indices=[]
        for i in range(obj):positions.extend([0,0,(-.2 if i<2*n else .2) if wire else 0]);indices.append(i)
        edges=[(layer*n+i,layer*n+i+1) for layer in range(4) for i in range(n-1)];node.addObject('MeshTopology',lines=seq(v for e in edges for v in e))
        visual=node.addObject('OglModel',name='visual',position=seq(positions),edges=seq(v for e in edges for v in e),color='1 .2 .2 1' if wire else '.2 .5 1 1')
        if not wire:finger_visuals.append(visual)
        node.addObject('RigidMapping',name='recorded_pose_mapping',input='@../dofs',output='@visual',rigidIndexPerPoint=seq(indices))
    # A latitude/longitude skin follows the ACTUAL recorded object's full pose.
    radius=c['object_radius'];positions=[];triangles=[];lat=12;lon=24
    for i in range(lat+1):
        for j in range(lon):theta=i*3.141592653589793/lat;phi=j*2*3.141592653589793/lon;import math;positions.extend([radius*math.sin(theta)*math.cos(phi),radius*math.cos(theta),radius*math.sin(theta)*math.sin(phi)])
    for i in range(lat):
        for j in range(lon):a=i*lon+j;b=i*lon+(j+1)%lon;triangles.extend([(a,b,b+lon),(a,b+lon,a+lon)])
    node=body.addChild('RecordedObject');node.addObject('OglModel',name='surface',position=seq(positions),triangles=seq(v for t in triangles for v in t),color='.8 .8 .85 1');node.addObject('RigidMapping',input='@../dofs',output='@surface',rigidIndexPerPoint=seq([obj]*((lat+1)*lon)))
    class Replay(Sofa.Core.Controller):
        def __init__(self):super().__init__();self.index=0;self.jam=None
        def onAnimateBeginEvent(self,event):
            frame=frames[min(self.index,len(frames)-1)];dofs.position.value=[frame['X'][7*i:7*(i+1)] for i in range(obj+1)]
            jam=c['pressure']>0 and 3<=frame['time']<c['hold_until']+1
            if jam!=self.jam:
                for visual in finger_visuals:
                    color='1 .6 .1 1' if jam else '.2 .5 1 1'
                    visual.material.value='Default Diffuse 1 '+color+' Ambient 1 0.2 0.2 0.2 1 Specular 0 1 1 1 1 Emissive 0 0 0 0 1 Shininess 0 45'
                print('REGRIP_REPLAY_COMMANDED_JAM',jam,frame['time'],flush=True);self.jam=jam
            if self.index<10:print('REGRIP_REPLAY_FRAME',self.index,frame['time'],flush=True)
            self.index+=1
    root.addObject(Replay());return root
