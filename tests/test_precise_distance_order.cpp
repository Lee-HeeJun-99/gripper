#include "../models/film_three_finger/PreciseDistanceOrder.h"
#include <iostream>
using namespace regrip_three_finger;
int main(){try{
 TriangleCoordinates a{{{-1.1989229165010329e-08,-6,30.009999996464114},{-1.1989229165010329e-08,0,30.010000000000002},{-5.0000000119892292,0,30.009999996464114}}};
 TriangleCoordinates b{{{-5.0000000119892292,0,30.009999996464114},{-1.1989229165010329e-08,0,30.010000000000002},{-5.0000000119892292,6,30.009999996464114}}};
 if(preciseOrder(a,b)!=-1||preciseOrder(b,a)!=1||preciseOrder(a,a)!=0)throw std::runtime_error("recorded exact-input ordering mismatch toDecimal840");
 if(rationalOrder(a,b)!=-1||rationalOrder(b,a)!=1||rationalOrder(a,a)!=0)throw std::runtime_error("exact rational fixture840 ordering");
 TriangleCoordinates c{{{-25.000000117070087,0,30.009999965473451},{-25.00000011707008,6,30.009999965473451},{-30.000000117070094,6.0000000000000036,30.009999965473451}}};
 TriangleCoordinates d{{{-25.00000011707008,-5.9999999999999991,30.009999965473451},{-25.000000117070087,0,30.009999965473451},{-30.000000117070094,1.7763568394002505e-15,30.009999965473451}}};
 bool unresolved=false;try{preciseOrder(c,d);}catch(const UnresolvedDistanceOrder&){unresolved=true;}if(!unresolved||rationalOrder(c,d)!=1||rationalOrder(d,c)!=-1)throw std::runtime_error("recorded unresolved898/exact900 fixture");
 auto rotate=[](TriangleCoordinates x){for(auto&p:x){double old=p[0];p[0]=-p[1];p[1]=old;}return x;};
 if(preciseOrder(rotate(a),rotate(b))!=-1)throw std::runtime_error("exact90degree ordering objectivity");
 TriangleCoordinates plane{{{-1,-1,2},{1,-1,2},{0,1,2}}};using S=boost::multiprecision::cpp_bin_float_100;if(preciseSquaredDistance<S>(plane)!=4)throw std::runtime_error("plane interior distance");
 bool rejected=false;try{auto degenerate=plane;degenerate[2]=degenerate[1];preciseOrder(degenerate,plane);}catch(const std::domain_error&){rejected=true;}if(!rejected)throw std::runtime_error("degenerate triangle accepted");
 std::cout<<"PASS value-only113/334bit ordering,Decimal840 fixture,exact90degree rotation,face,degenerate;NOT force/Jacobian or SOFA certification\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
