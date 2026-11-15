cmake_minimum_required(VERSION 3.22)
project(PatchRefinedApi LANGUAGES CXX)
find_package(Python3 REQUIRED COMPONENTS Interpreter)
find_package(Sofa.Component.StateContainer REQUIRED)
set(test_source "${CMAKE_CURRENT_BINARY_DIR}/TestPatch.cpp")
add_custom_command(OUTPUT "${test_source}"
 COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/generate_test.py" "${test_source}"
 DEPENDS generate_test.py ../../tests/test_curved_contact.cpp VERBATIM)
add_executable(patch_api "${test_source}")
target_include_directories(patch_api PRIVATE "${PATCH_BUILD}" "${FROZEN_CURVE_BUILD}/material_template/birth_template/legacy" "${CMAKE_CURRENT_SOURCE_DIR}/../../models/integrated")
target_compile_features(patch_api PRIVATE cxx_std_17)
target_compile_options(patch_api PRIVATE -O3 -march=native -ffp-contract=off -Wall -Wextra -Wpedantic)
target_link_libraries(patch_api PRIVATE Sofa.Core Sofa.DefaultType Sofa.Helper Sofa.Simulation.Core Sofa.Component.StateContainer)
