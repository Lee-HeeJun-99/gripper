# ReGrip product prototype — 2026-11-19

제품 우선 방향 전환에 따라 별도 구현했다. 기존 models/,Golden,Raw,
Checkpoint1644,자체 Solver와 검증 결과는 수정하지 않았다.

## 생성한 기준 후보

Single Skin + two bonded Rails + two edge cables,100mm 길이,폭24→12mm,
테이퍼 시작50mm,Root-centre radius50mm,0/120/240도 배치.
설정 원본은 config/design_v1.json. product_outboard14_v3는 동일 재료 단면의
Outboard14mm 비교 후보다. 최종 선정은 아니다.

제작 취급성을 검토하기 위해 Skin0.1mm/Rail0.5mm×2mm를 잠정 입력했다.
기존 연구의0.05mm/0.1mm나8층 ConceptV2와 다른 설계다. 물성은 미측정:
Native FEM E250MPa,nu0.3,핑거당 질량1g 가정. 실제 PET/TPU 인증값 아님.
코어 체적410mm³/핑거,1230mm³/3핑거. 기존439.34mm³와 동일 재료량이
아니므로 기존 모델 대비 성능 우위를 주장하지 않는다. 하드웨어 질량 미포함.

## 실제 산출물

- cad/generate.py:공유 형상에서 SCAD,양의 체적 Tetra 메시,STL,SVG,BOM 생성.
- meshes/product_outboard14_v3/:최신 파라메트릭 CAD 소스와 개별 Skin/Rail STL.
- drawings/candidate_v3/:치수도,부분 분해도,조립 SCAD,권위 BOM,기하 검사.
- cad/export_freecad.py:실제 BRep/STEP/STL/FCStd 생성용 FreeCAD 스크립트.
  문법 검사만 실행했다. FreeCAD/OCC/OpenSCAD가 시험 환경에서 발견되지
  않아 CAD kernel 실행·STEP·Assembly STEP·전체 Assembly STL은 미생성.
- sofa/run_native.py:SOFA 기본 FEM/CableConstraint/접촉/적분 Scene 생성·실행.
- sofa/scenes/native_three_finger_v1/:실제로800스텝 재실행한3핑거 Scene.
- results/:실제 CSV,Source/Binary/SDK 해시,로그,실패 증거,Accepted-state PNG.

STL 검증:Skin210mm³,각 Rail100mm³,합체410mm³. 모두 watertight,
consistent winding,양의 체적.3개 좌표계 determinant1,직교 오차<=1.62e-16.
이는 전체 어셈블리 간섭·가공 공차 검증이 아니다.

## 기구 관측과 변경

기본 가이드 normal3/outboard4mm,5mm Stroke에서는 실제 변형 중 와이어가
R30 물체와 약2.55mm 간섭했다. Outboard10mm도 약0.82mm 간섭.
Outboard14mm/5mm Stroke는 샘플 간섭 여유 약2.68mm지만 접촉 부족.
6mm Stroke에서는 접촉이 증가하나 약0.36mm 와이어 간섭이 다시 발생.
한 변수 변경 시험이며,동일 Stroke이지 동일 장력/Work 비교는 아니다.
가이드 질량,지지대,실제 가이드 마찰/마모,전 시간 CCD는 미검증.

Object 중심 깊이65mm,R30이면 지지면 깊이95mm가100mm 핑거보다 높아
닫힘을 방해한다.75mm 깊이 배치로 별도 시험했다. R20은80mm 배치.
초기 좌표를 바꾼 실제 물리 시험이지 저장 형상을 렌더링에서 옮긴 것이 아니다.

## 결정

초기 제작 후보만 유지한다. 실제 wrapping,독립 holding,lift와 제작 준비
완료는 승인하지 않는다. 다음은 와이어를 접촉면 밖으로 유지하면서 필요한
곡률을 만드는 가이드/앵커/Root angle의 단일 변수 기구 비교다.
자체 Solver 신규 개발보다 이 기구 문제와 Native 접촉 설정을 우선한다.
8층 필름/진공/Selective Jamming은 기본 파지 기능 이후의 교체형 확장안.
