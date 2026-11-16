"""Reproducible concept meshes/orthographic drawings and analytical screening.
Not a contact simulation. Existing baseline is extracted without editing it.
"""
import argparse,ast,hashlib,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,s):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x')as f:f.write(s)
def js(p,d):put(p,json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def baseline():
 source=ROOT/'tools/closure_frame_trial.py';tree=ast.parse(source.read_text());node=next(n for n in tree.body if isinstance(n,ast.ClassDef)and n.name=='Config')
 c={n.target.id:ast.literal_eval(n.value)for n in node.body if isinstance(n,ast.AnnAssign)}
 points=[];roots=[]
 for a in (0,2*math.pi/3,-2*math.pi/3):
  ex=(math.cos(a),0,-math.sin(a));ez=(math.sin(a),0,math.cos(a))
  origin=[95-95*ex[0]+c['base_z']*ez[0],0,-95*ex[2]+c['base_z']*ez[2]];roots.append(origin)
  for layer in (0,1):
   points.append([[origin[j]+100*i/10*ex[j]+(layer-.5)*.4*ez[j]for j in range(3)]for i in range(11)])
 return dict(source='tools/closure_frame_trial.py',source_sha256=sha(source),config=c,center=[95,0,0],roots=roots,centerlines=points,root_radius_mm=math.hypot(95,c['base_z']),contact_surface_area_mm2=None,contact_model='1D centerline skin;no finite contact width',guide='world y,rotation x/z constrained',equivalent_beam_area_per_layer_mm2=json.loads((ROOT/'models/gripper_100mm/assumptions.json').read_text())['used_for_numerical_tests_only']['equivalent_circular_area_mm2'])
def width(s):return 24 if s<=50 else 24-12*(s-50)/50
def ribbon(angle,theta,layer=0):
 ex=(math.cos(angle),0,-math.sin(angle));ew=(math.sin(angle),0,math.cos(angle));v=[]
 for i in range(21):
  s=5*i;t=theta*s/100;k=theta/100
  radial=50-((1-math.cos(t))/k if k else 0);y=-math.sin(t)/k if k else -s
  for j in range(5):
   w=width(s)*(j/4-.5);offset=layer*.05
   v.append([radial*ex[0]+w*ew[0]+offset*math.cos(t)*ex[0],y-offset*math.sin(t),radial*ex[2]+w*ew[2]+offset*math.cos(t)*ex[2]])
 f=[]
 for i in range(20):
  for j in range(4):
   a=i*5+j;f.extend([(a,a+1,a+5),(a+1,a+6,a+5)])
 return v,f
def obj(meshes):
 out=['# Concept / implemented mesh geometry ONLY;not SOFA deformed output'];offset=1
 for n,(v,f)in enumerate(meshes):
  out.append('g finger_'+str(n));out += ['v '+' '.join(f'{x:.12g}'for x in p)for p in v]
  out += ['f '+' '.join(str(offset+i)for i in q)for q in f];offset+=len(v)
 return '\n'.join(out)+'\n'
def svg_panel(polylines,title,projection,origin=(0,0,0)):
 def proj(p):
  x,y,z=[p[i]-origin[i]for i in range(3)]
  return {'front':(x,-y),'top':(x,z),'side':(z,-y),'iso':(x-.55*z,-y+.3*(x+z))}[projection]
 pts=[proj(p)for line in polylines for p in line];xmin=min(x for x,y in pts);xmax=max(x for x,y in pts);ymin=min(y for x,y in pts);ymax=max(y for x,y in pts);scale=min(290/max(1,xmax-xmin),205/max(1,ymax-ymin))
 out=[f'<text x="12" y="22" font-size="13">{title}</text>']
 for i,line in enumerate(polylines):
  xy=[proj(p)for p in line];coords=' '.join(f'{15+(x-xmin)*scale:.3f},{40+(y-ymin)*scale:.3f}'for x,y in xy)
  out.append(f'<polyline points="{coords}" fill="none" stroke="{["#087f8c","#d45c35","#5956a5"][i%3]}" stroke-width="1.4"/>')
 return ''.join(out)
def drawing(b,candidates):
 panels=[]
 for i,(label,lines,origin)in enumerate([('Baseline extracted centerlines',b['centerlines'],b['center']),*candidates]):
  for j,view in enumerate(('iso','front','side','top')):
   panels.append(f'<g transform="translate({j*330},{i*275+45})">'+svg_panel(lines,label+' / '+view,view,origin)+'</g>')
 return '<svg xmlns="http://www.w3.org/2000/svg" width="1320" height="940" viewBox="0 0 1320 940"><rect width="1320" height="940" fill="#fafafa"/><text x="20" y="25" font-size="19">ReGrip: extracted baseline + CONCEPT meshes. NOT simulated deformation.</text>'+''.join(panels)+'</svg>'
def mechanism():
 s=['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="540"><rect width="1100" height="540" fill="white"/><g font-family="sans-serif"><text x="20" y="28" font-size="21">CONCEPT: tapered film cartridge / three-zone vacuum jacket</text>']
 for i,(a,b)in enumerate(((0,30),(35,65),(70,100))):
  x=35+8*a;w=8*(b-a);s.append(f'<rect x="{x}" y="65" width="{w}" height="130" rx="10" fill="{["#b4dfe5","#e6d3aa","#cec9e8"][i]}" stroke="#333"/><text x="{x+12}" y="95">zone {i+1}: {a}-{b} mm</text><path d="M{x+20},65 V45 H1015 V{250+i*40}" fill="none" stroke="#555"/><text x="900" y="{265+i*40}">circuit {i+1}</text>')
 s+=['<path d="M20,115 H850 M20,160 H850" stroke="#c74b31" stroke-width="3"/><text x="35" y="220">Two edge tendons; equalizer drive. Three circuits shared across fingers.</text><text x="35" y="248">5 mm unjammed hinge/seal bridges. Continuous object-facing skin.</text>']
 for j in range(8):s.append(f'<rect x="40" y="{290+8*j}" width="330" height="5" fill="#69a4ad" stroke="#333"/>')
 s+=['<text x="390" y="310">Section: 8 x assumed 0.05 mm film + sleeve</text><text x="390" y="340">Pressure port / sealed pouch / sliding distal layer ends</text><text x="390" y="370">Root clamp transfers load; seals must not bond all layers together</text><text x="35" y="410">Sequence: approach - tendon adapt - selected zones jam - hold - vent - release</text><text x="35" y="445">Jamming OFF/ON shapes here are NOT SOFA results. No proven holding-force gain.</text><text x="35" y="480">Changeable root cartridge; elastic sleeve/return strip. Sealing and hose routing unresolved.</text></g></svg>']
 return ''.join(s)
def compliance(zones):
 # Euler-Bernoulli tip-force compliance integral,assumed EI multipliers only.
 # This is NOT a pressure calibration or a grasp model.
 E=250;off=8*E*24*.05**3/12
 return sum(((100-a)**3-(100-b)**3)/(3*off*m)for a,b,m in zones)
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);args=p.parse_args()
 if not args.tag.replace('_','').isalnum():raise ValueError('simple unique version')
 base=ROOT/'designs';b=baseline();js(base/'baseline'/args.tag/'geometry.json',b)
 candidate_lines=[];comparison=[]
 for name,selective in (('film_contact',False),('selective_jamming',True)):
  folder=base/name/args.tag
  meshes=[ribbon(a,.77)for a in (0,2*math.pi/3,-2*math.pi/3)]
  rest=[ribbon(a,0)for a in (0,2*math.pi/3,-2*math.pi/3)]
  put(folder/'rest.obj',obj(rest));put(folder/'prescribed_close.obj',obj(meshes))
  put(folder/'stack_section.obj',obj([ribbon(0,0,j)for j in range(8)]))
  config=dict(scope='Concept Design + implemented mesh loading geometry;NOT validated shell/contact mechanics',length_mm=100,body_radius_mm=50,width_mm={'root':24,'tip':12,'taper_start':50},layers=8,film_thickness_mm=.05,physical_measurements=None,angles_deg=[0,120,-120],curl_rad=.77,tendon_offset_mm=1.5,tendon_pull_mm=1.5*.77,edge_tendons_per_finger=2,vacuum_zones_mm=[[0,30],[35,65],[70,100]]if selective else[[0,100]],vacuum_circuits=3,independent_finger_zone_control=False,object={'shape':'sphere','radius_mm':20,'center_mm':[0,-75,0]},root_cartridge='split clamp with serviceable film insert',seal='separate pouches,5mm flexible bridges'if selective else'full sleeve',open_issues=['transverse shell compliance','vacuum seal leakage','edge cable friction','hose routing','wear','layer-end sliding','post-jam load transfer'])
  js(folder/'parameters.json',config)
  vertices=[p for v,f in rest for p in v];triangles=[];offset=0
  for v,f in rest:
   triangles.extend(tuple(offset+i for i in face)for face in f);offset+=len(v)
  positions=' '.join(str(x)for p in vertices for x in p);indices=' '.join(str(i)for t in triangles for i in t)
  # Inline EXACT same OBJ geometry;matching SDK lacks IO.Mesh plugin.
  scene=f'''<Node name="{name}_geometry_only" gravity="0 0 0"><RequiredPlugin pluginName="Sofa.Component.AnimationLoop Sofa.Component.Topology.Container.Constant Sofa.Component.StateContainer"/><DefaultAnimationLoop/><MeshTopology position="{positions}" triangles="{indices}"/><MechanicalObject template="Vec3d" position="{positions}"/></Node>'''
  put(folder/'geometry.scn',scene)
  lines=[]
  for v,f in meshes:
   lines += [[v[i*5+j]for i in range(21)]for j in (0,2,4)]
   lines += [[v[i*5+j]for j in range(5)]for i in (0,6,13,20)]
  candidate_lines.append((name+' prescribed curl',lines,[0,0,0]))
  minimum=min(2*math.sqrt(v[i*5+2][0]**2+v[i*5+2][2]**2)*math.sin(math.pi/3)-width(i*5)for v,f in meshes for i in range(21))
  area=3*(50*24+50*(24+12)/2);volume=area*8*.05
  baseline_volume=3*100*2*b['equivalent_beam_area_per_layer_mm2']
  comparison.append(dict(candidate=name,nominal_surface_area_mm2=area,actual_contact_area_mm2=None,film_volume_mm3=volume,baseline_equivalent_beam_volume_mm3=baseline_volume,material_volume_ratio=volume/baseline_volume,equal_material_film_thickness_mm=baseline_volume/(area*8),sampled_width_clearance_mm=minimum,clearance_scope='same-material-station center separation minus width;not all-pairs collision proof',tendon_pull_mm=config['tendon_pull_mm'],grasp_force=None,pressure_distribution=None,hold_energy=None))
 put(base/'visualizations'/args.tag/'assembly_views.svg',drawing(b,candidate_lines));put(base/'visualizations'/args.tag/'mechanism_section.svg',mechanism())
 zones=[[0,30,16],[30,100,1]];Coff=compliance([[0,100,1]]);Cselect=compliance(zones);Con=compliance([[0,100,16]])
 js(base/'visualizations'/args.tag/'comparison.json',dict(source='geometry and analytical assumed constant-width EB screening;NO SOFA contact performance',baseline=b['source_sha256'],candidates=comparison,assumed_EI_multiplier=16,compliance_per_tip_force={'OFF':Coff,'proximal30_ON':Cselect,'all_ON':Con},selective_stiffness_ratio=Coff/Cselect,full_stiffness_ratio=Coff/Con,limitations=['EB screen uses uniform24mm width,not tapered mesh','mass,area and drive conditions are not yet matched for performance comparison','pressure-to-stiffness uncalibrated','unbonded vs perfectly bonded EI ratio N^2 is only a theoretical bound']))
 print(json.dumps(dict(version=args.tag,baseline_radius=b['root_radius_mm'],candidates=comparison,EB_selective_ratio=Coff/Cselect),indent=2))
if __name__=='__main__':main()
