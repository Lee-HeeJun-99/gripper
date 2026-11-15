cmake_minimum_required(VERSION 3.22)
project(ReGripCurvedContact LANGUAGES CXX)
add_subdirectory(../material_point_contact "${CMAKE_CURRENT_BINARY_DIR}/material_template" EXCLUDE_FROM_ALL)
find_package(Python3 REQUIRED COMPONENTS Interpreter)
find_package(Sofa.Component.StateContainer REQUIRED)
set(generated "${CMAKE_CURRENT_BINARY_DIR}/CurvedGenerated.inc")
add_custom_command(OUTPUT "${generated}"
 COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/../material_point_contact/generate.py" "${CMAKE_CURRENT_BINARY_DIR}/material_template/birth_template/BirthGenerated.inc" "${CMAKE_CURRENT_BINARY_DIR}/FrozenPoint.inc"
 COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/generate.py" "${CMAKE_CURRENT_BINARY_DIR}/FrozenPoint.inc" "${generated}"
 DEPENDS generate.py ../material_point_contact/generate.py "${CMAKE_CURRENT_BINARY_DIR}/material_template/birth_template/BirthGenerated.inc" VERBATIM)
add_library(ReGripCurvedContact SHARED CurvedContact.cpp "${generated}")
add_executable(test_curved_contact ../../tests/test_curved_contact.cpp "${generated}")
foreach(target ReGripCurvedContact test_curved_contact)
 target_include_directories(${target} PRIVATE "${CMAKE_CURRENT_BINARY_DIR}" "${CMAKE_CURRENT_BINARY_DIR}/material_template/birth_template/legacy" "${CMAKE_CURRENT_SOURCE_DIR}/../integrated")
 target_compile_features(${target} PRIVATE cxx_std_17)
 target_compile_options(${target} PRIVATE -Wall -Wextra -Wpedantic)
 target_link_libraries(${target} PRIVATE Sofa.Core Sofa.DefaultType Sofa.Helper Sofa.Simulation.Core Sofa.Component.StateContainer)
endforeach()
