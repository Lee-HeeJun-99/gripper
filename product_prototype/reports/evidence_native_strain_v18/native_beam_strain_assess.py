"""High-precision algebraic projection contrast,not replacement native physics."""
import argparse,csv,json
from decimal import Decimal,localcontext
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from native_bending_coupon import BASE,sha

def exact(x):return Decimal.from_float(float(x))

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);source=BASE/'results/native_beam_strain470';meta=json.loads((source/'summary.json').read_text());records=[]
    for item in meta['records']:
        assert item['actual_position_error_m']==0 and item['native_force_reproduction_error_N']==0
        nx=item['nx'];case=source/f'{nx}_{item["variant"]}';node=ET.parse(case/'scene.scn').getroot().find('./Node');q=np.fromstring(node.find('NativeBeamStrainObserver').get('privatePositions'),sep=' ').reshape(-1,7);rows=list(csv.DictReader((case/'PRIVATE_native_strain.csv').open()));comparison=[];difference=np.zeros((nx,3))
        with localcontext() as ctx:
            ctx.prec=70
            for row in rows:
                i,j=int(row['node0']),int(row['node1']);axis=np.array([float(row[k]) for k in ('axis_x','axis_y','axis_z')]);projection=sum((exact(axis[k])*(exact(q[j,k])-exact(q[i,k])) for k in range(3)),Decimal(0));rest=exact(row['rest1_x_m'])-exact(row['rest0_x_m']);delta=projection-rest
                native=exact(row['delta_axial_m']);error=float(native-delta);force_error=float((native-delta)*exact(row['EA_N'])/exact(row['L_m']));difference[i]+=force_error*axis;difference[j]-=force_error*axis
                comparison.append(dict(beam=int(row['beam']),native_delta_m=float(native),decimal_projection_delta_m=str(delta),native_minus_decimal_m=error,axial_force_contrast_N=force_error))
        fixed=np.fromstring(node.find('FixedProjectiveConstraint').get('indices'),sep=' ',dtype=int);free=np.ones(nx,dtype=bool);free[fixed]=False
        (out/f'{nx}_{item["variant"]}.json').write_text(json.dumps(comparison,indent=2));records.append(dict(nx=nx,variant=item['variant'],max_native_vs_projection_delta_m=max(abs(r['native_minus_decimal_m']) for r in comparison),assembled_free_force_contrast_N=float(np.linalg.norm(difference[free])),source_csv_sha256=sha(case/'PRIVATE_native_strain.csv'),source_scene_sha256=sha(case/'scene.scn')))
    result=dict(scope='70digit algebraic projection contrast at PRIVATE poses;NOT alternative equilibrium,force implementation,or proven correction',producer_sha256=sha(Path(__file__)),source_summary_sha256=sha(source/'summary.json'),assumptions='No endpoint offsets;fixed Native midpoint axis coefficients held as exact binary64 inputs. Does not recompute quaternion/spline geometry at70digits;not an exact continuum reference.',records=records,decision='Native axial transformation/coordinate representation is sensitive at strict residual scale. No force replacement,rounding floor,tolerance change or corrected state adopted;fine mesh remains unqualified.')
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':main()
