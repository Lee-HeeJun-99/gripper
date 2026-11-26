"""Read-only source reconciliation. Never inherit an assembly approval by part hash alone."""
import argparse,csv,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT.parent
REPO=PROJECT.parent
S1=PROJECT/'stage1_manufacturing'
S2=PROJECT/'stage2_load_transfer'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return dict(path=str(p.relative_to(REPO)),SHA256=sha(p))
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def build():
    geometry=S2/'models/geometry/revAA_extract2/summary.json'
    g=json.loads(geometry.read_text());byid={p['part_ID']:p for p in g['parts']}
    bom=S1/'bom/revAA_mbd1/STAGE1_BOM.csv'
    rows=list(csv.DictReader(bom.open()));parts=[]
    for row in rows:
        p=S1/row['STEP'];geom=byid[row['part_ID']]
        assert sha(p)==row['STEP_SHA256']==geom['STEP_SHA256']
        parts.append(dict(part_ID=row['part_ID'],STEP=ref(p),material_requirement=row['material'],
            geometry={k:geom[k] for k in ('volume_m3','centroid_m','central_geometric_inertia_m5')},
            physical_mass_kg=None,physical_inertia_kg_m2=None,material_certificate=None,
            interface_definition=row['interface_notes'],load_ports_status='UNMAPPED',
            reuse_rule='Geometry only. Changed material, interfaces, loads or contacts invalidate physical evidence even if STEP unchanged.'))
    return dict(revision='revAA_heel_relief2',package='revAA_mbd1',adopted_design=True,
        source_HEAD=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
        assembly=ref(S1/'cad/assembly/revAA_mbd1/ASSEMBLY.step'),BOM=ref(bom),geometry_source=ref(geometry),
        stage1_release=ref(S1/'validation/release_revAA2/summary.json'),
        stage2_registry=ref(S2/'models/analytical/release_registry.json'),
        criteria=ref(S2/'models/analytical/criteria.json'),
        candidate_only=['revAB_sliding_pet1'],parts=parts,
        stage1_scope='UNPOWERED FIRST-ARTICLE ENGINEERING DESIGN ONLY',
        hardware_status='HARDWARE_NOT_MEASURED',manufacturing_status='MANUFACTURING_PROCESS_NOT_QUALIFIED',
        powered_status='POWERED_OPERATION_NOT_AUTHORIZED')
def integrity(doc):
    errors=[]
    for key in ('assembly','BOM','geometry_source','stage1_release','stage2_registry','criteria'):
        r=doc[key];p=REPO/r['path']
        if not p.is_file() or sha(p)!=r['SHA256']:errors.append(key+': missing/stale')
    ids=[]
    for part in doc['parts']:
        ids.append(part['part_ID']);r=part['STEP'];p=REPO/r['path']
        if not p.is_file() or sha(p)!=r['SHA256']:errors.append(part['part_ID']+': geometry invalidated')
    if len(ids)!=304 or len(set(ids))!=304:errors.append('part inventory missing/duplicate')
    return errors
def invalidated(old,new):
    """Explicit dependency dimensions; unchanged STEP never implies unchanged physics."""
    keys=('STEP','material_requirement','material_certificate','interface_definition','load_ports_status','physical_mass_kg','physical_inertia_kg_m2')
    a={r['part_ID']:r for r in old['parts']};b={r['part_ID']:r for r in new['parts']}
    return {n:[k for k in keys if a.get(n,{}).get(k)!=b.get(n,{}).get(k)] for n in set(a)|set(b)
            if any(a.get(n,{}).get(k)!=b.get(n,{}).get(k) for k in keys)}
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'validation/integrated'/a.tag;out.mkdir(parents=True,exist_ok=False)
    d=build();errors=integrity(d);dump(out/'baseline.json',d)
    dump(out/'summary.json',dict(status='PASS' if not errors else 'FAIL',scope='SOURCE/GEOMETRY RECONCILIATION ONLY',errors=errors,part_count=len(d['parts']),producer=ref(Path(__file__))))
    if not (ROOT/'CURRENT_BASELINE.json').exists():dump(ROOT/'CURRENT_BASELINE.json',d)
    print(json.dumps(dict(parts=len(d['parts']),errors=errors,scope='not physical mass or integrated release')))
if __name__=='__main__':main()
