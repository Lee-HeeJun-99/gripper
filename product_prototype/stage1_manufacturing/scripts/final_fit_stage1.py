"""Worst-case diameter+paired-axis clearance, not a fit parameter scan.

16.010minimum seat left only3um combined radial float, insufficient for
5um housing +2.5um shaft axis offsets.16.030+-0.005 allows3um radial margin
under SKF local-diameter bounds; incoming form-envelope gauges also required.
Only material is removed from the two retained carriers; stops are unchanged.
"""
from build_stage1 import cyl,cut
def fit_delta(old):
 new={};notes={}
 for label,y,h in [('L',-9.001,5.501),('R',8.7,5.801)]:
  new['PEDESTAL_'+label]=cut(old['F0_PEDESTAL_'+label],cyl(8.015,(80,y,20),h,(0,1,0)))
  notes['PEDESTAL_'+label]='Custom16.030+-0.005 seat with minimum-material bore envelope; paired housing coax0.010dia, shaft journal coax0.005dia; incoming gauges mandatory; actual inner abutment unchanged'
 return new,notes,[]
