"""Passive Shell/assembly instrumentation identity, not convergence approval."""
import argparse,json,xml.etree.ElementTree as ET
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False)
 source=ROOT/'results/autonomous_film_20261116_trapezoid_reference69/1';plugin=ROOT/'build/film_shell_20261116_shell_profile157/libReGripFilmShell.so';sdk=ROOT/'build/grasp_20261115/sofa_patched';results={}
 for enabled in (False,True):
  name='on' if enabled else 'off';case=out/name;case.mkdir();tree=ET.parse(source/'scene.scn');root=tree.getroot()
  for node in root.iter():
   for key,value in list(node.attrib.items()):
    if str(source) in value:node.set(key,value.replace(str(source),str(case)))
    if 'libReGripFilmShell.so' in value:node.set(key,str(plugin))
  field=next(root.iter('FilmShell'));field.set('filename',str(case/'journal.csv'))
  if enabled:field.set('costProfileFilename',str(case/'cost.csv'))
  tree.write(case/'scene.scn');r=guarded([sdk/'bin/graph_probe',sdk,case/'scene.scn','20','0',plugin],case/'process',480)
  results[name]=dict(process=r,journal_sha256=sha(case/'journal.csv'),scene_sha256=sha(case/'scene.scn'))
 exact=results['on']['journal_sha256']==results['off']['journal_sha256'];ok=exact and all(x['process']['exit_code']==0 for x in results.values())
 write_json(out/'summary.json',dict(status='PASS' if ok else 'FAIL',scope='passive cost observer physical journal identity only',binary_sha256=sha(plugin),results=results,bitwise_equal=exact));print(json.dumps(dict(status='PASS' if ok else 'FAIL',bitwise_equal=exact)))
if __name__=='__main__':main()
