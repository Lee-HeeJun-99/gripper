#include "Bridge.h"
#include <sofa/simulation/AnimateBeginEvent.h>
#include <sofa/core/behavior/Mass.h>
#include <iostream>
#include "../../models/contact_birth/MaterialCells.h"
#include "../../models/curved_contact/Map.h"
#include "CurveClassOnly.inc"
using Contact=regrip_integrated::CurvedMaterialContact;
Contact*contact(CheckpointFF*f){need(f->getClassName()=="CurvedMaterialContact","checkpoint contact type");auto*c=static_cast<Contact*>(f);need(f->findData("historySpacing")==&c->historySpacing&&f->findData("objectIndex")==&c->objectIndex&&f->findData("filename")==&c->filename,"project contact ABI/data offset mismatch");need(c->journalFilename.getValue().empty(),"checkpoint scope requires optional contact journal disabled");return c;}
extern "C" unsigned curveCheckpointSteps(CheckpointFF*f){return contact(f)->steps;}
extern "C" void writeCurveState(CheckpointFF*f,std::ostream&out){auto*c=contact(f);auto signature=c->signature();out<<signature.size()<<' ';for(double v:signature)out<<v<<' ';out<<'\n';
 out<<c->steps<<' '<<c->plastic<<' '<<c->committedPlastic<<' '<<c->released<<' '<<c->lastEventTime<<' '<<c->bornNodes<<' '<<c->deadNodes<<' '<<c->unresolvedEvents<<' '<<c->maximumUnresolvedDepth<<'\n';
 out<<c->previous.size()<<'\n';for(auto&p:c->previous){for(int j=0;j<3;++j)out<<p.getCenter()[j]<<' ';for(int j=0;j<4;++j)out<<p.getOrientation()[j]<<' ';out<<'\n';}
 out<<c->grids.size()<<'\n';for(const auto&g:c->grids){out<<g.count<<' '<<g.length<<' '<<g.active.size()<<'\n';for(unsigned i:g.active){const auto&h=g.state.at(i);need(h.active,"inactive checkpoint active ID");out<<i<<' '<<int(h.sliding)<<' ';for(auto&v:{h.local,h.normal,h.elastic})for(double d:v)out<<d<<' ';out<<'\n';}}
}
extern "C" void readCurveState(CheckpointFF*f,std::istream&in){auto*c=contact(f);size_t count;need(bool(in>>count)&&count==c->signature().size(),"checkpoint contact signature size");for(double expected:c->signature())need(scalar(in)==expected,"checkpoint physics/topology changed");
 need(bool(in>>c->steps)&&c->steps<=240000,"checkpoint contact step count");c->plastic=scalar(in);c->committedPlastic=scalar(in);c->released=scalar(in);c->lastEventTime=scalar(in);need(bool(in>>c->bornNodes>>c->deadNodes>>c->unresolvedEvents),"checkpoint event counts");c->maximumUnresolvedDepth=scalar(in);need(c->plastic>=0&&c->committedPlastic>=0&&c->released>=0,"negative checkpoint dissipation");
 need(bool(in>>count)&&count==c->previous.size(),"checkpoint previous size");for(auto&p:c->previous){for(int j=0;j<3;++j)p.getCenter()[j]=scalar(in);for(int j=0;j<4;++j)p.getOrientation()[j]=scalar(in);Contact::pose(p);}
 need(bool(in>>count)&&count==c->grids.size(),"checkpoint grid size");for(auto&g:c->grids){unsigned cells;size_t active;need(bool(in>>cells)&&cells==g.count,"checkpoint material cells");need(scalar(in)==g.length,"checkpoint reference length");need(bool(in>>active)&&active<=g.count,"checkpoint active count");for(auto&h:g.state)h={};g.active.clear();for(size_t j=0;j<active;++j){unsigned id;int sliding;need(bool(in>>id>>sliding)&&id<g.count&&(sliding==0||sliding==1)&&(g.active.empty()||id>g.active.back()),"checkpoint material ID");auto&h=g.state[id];h.active=true;h.sliding=sliding;for(auto*v:{&h.local,&h.normal,&h.elastic})for(double&d:*v)d=scalar(in);need(std::abs(regrip_integrated::dot(h.normal,h.normal)-1)<1e-8,"checkpoint normal");g.active.push_back(id);}}
 c->cachedEpoch=~0u;c->cachedX.clear();
}
