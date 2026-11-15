"""Verify source-controlled configuration replaces an ignored historical template."""
import json,xml.etree.ElementTree as ET
from beam_common import ROOT,OUT,write_json,sha
from beam_grasp_trial import run,TEMPLATE
def normalized(path):
    root=ET.parse(path).getroot()
    for e in root.iter():
        if 'filename' in e.attrib:e.set('filename',e.get('filename').rsplit('/',1)[-1])
    return ET.tostring(root)
def main():
    target=OUT/'packaging_check.json'
    if target.exists():raise FileExistsError(target)
    prepared=run('packaging_probe',prepare_only=True);old=OUT/'grasp/Tz_v2';c=json.loads((prepared/'config.json').read_text());previous=json.loads((old/'config.json').read_text());ignore={'template_config_sha256','template_scene_sha256'}
    checks=dict(physical_xml_identical=normalized(prepared/'scene.scn')==normalized(old/'scene.scn'),config_identical={k:v for k,v in c.items() if k not in ignore}=={k:v for k,v in previous.items() if k not in ignore},source_controlled_template=TEMPLATE==ROOT/'models/conservative_beam/templates')
    write_json(target,dict(status='PASS' if all(checks.values()) else 'FAIL',checks=checks,canonical_hashes={n:sha(TEMPLATE/n) for n in ('config.json','scene.scn')},scope='configuration packaging equivalence only, prepared scene NOT RUN, actual measured Tz_v2 physics remains distinct'));print(checks)
if __name__=='__main__':main()
