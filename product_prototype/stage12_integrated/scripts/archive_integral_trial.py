"""Record AK1 preserved local solids without tracking intermediate bulk CAD."""
import json
from baseline_registry import ROOT,ref,dump
def main():
    folder=ROOT/'cad/exports/revAK_integral1';out=folder/'LOCAL_RAW_MANIFEST.json'
    if out.exists():raise FileExistsError(out)
    files=[ref(p) for p in sorted(folder.iterdir()) if p.suffix in ('.step','.stl')]
    dump(out,dict(scope='Original AK1 intermediate CAD retained locally; independent foot support FAIL is preserved separately',files=files,source=ref(folder/'summary.json'),failure=ref(ROOT/'validation/transmission/AK_support1/summary.json'),deleted=False,regenerated=False))
    q=json.loads((ROOT/'INTEGRATED_TASKS.json').read_text())
    for t in q['tasks']:
        if t['id']=='AH_collet_and_axial_capacity':t['hypothesis']='AK actual9.7..11.2mm shaft grip and clamp-zone coverage remove old short-grip geometry concern; combined torque and spring axial load still require actual contact/preload/material and motor bearing evidence'
    dump(ROOT/'INTEGRATED_TASKS.json',q)
if __name__=='__main__':main()
