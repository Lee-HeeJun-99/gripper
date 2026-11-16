import json,re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class FilmDesign(unittest.TestCase):
 def test_equal_volume(self):
  d=json.loads((ROOT/'designs/film_contact/equal_volume_v2/parameters.json').read_text())
  self.assertAlmostEqual(d['volume_mm3'],d['baseline_volume_mm3'],places=10)
  self.assertEqual(d['skin_thickness_mm'],.05);self.assertEqual(d['backing_thickness_mm'],.1)
  self.assertIsNone(d['density_measured']);self.assertLess(2*d['rail_width_mm'],12)
 def test_separate_layer_midplanes(self):
  text=(ROOT/'designs/film_contact/equal_volume_v2/backing_rails.obj').read_text();p=next(line for line in text.splitlines()if line.startswith('v ')).split();self.assertAlmostEqual(float(p[1]),50.075,places=8)
 def test_application_limits(self):
  text=(ROOT/'reports/REGRIP_COMPETITION_APPLICATION_DRAFT.md').read_text()
  sections=re.findall(r'## (.*?) \((\d+)/(\d+)자\)\n\n(.*?)(?=\n## |\Z)',text,re.S)
  self.assertEqual(len(sections),11)
  for name,count,limit,body in sections:self.assertEqual(len(body.strip()),int(count),name);self.assertLessEqual(int(count),int(limit),name)
if __name__=='__main__':unittest.main()
