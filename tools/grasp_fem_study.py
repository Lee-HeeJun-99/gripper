"""Independent FEM assumptions, NOT SOFA/real-film measurements."""
from dataclasses import replace
from models.multilayer.beam import Design,solve
from grasp_common import ROOT,OUT,write_json,sha,provenance

def main():
    out=OUT/'fem';out.mkdir(exist_ok=False);rows=[]
    for family in ('validated_equivalent_section','fixed_per_layer_rectangle','fixed_total_area_vary_width','fixed_stack_height'):
        for layers in (2,4,8):
            thickness=.8/layers if family=='fixed_stack_height' else .4
            area=.7322329862910148 if family=='validated_equivalent_section' else (6.4/layers if family=='fixed_total_area_vary_width' else 8*thickness)
            inertia=.04266666666666668 if family=='validated_equivalent_section' else area*thickness**2/12
            d=Design(layers=layers,nodes=21,thickness=thickness,area=area,inertia=inertia,coupling=0)
            off=solve(d)
            for k in (0,1,100):
                on=solve(replace(d,coupling=k));status='PASS' if on['small_rotation_validated'] and on['normalized_residual']<1e-3 else 'FAIL'
                rows.append(dict(family=family,layers=layers,k=k,total_area_mm2=layers*area,total_assumed_stack_height_mm=layers*thickness,area_per_layer=area,inertia_per_layer=inertia,centroid_pitch=thickness,status=status,ratio=off['deflection_mm']/on['deflection_mm'] if status=='PASS' else None,result=on))
    d=Design(layers=2,nodes=21,coupling=1);sensitivity=[]
    for parameter,values in [('young',[200.,250.,300.]),('coupling',[.1,1.,10.]),('thickness',[.36,.4,.44])]:
        for value in values:sensitivity.append(dict(parameter=parameter,value=value,result=solve(replace(d,**{parameter:value}))))
    write_json(out/'summary.json',dict(rows=rows,sensitivity=sensitivity,scope='independent static EB FEM under explicitly assumed research sections; varying pitch alone is NOT varying material thickness',fem_source_sha256=sha(ROOT/'models/multilayer/beam.py'),provenance=provenance()))
    print(len(rows),'independent FEM comparisons',sum(r['status']=='PASS' for r in rows),'PASS')

if __name__=='__main__':main()
