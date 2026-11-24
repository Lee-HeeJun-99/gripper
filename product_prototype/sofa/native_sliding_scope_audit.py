"""Bounded read-only alternative API audit; do not disguise a joint as contact."""
import argparse,json
from pathlib import Path
from analyse import BASE,sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);sdk=Path('/home/ubuntu/SOFA/v26.06.00');folder=sdk/'include/Sofa.Component.Constraint.Lagrangian.Model/sofa/component/constraint/lagrangian/model';paths=[folder/'SlidingLagrangianConstraint.h',folder/'SlidingLagrangianConstraint.inl',sdk/'share/sofa/examples/Component/Constraint/Lagrangian/SlidingLagrangianConstraint.scn'];records=[]
 for f in paths:
  text=f.read_text();records.append(dict(path=str(f),sha256=sha(f),relevant_lines=[dict(line=i,text=s.strip()) for i,s in enumerate(text.splitlines(),1) if any(x in s for x in ('sliding_point','axis_1','axis_2','BilateralConstraintResolution','UnilateralConstraintResolution','m_projectionBarycentricCoordinate','m_constraintDirections.push_back','SlidingLagrangianConstraint name='))]))
 d=dict(status='BLOCKED_AS_FINITE_WIRE_SURFACE_CONTACT_REPLACEMENT',alternative='Installed documented SlidingLagrangianConstraint (Vec3 point/finite segment)',actual_Native_run=False,reason='It supplies2bilateral transverse rows and2unilateral endpoint rows for a designated point/segment. No finite wire radius, bore clearance, rolling/friction or documented automatic material-segment reassociation. It may represent a deliberately idealized captured joint, NOT the current loose finite bore or contact normal refresh. Replacing actual surface collision with it would add unsupported transverse support. No equivalent-coupon claim or SDK edits.',records=records,scope='New alternative contract scope audit only,not repeated1678normal-API scan or proof every stockSOFA representation is impossible. Do not launch a cosmetic joint coupon as wire sliding/grasp evidence.',source_sha256=sha(Path(__file__)));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in d.items() if k!='records'},indent=2))
if __name__=='__main__':main()
