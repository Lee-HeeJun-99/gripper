"""Continuous local aperture lower bound, not sampled 3D motion clearance."""
import argparse,json,math,shutil
from pathlib import Path
from baseline_registry import ROOT,ref,dump
def main():
    p=argparse.ArgumentParser();p.add_argument('--candidate',required=True);p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'validation/worst_case'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    source=ROOT/'cad/exports'/a.candidate/'summary.json';d=json.loads(source.read_text());f=d['funnel_profile'];cx=f['center_X_mm'];rf=f['radius_mm'];u_max=5.;Rmin=88/math.radians(60);dmax=.21/2+.32
    # Aperture A=neutral-R+sqrt((R-d)^2-u^2) - [cx+sqrt(rf^2-u^2)+frontfloat].
    # R-d>=rf ensures A(u)>=A(0), via rationalized square-root differences.
    # At u=0, tr cancels EXACTLY with frontfloat=.20-tr; tp maximum is worst.
    assert Rmin-dmax>=rf>u_max
    stock_min=50.3-.32-(cx+rf);profile_budget=.010
    lower=stock_min-profile_budget
    result=dict(status='PASS' if lower>=.100-1e-12 else 'FAIL',scope='CONTINUOUS CONFORMING-CIRCULAR-RAIL / CORRELATED STOCK APERTURE ONLY, NOT FREE PET OR 3D CCD',
        ranges=dict(angle_deg=[0,60],channel_axial_u_mm=[0,5],PET_mm=[.28,.32],rail_mm=[.19,.21],frontfloat_mm='0.20 - actual rail thickness'),
        analytical_nominal_profile_lower_mm=stock_min,proposed_normal_profile_error_budget_mm=profile_budget,conditional_manufactured_lower_mm=lower,required_lower_mm=.100,
        proof=['R-d >= rf on the entire domain; sqrt(a*a-u*u)-a=-u*u/(sqrt(a*a-u*u)+a)',
          'For a>=rf, aperture(u)-aperture(0)>=0, so no axial grid is required',
          'At u=0, rail thickness cancels with the actual correlated front float; maximum PET thickness is worst'],
        source=ref(source),producer=ref(out/'producer.py'),manufacturing_profile_tolerance_is_requirement_not_measurement=True,
        does_not_qualify=['Actual independent PET equilibrium/friction','Whole terminal toolpaths/strength','Full assembly motion, tolerances or hardware'])
    dump(out/'summary.json',result)
    # Partial manufacturing view, native vector directly from actual CAD profile.
    drawing=ROOT/'cad/drawings'/a.tag;drawing.mkdir(parents=True,exist_ok=False)
    points=[]
    for i in range(101):
        z=-95+i*.05;x=cx+math.sqrt(rf*rf-(z+95)**2);points.append(f'{80+(x-48.5)*120:.5f},{700-(z+95)*100:.5f}')
    svg='<svg xmlns="http://www.w3.org/2000/svg" width="900" height="800" viewBox="0 0 900 800"><rect width="900" height="800" fill="white"/><g font-family="sans-serif" font-size="18" fill="black"><text x="30" y="35">Rev AD local inner lip profile - mm - CANDIDATE ONLY</text><text x="30" y="65">CNC profile error requirement +/-0.010 normal; not process qualification</text><text x="30" y="95">R='+str(round(rf,6))+'; centre X='+str(round(cx,6))+', Z=-95; Y=-6.6..+6.6</text><text x="30" y="125">Partial view only. Use actual referenced STEP for all other geometry.</text><text x="370" y="220">Z=-90: X='+str(round(cx+math.sqrt(rf*rf-25),6))+'</text><text x="370" y="700">Z=-95: X='+str(round(cx+rf,6))+'</text><text x="30" y="760">Retain lip; do not remove contact function to create clearance.</text></g><polyline points="'+' '.join(points)+'" stroke="black" stroke-width="3" fill="none"/></svg>'
    (drawing/'FUNNEL_PROFILE.svg').write_text(svg)
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
