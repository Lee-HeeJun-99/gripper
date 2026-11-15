import json,xml.etree.ElementTree as ET
from curve_common import OUT,write_json
from history_assess import comparison
from birth_assess import same_physics,observables
def layout_signature(name):
    path=OUT/'grasp'/name;c=json.loads((path/'config.json').read_text());n=c['nodes'];body=ET.parse(path/'scene.scn').getroot().find('Node');signature={'connectors':[],'cables':[]}
    for layer in body.findall('FrameLayerNetwork'):
        ids=list(map(int,layer.get('connectorIndices','').split()))or list(range(1,n));positions=[i*float(layer.get('length'))/(n-1)for i in ids]
        signature['connectors'].append(dict(positions=positions,attributes={k:v for k,v in layer.attrib.items()if k not in('name','filename','stride','nodesPerLayer','startIndex','connectorIndices')}))
    for cable in body.findall('RoutedCable'):
        ids=list(map(int,cable.get('route').split()));signature['cables'].append(dict(material_positions=[(i//n,(i%n)*100/(n-1))for i in ids],attributes={k:v for k,v in cable.attrib.items()if k not in('name','route')}))
    return signature
def main():
    cases={};checks={}
    for p in(OUT/'grasp').glob('*/metrics.json'):
        r=json.loads(p.read_text())
        if not r['config']['profile_only']:cases[p.parent.name]=r
    for a,b,limit in(('n11','n21',.01),('n21','n41',.01),('n11','fixed_n21',.01),('fixed_n21','fixed_n41',.01),('n11','halfdt',.001),('mass_n11','mass_n21',.01),('mass_n21','mass_n41',.01)):
        name=a+'_'+b
        if a not in cases or b not in cases:checks[name]=dict(status='NOT RUN');continue
        x,y=cases[a],cases[b];same_physics(x,y)
        if x['config'].get('mass_quadrature','inherited_equal_mass_per_node')!=y['config'].get('mass_quadrature','inherited_equal_mass_per_node'):raise ValueError('mass quadrature schemes differ')
        if x['identity']['curved']!=y['identity']['curved']:raise ValueError('compiled models differ')
        if not(x.get('bounded_hold_pass')and y.get('bounded_hold_pass')):checks[name]=dict(status='FAIL',reason='underlying physical gate',cases=[a,b]);continue
        r=comparison(x,y,limit);r['physical_layout_invariant']=layout_signature(a)==layout_signature(b);r['observables']={};oa,ob=observables(OUT/'grasp'/a),observables(OUT/'grasp'/b)
        for k in oa:
            rel=abs(oa[k]-ob[k])/abs(ob[k])if ob[k]else(0 if oa[k]==0 else None);r['observables'][k]=dict(absolute=abs(oa[k]-ob[k]),relative=rel)
        d=r['observables']['friction_dissipation']['relative'];r['loss_status']='PASS'if d is not None and d<=limit else'FAIL';checks[name]=r
    mass_pairs=[checks[n]for n in('mass_n11_mass_n21','mass_n21_mass_n41')];qualified=all(r['status']=='PASS'and r.get('loss_status')=='PASS'and r.get('physical_layout_invariant')for r in mass_pairs)
    result=dict(status='FAIL'if any(r['status']=='FAIL'or r.get('loss_status')=='FAIL'for r in checks.values())else'EXPERIMENTAL',derived_mass_spatial_gate='PASS'if qualified else'FAIL'if any(r['status']=='FAIL'or r.get('loss_status')=='FAIL'for r in mass_pairs)else'NOT RUN',comparisons=checks,cases={n:{k:r.get(k)for k in('status','bounded_hold_pass','hold_displacement_mm','hold_rotation_increment_rad','global_force_residual','global_moment_residual','process','failure_reason')}for n,r in cases.items()},scope='new director-Hermite component,normal/tangent fixed material midpoint quadrature;1percent unchanged;no global grasp or energy qualification',grasp_optimization='BLOCKED')
    write_json(OUT/'assessment.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
