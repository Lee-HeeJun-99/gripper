"""Primary-drawing clearance GAUGE, not invented manufacturer internal CAD."""
import argparse,csv,json,sys,shutil,math
from pathlib import Path
from baseline_registry import ROOT,S1,ref,dump,sha
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,export,common,volume,bounds,overlap
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from OCP.gp import gp_Ax2,gp_Pnt,gp_Dir
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'cad/exports'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    diameter=1.250*25.4;length=1.803*25.4
    # Deliberately conservative full-OD envelope including shaft ends. It may
    # produce false-positive clearance failures, never proof of real solid overlap.
    gauge=BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(80,-12.5-length,20),gp_Dir(0,1,0)),diameter/2,length).Shape()
    export(gauge,out/'HPMC_CLEARANCE_GAUGE');hits=[];cutset=[]
    for row in csv.DictReader((S1/'bom/revAA_mbd1/STAGE1_BOM.csv').open()):
        name=row['part_ID']
        if name.startswith('F0_COUPLING_'):cutset.append(name);continue
        path=S1/row['STEP'];assert sha(path)==row['STEP_SHA256'];part=read(path)
        if overlap(bounds(gauge),bounds(part)):
            v=common(gauge,part)
            if abs(v)>1e-8:hits.append(dict(part=name,gauge_common_mm3=v))
    torque=2.5*.00706155183333;J=3.8e-6*.1129848290276
    result=dict(status='LIMITER_NOT_QUALIFIED',scope='CONSERVATIVE ENVELOPE / INTERFACE SCREEN, NOT SELECTED PART OR PRODUCT REVISION',
        source_drawing='https://www.magtrol.com/wp-content/uploads/hpmc-25.pdf',drawing_revision='B',
        gauge_STEP=ref(out/'HPMC_CLEARANCE_GAUGE.step'),gauge_STL=ref(out/'HPMC_CLEARANCE_GAUGE.stl'),
        dimensions=dict(OD_mm=diameter,overall_length_mm=length,input_nominal_diameter_mm=.1250*25.4,output_diameter_interval_mm=[.1246*25.4,.1248*25.4]),
        current_coupling_length_mm=19.5,extra_axial_space_mm=length-19.5,current_interfaces_mm=[5.,4.4],
        declared_service_cutset=cutset,retained_parts_with_gauge_overlap=hits,
        published_minimum_torque_Nm=torque,published_maximum_torque_Nm=None,
        nominal_external_inertia_kg_m2=J,published_acceleration_consistency_relative=abs(torque/J/41100-1),
        product_force_cap_certified=False,hardware_measured=False,
        missing=['Guaranteed maximum torque vs temperature/speed and uncertainty','Mounting adaptation from3.175mm to5/4.4mm and actual mechanical support','Complete driven inertia / cable EA / transient allowance','Maximum normal grasp demand and certified structural upper load'],
        next='Manufacturer certified maximum/drawing confirmation or independently calibrated limiter design; do not turn minimum rating into maximum',producer=ref(out/'producer.py'))
    dump(out/'summary.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
