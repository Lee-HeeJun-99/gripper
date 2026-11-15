"""Reuse immutable controlled-event builder, changing ONLY the new scene tag.

All overrides are local to this CLI process, never edits to historical tools.
The engine sees the saved transformed XML; its hash is captured by the builder.
"""
import xml.etree.ElementTree as ET
import birth_events as original
from research_common import OUT,PLUGIN,identity,write_json
def main():
    engine=original.execute_process
    def execute(command,out,timeout):
        tree=ET.parse(out/'scene.scn');field=tree.getroot().find('.//BirthAwareContact')
        if field is None:raise ValueError('controlled template changed')
        field.tag='MaterialPointContact';tree.write(out/'scene.scn',encoding='utf-8',xml_declaration=True)
        return engine(command,out,timeout)
    original.OUT=OUT;original.PLUGIN=PLUGIN;original.identity=identity;original.execute_process=execute
    results={'birth':original.case('birth',1.03,-.02,.02,expected_extension=.01),'through':original.case('through',2.,-4.,.02,expect_error=True),'none':original.case('none',1.03,0,.02,expected_extension=0)}
    write_json(OUT/'controlled_events.json',dict(results=results,scope='actual SOFA controlled fixed-object plane unit; tag replacement saved in new XML only; not free grasp; through PASS means rejection classifier'))
if __name__=='__main__':main()
