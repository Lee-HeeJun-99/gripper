"""Independent audit of discrete material-cell counts in actual trial XML."""
import xml.etree.ElementTree as ET
import math,sys
from collections import Counter
from birth_common import OUT,write_json
def main():
    result={}
    for name in('base','n21','n41'):
        node=ET.parse(OUT/'grasp'/name/'scene.scn').getroot().find('Node');flat=list(map(float,node.find('MechanicalObject').get('position').split()));x=[flat[i:i+7]for i in range(0,len(flat),7)];c=node.find('BirthAwareContact');e=list(map(int,c.get('segments').split()));lengths=[math.sqrt(sum((x[e[i+1]][j]-x[e[i]][j])**2 for j in range(3)))for i in range(0,len(e),2)];h=float(c.get('historySpacing'));counts=[]
        for L in lengths:
            ratio=L/h;nearest=round(ratio);counts.append(nearest if abs(ratio-nearest)<=32*sys.float_info.epsilon*max(1,abs(ratio))else math.ceil(ratio))
        result[name]=dict(status='PASS' if len(set(counts))==1 else'FAIL',length_range_mm=[min(lengths),max(lengths)],counts=dict(Counter(counts)),scope='actual XML discrete count audit; does NOT certify physical mesh convergence')
    write_json(OUT/'material_grid_audit.json',result);print(result)
if __name__=='__main__':main()
