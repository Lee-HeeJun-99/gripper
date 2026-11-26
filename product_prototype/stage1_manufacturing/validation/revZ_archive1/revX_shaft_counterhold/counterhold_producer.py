"""Dedicated positive counterholding, without adding gripper parts.

Only outboard coupling grip is milled. Bearing seats, M5thread zones,
8mm shoulder and crosspin remain unchanged. Round +/-Z jaw lands retained.
"""
from build_stage1 import box,cut
def counterhold_delta(old):
 s=cut(old['F0_SHAFT'],box(70,-18.01,15,8,5.51,10),box(82,-18.01,15,8,5.51,10))
 return {'SHAFT':s},{'SHAFT':'303 counterholdAF4.00+0/-0.02 onX78/82, Y-18..-12.5; bearing seatsY-8.5..-3.5/9..14, M5zones and8mm shoulder untouched. Round+/-Z lands grip split coupling. Hold real4AF spanner with coupling removed; torque capacity Stage2.'},[]
CONFIG=dict(shaft_counterhold_AF_mm=4,shaft_counterhold_Y_mm=[-18,-12.5],counterhold_stage='Coupling/caps removed during fine-nut setting; direct shaft counterhold, not holding an unqualified opposite nut')
