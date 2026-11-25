"""Stock forcefield plus public input-data schedule; no mechanical-state writes."""
import xml.etree.ElementTree as ET
from analyse import BASE,sha

def attach(root,out,names,coefficient,begin=.5,end=.6):
 binary=BASE/'cad/build_brake_schedule1920/libReGripBrakeSchedule.so';assert binary.is_file();root.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)));root.insert(0,ET.Element('RequiredPlugin',pluginName='Sofa.Component.MechanicalLoad'))
 for name in names:
  body=root.find(f"Node[@name='{name}']/Node[@name='body3']");ff=body.find('UniformVelocityDampingForceField')
  if ff is None:ff=ET.SubElement(body,'UniformVelocityDampingForceField',template='Rigid3d',name='motorViscousLoss',implicit='1')
  ff.set('dampingCoefficient','0');assert ff.get('implicit')=='1';ET.SubElement(root,'NativeBrakeSchedule',target=f'@{name}/body3/{ff.get("name")}',begin=str(begin),end=str(end),coefficient=str(coefficient),filename=str(out/f'{name}_brake_schedule.csv'))
 return dict(binary=str(binary),binary_sha256=sha(binary),controller_source_sha256=sha(BASE/'sofa/native_brake_schedule/Controller.cpp'),helper_source_sha256=sha(BASE/'sofa/brake_schedule_common.py'),begin_s=begin,end_s=end,coefficient_Nms_per_rad=coefficient)
