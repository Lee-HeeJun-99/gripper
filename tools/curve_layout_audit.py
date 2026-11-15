import json,xml.etree.ElementTree as ET
from curve_common import OUT,write_json
def main():
    rows={}
    for n in(11,21,41):
        p=OUT/'grasp'/('n'+str(n))/'scene.scn'
        if not p.exists():continue
        body=ET.parse(p).getroot().find('Node');layers=[]
        for layer in body.findall('FrameLayerNetwork'):
            ids=list(map(int,layer.get('connectorIndices','').split()))or list(range(1,n));L=float(layer.get('length'));k=float(layer.get('stiffness'));kn=float(layer.get('normalStiffness'));positions=[i*L/(n-1)for i in ids];weights=[]
            for j,x in enumerate(positions):
                left=(positions[j-1]+x)/2 if j else 0.;right=(x+positions[j+1])/2 if j+1<len(ids)else L;weights.append(right-left)
            layers.append(dict(point_count=len(ids),coordinates_mm=positions,uniform_relative_slip_energy_for_1e_minus6_mm=.5*k*len(ids)*1e-12,total_point_tangent_stiffness=k*len(ids),total_point_normal_stiffness=kn*len(ids),pressure_tributary_lengths=weights,total_tributary_length=sum(weights)))
        rows[str(n)]=dict(layers=layers,cable_guide_counts=[len(c.get('route').split())for c in body.findall('RoutedCable')])
    result=dict(status='FAIL',origin='actual scene and force-law audit;not a dynamics result',reason='default all-nonroot connectors keep point stiffness while their count changes;not fixed physical connector layout under mesh refinement',cases=rows,law_source='models/integrated/Components.cpp LayerNetwork and models/closure_frame/FrameLayer.cpp; stiffness explicitly Point shear stiffness',proposed_control='preserve10point connectors and11cable guides at original10mm material coordinates;do not rescale stiffness or alter old results')
    path=OUT/'layout_audit.json'
    if path.exists():raise FileExistsError(path)
    write_json(path,result);print({n:(r['layers'][0]['total_point_tangent_stiffness'],r['layers'][0]['total_point_normal_stiffness'],r['cable_guide_counts'][0])for n,r in rows.items()})
if __name__=='__main__':main()
