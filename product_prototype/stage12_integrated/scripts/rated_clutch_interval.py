"""New complete catalog clutch interval, not HPMC minimum-rating reuse.

JH-1M published torque tolerance is an ambient/catalog design input, NOT a
certified all-temperature/fault/transient maximum. Actual mounting drawing
was not visually retrieved; ambiguous thread text is deliberately not used.
"""
import argparse,json,math,shutil
from baseline_registry import ROOT,S2,ref,dump
from jam_energy import peak
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'validation/overload'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    jsrc=ROOT/'validation/overload/AH_load_window1/summary.json';J=json.loads(jsrc.read_text())['conditional_partial_loadside_J_kg_m2']
    prev=S2/'validation/worst_case/jam_reference1/summary.json';old=json.loads(prev.read_text());factor=old['idler_runout_bending_reference_Pa']/old['ideal_reference_tension_N']
    tau=[(.064-.007),(.064+.007)];r=.011165;F=tau[1]/r;rows=[]
    for rpm in (0.,60.):
        peakN=peak(F,.968626,10000,J,rpm*2*math.pi/60)
        rows.append(dict(scenario_rpm=rpm,conditional_partial_J_kg_m2=J,assumed_k_N_m=10000,initial_scenario_tension_N=.968626,constant_catalog_force_N=F,conditional_peak_N=peakN,idler_nominal_bending_reference_Pa=factor*peakN,required_minimum_yield_for_SF2_without_notch_Pa=2*factor*peakN))
    assert tau[0]>0 and F>0 and rows[1]['conditional_peak_N']>=rows[0]['conditional_peak_N']
    result=dict(status='CATALOG_INTERVAL_REQUIREMENTS_COMPUTED',scope='New manufacturer complete-clutch torque interval and conditional structural demand only',producer=ref(out/'producer.py'),
        manufacturer=dict(model='WM Berg JH-1M',source='https://www.wmberg.com/documentation/metric-catalog/section-g_metric.aspx?ext=.pdf',catalog_page='MG37 / PDF page37, index36',retrieved='2026-11-26',published_torque_Nm=.064,published_tolerance_Nm=.007,published_bore_mm=[3,3.02],OD_mm=16,length_mm=26.7,availability_and_price='NOT CONFIRMED',mounting_thread='NOT USED: parsed pitch text ambiguous; screenshot/cache miss and direct PDF403 preserved in report'),
        torque_interval_Nm=tau,minimum_static_reference_force_at_nominal_radius_N=tau[0]/.01125,maximum_catalog_static_reference_force_N=F,rows=rows,
        partial_inertia_source=ref(jsrc),idler_reference=ref(prev),
        compatibility='Existing5mm motor shaft is NOT compatible with3mm clutch bore; no implicit adapter, drilling-out, supplier special bore or installed CAD is claimed.',
        difference='Published complete-unit nominal torque WITH tolerance; not a minimum-only hysteresis rating or uncalibrated adjustable-friction setting',
        unresolved=['Manufacturer temperature/rate/slip-energy/response bounds','Actual output inertia and wire EA','Actual complete mounting drawing and input/output coupling interfaces','Bearing seizure/fault envelope vs normal catalog slip condition','Candidate-matched reinforced Idler and material/notch/fatigue proof'],product_force_cap_qualified=False,whole_system_release=False)
    dump(out/'summary.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
