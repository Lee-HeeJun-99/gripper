#include "FrameReturn.h"
#include "FrameClassOnly.inc"
extern "C" FrameReturnInventory auditFrameReturn(sofa::core::behavior::ForceField<sofa::defaulttype::Rigid3Types>*f,const sofa::defaulttype::Rigid3Types::VecCoord&before){
 using namespace regrip_integrated;using Frame=FrameLayerNetwork;
 if(f->getClassName()!="FrameLayerNetwork")throw std::runtime_error("frame audit class");auto*c=static_cast<Frame*>(f);
 if(f->findData("referenceOrientation")!=&c->reference||f->findData("nodesPerLayer")!=&c->nodes||f->findData("filename")!=&c->filename)throw std::runtime_error("frame audit project ABI");
 if(c->mode.getValue()!=1)throw std::runtime_error("pressure return scope requires mode1");
 auto x0=c->local(before),x1=c->local(c->getMState()->read(sofa::core::vec_id::read_access::position)->getValue());auto selected=c->ids();unsigned n=c->nodes.getValue();double h=c->height.getValue(),k=c->stiffness.getValue();size_t count=0;FrameReturnInventory out;
 for(unsigned l=0;l<c->layers.getValue()-1;++l)for(size_t j=0;j<selected.size();++j){unsigned i=selected[j],a=c->start.getValue()+l*n+i,b=a+n;
  auto slip=[&](const Frame::VecCoord&x){auto p=c->pose(x[a]),q=c->pose(x[b]);return q.p[0]-p.p[0]-h*(std::atan2(p.q[1],p.q[3])+std::atan2(q.q[1],q.q[3]));};
  double s0=slip(x0),s1=slip(x1),z=c->plastic.at(count++),left=j?.5*(selected[j-1]+i)*c->length.getValue()/(n-1):0,right=j+1==selected.size()?c->length.getValue():.5*(i+selected[j+1])*c->length.getValue()/(n-1);
  auto r=slider(s1,z,k,c->mu.getValue()*c->currentPressure()*c->width.getValue()*(right-left));double e0=s0-z,e1=s1-r.plastic,U0=.5*k*e0*e0,U1=.5*k*e1*e1,W=k*e1*(s1-s0),P=.5*k*(e1-e0)*(e1-e0);
  out.oldEnergy+=U0;out.newEnergy+=U1;out.endpointWork+=W;out.plastic+=r.dissipation;out.projection+=P;out.residual+=U1-U0-W+r.dissipation+P;
 }
 return out;
}
