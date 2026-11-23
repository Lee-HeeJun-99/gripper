import csv,unittest
from contact_provenance_assess import BASE,join
class TestProvenance(unittest.TestCase):
 def test_actual_unique_and_horizontal(self):
  src=BASE/'results/contact_provenance_run1222'
  with (src/'provenance.features.csv').open() as f,(src/'provenance.children.csv').open() as c:r=join(list(csv.DictReader(f)),list(csv.DictReader(c)))
  self.assertEqual(len(r),35);self.assertTrue(all(x['match_count']==1 for x in r))
  at=[x for x in r if x['previous_time_s']==.0004];self.assertEqual(len(at),7);self.assertTrue(all(x['normal']==[1.,0.,0.] for x in at))
 def test_ambiguity_is_not_silently_accepted(self):
  f=dict(previous_time_s='0',model0='/a/Triangle',model1='/b/Point',point0='0 0 0',point1='0 0 0',normal='0 0 1')
  c=[dict(previous_time_s='0',constraint='/response',state='/a/contact',side='0',row='0',point='0 0 0',J='0 0 -1'),dict(previous_time_s='0',constraint='/response',state='/b/contact',side='1',row='0',point='0 0 0',J='0 0 1')]
  self.assertEqual(join([f,f],c)[0]['match_count'],2)
if __name__=='__main__':unittest.main()
