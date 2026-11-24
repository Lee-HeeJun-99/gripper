"""Four-route initial finite-envelope gate;not dynamic assembly evidence.

A: prior Skin-only centre-terminated support proxy is unsafe for wire.
B: one outer-wall attachment + backside elbow design,not random offsets.
"""
import argparse,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from opposed_tendon_coupon import nonuniform_reference,segment_bound
def pair_bound(a,b,c,d,radius=.5,step=.25):
 n=max(1,int(np.ceil(np.linalg.norm(b-a)/step)));p=np.linspace(a,b,n+1);D=d-c;s=np.clip((p-c)@D/(D@D),0,1);return float(np.linalg.norm(p-(c+s[:,None]*D),axis=1).min()-np.linalg.norm(b-a)/(2*n)-radius)
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);base=BASE/'results/b3_railback_grasp1001298';back=BASE/'results/opposed_nonuniform_mid1398';c=json.loads((base/'config.json').read_text());mesh=json.loads((base/'mesh.json').read_text());frontroot=ET.parse(base/'scene.scn').getroot();reference=nonuniform_reference(frontroot,c,mesh);backroot=ET.parse(back/'scene.scn').getroot();routes=[];centres=[];supportsA=[];supportsB=[];bore=[];details=[];guide=frontroot.find("Node[@name='guides0']");anchors=np.fromstring(guide.find("Node[@name='anchors']/MechanicalObject").get('position'),sep=' ').reshape(-1,3)*1000;owners=np.fromstring(guide.find("Node[@name='anchors']/RigidMapping").get('rigidIndexPerPoint'),sep=' ',dtype=int)
 for mode,root in (('front',frontroot),('back',backroot)):
  for cable in range(2):
   n=root.find(f"Node[@name='guides0']/Node[@name='cable{cable}']");q=np.fromstring(n.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3)*1000;pull=np.fromstring(n.find('CableConstraint').get('pullPoint'),sep=' ')*1000;path=np.vstack([pull,q]);routes.append(path);centres.extend(q);ids=np.fromstring(n.find('RigidMapping').get('rigidIndexPerPoint'),sep=' ',dtype=int);attach=[]
   for k,(point,owner) in enumerate(zip(q,ids)):
    before=path[k];incoming=(point-before)/np.linalg.norm(point-before);outgoing=incoming if k==len(q)-1 else (q[k+1]-point)/np.linalg.norm(q[k+1]-point);axis=incoming+outgoing;axis/=np.linalg.norm(axis);width=np.array([0.,np.sign(point[1]),0.]);width-=axis*np.dot(axis,width);width/=np.linalg.norm(width);wall=point+1.5*width;foot=anchors[owners==owner].mean(0);supportsA.append((foot,point));normal=np.array(reference(c,[c['tendon']['guide_stations'][k],0,1],0))-reference(c,[c['tendon']['guide_stations'][k],0,0],0)
    if mode=='front':elbow=wall-6*normal;supportsB.extend([(foot,elbow),(elbow,wall)])
    else:supportsB.append((foot,wall))
    # Straight2mm bore axis is local incoming/outgoing bisector. Wire must fit
    # both entry planes;this does NOT resolve finite-curvature cable bending.
    cos=min(np.dot(incoming,axis),np.dot(outgoing,axis));radial=np.sqrt(max(0.,1-cos*cos))/cos;bore.append(.6-.25-radial);attach.append(wall.tolist())
   details.append(dict(mode=mode,cable=cable,route_mm=path.tolist(),outer_wall_attachment_mm=attach))
 wires=[(i,a,b) for i,path in enumerate(routes) for a,b in zip(path[:-1],path[1:])];wirewire=min(pair_bound(a,b,c1,d) for i,a,b in wires for j,c1,d in wires if i<j);points=np.array(centres);guidegap=min(float(np.linalg.norm(points[i]-points[j])-2*np.hypot(1.5,1)) for i in range(len(points)) for j in range(i));wireA=min(pair_bound(a,b,c1,d) for a,b in supportsA for i,c1,d in wires);wireB=min(pair_bound(a,b,c1,d) for a,b in supportsB for i,c1,d in wires);finger=frontroot.find("Node[@name='finger0']");q0=np.fromstring(finger.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3)*1000;skin=finger.find("Node[@name='skinCollision']");index=np.fromstring(skin.find('SubsetMapping').get('indices'),sep=' ',dtype=int);tri=q0[index[np.fromstring(skin.find('MeshTopology').get('triangles'),sep=' ',dtype=int).reshape(-1,3)]];skinB=min(segment_bound(a,b,tri,.25,.25) for a,b in supportsB);safe=min(wirewire,guidegap,wireB,skinB,min(bore))>0
 d=dict(status='PASS_INITIAL_FOUR_ROUTE_PROXY_GATE_ONLY' if safe else 'REJECT_INITIAL_FOUR_ROUTE_GATE',wire_wire_capsule_lower_bound_mm=wirewire,guide_guide_enclosing_sphere_gap_mm=guidegap,centre_terminated_support_wire_lower_bound_mm=wireA,outer_wall_elbow_support_wire_lower_bound_mm=wireB,outer_wall_elbow_support_skin_lower_bound_mm=skinB,minimum_straight_bore_wire_margin_mm=min(bore),all_bore_margins_mm=bore,routes=details,support_A_segments_mm=[(a.tolist(),b.tolist()) for a,b in supportsA],support_B_segments_mm=[(a.tolist(),b.tolist()) for a,b in supportsB],Native_four_cable='NOT RUN',mass_inertia='NOT MEASURED for new finite supports and paired eyelets',scope='Initial singlefinger actualrest-reference routecoexistence:wireR.25,rodR.25,eyeletOD3/ID1.2/length2mm. Supports must joinouterwall not borecentre;annularsolid/manufacturing/strength and bendradius5mm NOTQUALIFIED. Bore geometricplanesonly,not a flexiblewire contactsolution. No dynamic3Finger/HoldingPASS.',physical_validation='NOT QUALIFIED',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),input_hashes={str(p.relative_to(BASE)):sha(p) for p in (base/'scene.scn',base/'mesh.json',base/'config.json',back/'scene.scn')});(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in d.items() if k not in ('routes','support_A_segments_mm','support_B_segments_mm','all_bore_margins_mm','input_hashes')}))
if __name__=='__main__':main()
