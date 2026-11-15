#include "Bridge.h"
#include "FrameClassOnly.inc"
using Frame=regrip_integrated::FrameLayerNetwork;
using Cable=regrip_integrated::RoutedCable;
Frame*frame(CheckpointFF*f){need(f->getClassName()=="FrameLayerNetwork","checkpoint frame type");auto*c=static_cast<Frame*>(f);need(f->findData("referenceOrientation")==&c->reference&&f->findData("nodesPerLayer")==&c->nodes&&f->findData("filename")==&c->filename,"project frame ABI/data offset mismatch");return c;}
extern "C" void writeFrameState(CheckpointFF*f,std::ostream&out){auto*c=frame(f);out<<c->plastic.size()<<' '<<c->steps<<' '<<c->dissipated<<'\n';for(double p:c->plastic)out<<p<<' ';out<<'\n';}
extern "C" void readFrameState(CheckpointFF*f,std::istream&in){auto*c=frame(f);size_t n;need(bool(in>>n)&&n==c->plastic.size(),"checkpoint layer plastic size");need(bool(in>>c->steps)&&c->steps<=240000,"checkpoint layer steps");c->dissipated=scalar(in);need(c->dissipated>=0,"checkpoint layer dissipation");for(double&p:c->plastic)p=scalar(in);c->dissipatedEnergy.setValue(c->dissipated);}
Cable*cable(CheckpointFF*f){need(f->getClassName()=="RoutedCable","checkpoint cable type");auto*c=static_cast<Cable*>(f);need(f->findData("offsetZ")==&c->offset&&f->findData("route")==&c->route,"project cable ABI/data offset mismatch");return c;}
extern "C" void writeCableState(CheckpointFF*f,std::ostream&out){out<<cable(f)->restLength<<'\n';}
extern "C" void readCableState(CheckpointFF*f,std::istream&in){double length=scalar(in);need(length>0,"checkpoint cable rest length");cable(f)->restLength=length;}
