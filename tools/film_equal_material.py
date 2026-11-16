"""Equal-solid-volume skin/rail CONCEPT; EB bounds are not jamming/grasp results."""
import argparse,json,math
from design_regrip import ROOT,baseline,ribbon,obj,put,js,width
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
 if not a.tag.replace('_','').isalnum():raise ValueError('tag')
 b=baseline();target=600*b['equivalent_beam_area_per_layer_mm2'];skin_area=6300;ts=.05;tr=.1;rail=(target-skin_area*ts)/(3*2*100*tr)
 if rail<=0 or 4*rail>=12:raise ValueError('rails do not fit distal skin')
 folder=ROOT/'designs/film_contact'/a.tag
 skin=[ribbon(angle,0)for angle in (0,2*math.pi/3,-2*math.pi/3)]
 rails=[]
 for mesh in skin:
  v,_=mesh
  for side in (-1,1):
   points=[]
   for i in range(21):
    left=v[5*i];right=v[5*i+4];center=v[5*i+2];w=width(5*i);direction=[(right[j]-left[j])/w for j in range(3)]
    # Near-edge narrow backing strips,finite thickness parameter,not thickened Beam.
    normal=[center[0]/50,0,center[2]/50]
    for offset in (side*(w/2-rail),side*w/2):points.append([center[j]+offset*direction[j]+(ts+tr)/2*normal[j]for j in range(3)])
   faces=[]
   for i in range(20):faces.extend([(2*i,2*i+1,2*i+2),(2*i+1,2*i+3,2*i+2)])
   rails.append((points,faces))
 put(folder/'skin.obj',obj(skin));put(folder/'backing_rails.obj',obj(rails))
 configs=dict(scope='Concept geometry and independent EB upper/lower bounds;NOT laminate SOFA or proven grasp',reference_baseline_source_sha256=b['source_sha256'],length_mm=100,body_radius_mm=50,skin_thickness_mm=ts,backing_thickness_mm=tr,rail_width_mm=rail,skin_layers=1,backing_rails_per_finger=2,skin_area_mm2=skin_area,volume_mm3=skin_area*ts+3*2*100*tr*rail,baseline_volume_mm3=target,volume_ratio=(skin_area*ts+3*2*100*tr*rail)/target,density_measured=None,notes=['Equal solid volume is equal mass ONLY if density matches','Root split clamp,edge tendon eyes and sleeves are additional mass,not counted','Two-layer overlap only under rails;NOT eight-layer film cartridge','Pressure/friction/tear/seal and actuator data unknown'])
 js(folder/'parameters.json',configs)
 def EI(s,bonded):
  w=width(s);As=w*ts;Ar=2*rail*tr;zs=ts/2;zr=ts+tr/2;zbar=(As*zs+Ar*zr)/(As+Ar)
  I=w*ts**3/12+2*rail*tr**3/12
  if bonded:I+=As*(zs-zbar)**2+Ar*(zr-zbar)**2
  return 250*I
 zones={'OFF':[],'full_bonded_upper_bound':[(0,100)],'proximal_upper_bound':[(0,30)],'distal_upper_bound':[(70,100)],'proximal_middle_upper_bound':[(0,65)]}
 C={}
 for name,intervals in zones.items():
  C[name]=sum((100-(i+.5)*.01)**2/EI((i+.5)*.01,any(l<=(i+.5)*.01<=u for l,u in intervals))*.01 for i in range(10000))
 js(folder/'section_bounds.json',dict(source='Independent variable-width Euler-Bernoulli integration,not SOFA. Perfect bonding is only an upper bound,not a pressure calibration.',assumed_E=250,compliance=C,ratios={k:C['OFF']/v for k,v in C.items()},actuator_force=None,grasp_load=None,contact_area=None))
 svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="440"><rect width="1100" height="440" fill="white"/><g font-family="sans-serif"><text x="25" y="30" font-size="21">Equal-volume skin + backing-rail cartridge — CONCEPT, not SOFA deformation</text><rect x="40" y="90" width="700" height="22" fill="#8dc5cb" stroke="#333"/><rect x="40" y="112" width="{700*rail/24}" height="44" fill="#dfb77d" stroke="#333"/><rect x="{740-700*rail/24}" y="112" width="{700*rail/24}" height="44" fill="#dfb77d" stroke="#333"/><text x="40" y="195">Skin: 0.05 mm. Two backing rails: 0.10 mm × {rail:.5f} mm. Width 24→12 mm.</text><text x="40" y="230">Total solid volume {target:.5f} mm³ = extracted equivalent Beam baseline (density unmeasured).</text><text x="40" y="265">Root split clamp / sliding rail ends / two edge string guides / common equalizer.</text><text x="40" y="300">Optional proximal mechanical pinch latch; three-zone vacuum NOT the 5-day default.</text><text x="40" y="335">Section thickness amplified. Clamp, sleeve, guide and actuator mass not included.</text><text x="40" y="370">No demonstrated pressure calibration, holding-force advantage or laminate friction yet.</text></g></svg>'''
 put(folder/'section.svg',svg);print(json.dumps(dict(folder=str(folder),parameters=configs,section_ratio={k:C['OFF']/v for k,v in C.items()})))
if __name__=='__main__':main()
