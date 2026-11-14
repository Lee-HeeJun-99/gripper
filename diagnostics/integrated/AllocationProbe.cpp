// Child-local LD_PRELOAD C++ allocation attribution. NOT a complete malloc profiler.
// Fixed tables avoid self-allocation. Aligned allocations and direct malloc not tracked.
#include <execinfo.h>
#include <dlfcn.h>
#include <pthread.h>
#include <cstdlib>
#include <cstdio>
#include <cstring>
#include <cstdint>
#include <new>
namespace {
constexpr size_t P=1<<19,G=1<<14,S=8;
struct Entry{void*p=nullptr;size_t size=0;unsigned group=0;};
struct Group{void*stack[S]{};size_t live=0,peak=0,count=0;bool used=false;};
Entry pointers[P];Group groups[G];pthread_mutex_t lock=PTHREAD_MUTEX_INITIALIZER;
thread_local bool active=false;size_t skipped=0;
size_t mix(size_t x){x^=x>>23;x*=0x2127599bf4325c37ULL;x^=x>>47;return x;}
void insert(void*p,size_t n){
 if(active||!p)return;active=true;void*stack[S]{};backtrace(stack,S);
 size_t hash=0;for(auto a:stack)hash=mix(hash^reinterpret_cast<uintptr_t>(a));
 pthread_mutex_lock(&lock);size_t g=hash&(G-1),gtries=0;
 while(groups[g].used&&std::memcmp(groups[g].stack,stack,sizeof(stack))&&++gtries<G)g=(g+1)&(G-1);
 if(gtries==G){++skipped;pthread_mutex_unlock(&lock);active=false;return;}
 auto&group=groups[g];if(!group.used){group.used=true;std::memcpy(group.stack,stack,sizeof(stack));}
 size_t at=mix(reinterpret_cast<uintptr_t>(p))&(P-1),tries=0;
 while(pointers[at].p&&pointers[at].p!=reinterpret_cast<void*>(1)&&++tries<P)at=(at+1)&(P-1);
 if(tries==P)++skipped;else{pointers[at]={p,n,unsigned(g)};group.live+=n;group.count++;if(group.live>group.peak)group.peak=group.live;}
 pthread_mutex_unlock(&lock);active=false;
}
void erase(void*p){
 if(active||!p)return;active=true;pthread_mutex_lock(&lock);
 size_t at=mix(reinterpret_cast<uintptr_t>(p))&(P-1),tries=0;
 while(pointers[at].p&&pointers[at].p!=p&&++tries<P)at=(at+1)&(P-1);
 if(pointers[at].p==p){groups[pointers[at].group].live-=pointers[at].size;pointers[at].p=reinterpret_cast<void*>(1);}
 pthread_mutex_unlock(&lock);active=false;
}
}
void*operator new(size_t n){void*p=std::malloc(n?n:1);if(!p)throw std::bad_alloc();insert(p,n);return p;}
void*operator new[](size_t n){return ::operator new(n);}
void operator delete(void*p)noexcept{erase(p);std::free(p);}
void operator delete[](void*p)noexcept{::operator delete(p);}
void operator delete(void*p,size_t)noexcept{::operator delete(p);}
void operator delete[](void*p,size_t)noexcept{::operator delete(p);}
extern "C" void regrip_allocation_dump(){
 active=true;pthread_mutex_lock(&lock);std::fprintf(stderr,"ALLOC skipped=%zu; direct malloc/aligned allocations excluded\n",skipped);
 for(size_t j=0;j<G;++j)if(groups[j].used&&groups[j].live>16*1024){auto&g=groups[j];std::fprintf(stderr,"ALLOC live=%zu peak=%zu allocations=%zu\n",g.live,g.peak,g.count);
  for(size_t k=0;k<S;++k)if(g.stack[k]){Dl_info info{};dladdr(g.stack[k],&info);std::fprintf(stderr,"  %s %s +0x%zx\n",info.dli_fname?info.dli_fname:"?",info.dli_sname?info.dli_sname:"?",reinterpret_cast<uintptr_t>(g.stack[k])-reinterpret_cast<uintptr_t>(info.dli_saddr));}}
 pthread_mutex_unlock(&lock);active=false;
}
