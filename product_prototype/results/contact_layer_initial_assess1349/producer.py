"""Read preserved Native VTU correctly;Float32 text is not strict State API."""
import argparse,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/contact_layer_initial_export1341';g=json.loads((BASE/'results/b3_contact_layer_geometry1336/mesh.json').read_text());records=[]
 for i in range(3):
  f=src/f'layer{i}.vtu';data=ET.parse(f).find('UnstructuredGrid/Piece/Points/DataArray');q=np.fromstring(data.text,sep=' ').reshape(-1,3);expected=np.array(g['world_reference_m'][i]);printed=np.array([[float(format(x,'.6g')) for x in row] for row in expected]);records.append(dict(finger=i,points=len(q),declared_type=data.get('type'),max_absolute_q_error_m=float(abs(q-expected).max()),matches_expected_six_significant_digit_text=bool(np.array_equal(q,printed)),vtk_sha256=sha(f)))
 d=dict(status='PASS_QUANTIZED_INITIAL_EXPORT_DIAGNOSTIC_ONLY' if all(r['matches_expected_six_significant_digit_text'] for r in records) else 'FAIL_EXPORT_QUANTIZATION_HYPOTHESIS',records=records,scope='Preserved Native exportAtBegin VTU is Float32/six-significant-digit text. Coordinates match expected rounded initial positions only;not STRICT1e-12 API proof.1341 producer searched vtk rather than actual vtu and its FAIL is retained.',strict_API_identity='NOT MEASURED_BY_VTU',physical_validation='NOT QUALIFIED');(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
