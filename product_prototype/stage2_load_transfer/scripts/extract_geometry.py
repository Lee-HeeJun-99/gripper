"""Read-only Rev AA BRep integrals. Unit-density inertia is NOT physical inertia."""
import argparse, csv, hashlib, json, platform, sys
from pathlib import Path
import numpy as np
from OCP.STEPControl import STEPControl_Reader
from OCP.IFSelect import IFSelect_RetDone
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID

ROOT = Path(__file__).resolve().parents[1]
S1 = ROOT.parent / 'stage1_manufacturing'
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path):
    r = STEPControl_Reader()
    assert r.ReadFile(str(path)) == IFSelect_RetDone
    r.TransferRoots()
    return r.OneShape()
INTEGRATION_EPS = 1e-10
def properties(shape):
    p = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, p, INTEGRATION_EPS)
    c, j = p.CentreOfMass(), p.MatrixOfInertia()
    return p.Mass()*1e-9, np.array([c.X(),c.Y(),c.Z()])*1e-3, np.array([[j.Value(i+1,k+1) for k in range(3)] for i in range(3)])*1e-15
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--tag',required=True);args=parser.parse_args()
    out = ROOT/'models/geometry'/args.tag
    out.mkdir(parents=True, exist_ok=False)
    bom = S1/'bom/revAA_mbd1/STAGE1_BOM.csv'
    rows = list(csv.DictReader(bom.open()))
    records = []
    for row in rows:
        path = S1/row['STEP']
        assert sha(path) == row['STEP_SHA256'], row['part_ID']
        shape = load(path)
        vol, center, inertia = properties(shape)
        ex = TopExp_Explorer(shape,TopAbs_SOLID); n = 0
        while ex.More(): n += 1; ex.Next()
        assert BRepCheck_Analyzer(shape).IsValid() and n == 1 and vol > 0
        assert np.linalg.eigvalsh(inertia).min() > 0
        material = row['material']
        # Threaded hardware, purchased bearings, motors and stranded rope are
        # deliberately not assigned a uniform density from exterior CAD.
        exact_stock = row['make_or_buy'] == 'MAKE' and not any(x in row['part_ID'] for x in ('WIRE','TENDON','MOTOR'))
        records.append(dict(part_ID=row['part_ID'],material=material,volume_m3=vol,
            centroid_m=center.tolist(),central_geometric_inertia_m5=inertia.tolist(),
            uniform_density_candidate=exact_stock,physical_mass_status='UNASSIGNED',
            STEP_SHA256=sha(path),STEP=str(path.relative_to(ROOT.parent.parent))))
    total = sum(x['volume_m3'] for x in records)
    center = sum(x['volume_m3']*np.array(x['centroid_m']) for x in records)/total
    inertia = np.zeros((3,3))
    for x in records:
        d = np.array(x['centroid_m'])-center
        inertia += np.array(x['central_geometric_inertia_m5'])+x['volume_m3']*(d@d*np.eye(3)-np.outer(d,d))
    assembly = S1/'cad/assembly/revAA_mbd1/ASSEMBLY.step'
    av, ac, ai = properties(load(assembly))
    errors = dict(volume_relative=abs(av-total)/total,centroid_m=float(np.linalg.norm(ac-center)),
                  inertia_relative=float(np.linalg.norm(ai-inertia)/np.linalg.norm(ai)))
    result = dict(scope='GEOMETRIC INTEGRALS ONLY; NOT PHYSICAL MASS QUALIFICATION',case='revAA_heel_relief2',
        CAD_length_unit='mm',output_units='m, m^3, m^5',parts=records,
        assembly_volume_m3=av,assembly_centroid_m=ac.tolist(),assembly_geometric_inertia_m5=ai.tolist(),
        independent_parallel_axis_errors=errors,part_count=len(records),
        acceptance={'part_count':304,'volume_relative_max':1e-8,'centroid_m_max':1e-9,'inertia_relative_max':1e-8},
        integration_relative_requested=INTEGRATION_EPS,
        status='PASS' if len(records)==304 and errors['volume_relative'] < 1e-8 and errors['centroid_m'] < 1e-9 and errors['inertia_relative'] < 1e-8 else 'FAIL',
        hashes={'source':sha(Path(__file__)),'BOM':sha(bom),'assembly':sha(assembly)},
        python=platform.python_version(),command='PYTHONPATH=/tmp/regrip_stage1_ocp /home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/stage2_load_transfer/scripts/extract_geometry.py --tag '+args.tag)
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('parts','assembly_geometric_inertia_m5')},indent=2))
if __name__ == '__main__': main()
