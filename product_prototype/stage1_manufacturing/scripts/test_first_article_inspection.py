"""Synthetic software negative controls, not physical measurement records."""
import unittest
from first_article_inspection import evaluate
class RecordTests(unittest.TestCase):
 def test_empty_is_not_pass(self):self.assertEqual(evaluate([])['status'],'FIRST_ARTICLE_SCHEMA_FAIL')
 def test_blank_is_not_measured(self):self.assertEqual(evaluate([dict(inspection_ID='synthetic_blank')])['status'],'FIRST_ARTICLE_NOT_MEASURED')
 def test_missing_record_is_rejected(self):self.assertEqual(evaluate([dict(inspection_ID='wrong')],[dict(inspection_ID='required')])['status'],'FIRST_ARTICLE_SCHEMA_FAIL')
if __name__=='__main__':unittest.main()
