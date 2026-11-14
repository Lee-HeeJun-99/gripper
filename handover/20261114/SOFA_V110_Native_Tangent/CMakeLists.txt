cmake_minimum_required(VERSION 3.22)
project(SofaTangentialV110 VERSION 1.1.0 LANGUAGES CXX)
find_package(Sofa.Framework REQUIRED)
add_library(SofaTangentialV110 SHARED
    src/TangentialRigidForceField.cpp
    src/initPlugin.cpp)
target_compile_features(SofaTangentialV110 PRIVATE cxx_std_17)
target_link_libraries(SofaTangentialV110 PRIVATE Sofa.Core Sofa.DefaultType Sofa.Helper)
target_compile_definitions(SofaTangentialV110 PRIVATE SOFA_BUILD_TANGENTIAL_V110)
set_target_properties(SofaTangentialV110 PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
install(TARGETS SofaTangentialV110 RUNTIME DESTINATION bin LIBRARY DESTINATION lib ARCHIVE DESTINATION lib)
