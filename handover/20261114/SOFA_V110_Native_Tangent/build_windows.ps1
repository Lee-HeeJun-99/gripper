$ErrorActionPreference = 'Stop'
$sofa = 'C:\Users\lhj\SOFA\v26.06.00'
$src = $PSScriptRoot
if (-not (Get-Command cmake -ErrorAction SilentlyContinue)) { throw 'CMake not found. Install CMake and Visual Studio 2022 C++ Build Tools.' }
cmake -S $src -B (Join-Path $src 'build') -G 'Visual Studio 17 2022' -A x64 `
  "-DCMAKE_PREFIX_PATH=$sofa"
if ($LASTEXITCODE -ne 0) { throw 'CMake configure failed; see printed errors. Installed SOFA binary may lack C++ SDK headers.' }
cmake --build (Join-Path $src 'build') --config Release
if ($LASTEXITCODE -ne 0) { throw 'Build failed. Check C++ compiler/API errors; no DLL was verified.' }
Write-Host 'DLL output:'
Get-ChildItem (Join-Path $src 'build') -Filter 'SofaTangentialV110.dll' -Recurse
Write-Host 'Copy DLL to SOFA/bin only after successful build, then run scenes with runSofa.'
