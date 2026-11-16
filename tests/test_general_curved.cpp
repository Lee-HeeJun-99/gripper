// Reuse the immutable parent API/FD/virtual-work test without editing it.
// This translation unit exercises the NEW registered component and owner.
#include "../models/general_vector_history/GeneralCurvedContact.cpp"
#define CurvedMaterialContact GeneralVectorCurvedContact
#define main inherited_general_api_main
// CMake removes only the parent's component include from the reused test body.
#include "GeneralTestBody.inc"
#undef main
#undef CurvedMaterialContact
int main(){ return inherited_general_api_main(); }
