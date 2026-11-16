# ReGrip 구조 연구 — Concept v2, 제작 확정 아님

## 근거와 기존 구조

`tools/design_regrip.py`가 기존 `closure_frame_trial.py`의 Config를 AST로 읽고
기존 좌표식을 재현했다. 원본 SHA와 좌표는 designs/baseline/concept_v2/geometry.json.
100 mm×3핑거, 120°배치, 2층, 층 간격0.4 mm, 와이어 offset−0.2 mm,
평면 가이드와 root 고정이 존재한다. 중심 기준 root 반지름95.148 mm로
50 mm 목표를 만족하지 않는다. 기존 접촉은 선분/중심선이며 실제 폭8 mm의
필름 접촉압 분포를 계산한 모델이 아니다. 등가 원형 Beam 면적과8×0.4직사각
단면도 같지 않다. 기존 연구 모델과 Golden은 수정하지 않았다.

## 선행 기술과 차별성 가설

- [Fang et al., Multimode Grasping..., 2021](https://pubmed.ncbi.nlm.nih.gov/34107748/):
  모듈형 핑거, 텐던, 레이어 재밍의 조합이 이미 알려져 있다.
- [Chung et al., Honeycomb-Velcro Jamming, 2024](https://www.mdpi.com/2076-0825/13/9/359):
  허니컴·직물·진공 막을 이용한 순응 접촉 및 강성화가 있다.
- [Layer-jamming skin-based bionic webbed foot, 2024](https://www.sciencedirect.com/science/article/pii/S026382232400343X):
  넓은 감싸기와 재밍 피부의 선행 사례다. 본문 접근403으로 상세 정량비교는 미실시.

따라서 넓은 접촉+재밍 자체를 신규 발명으로 주장하지 않는다. 검증할 ReGrip
가설은 **연속된 tapered contact skin과 교체형 적층 카트리지에서, 근위/중간/원위
재밍 회로를 분리하여 적응 구간을 남기고 하중 전달 구간만 잠그는 것**이다.
새로운 조합/구체 메커니즘 후보이며 독창성·특허 자유실시 판단은 NOT RUN.

## 실제 생성한 후보

1. Baseline: 추출한 기존 좌표/기구를 기준으로 유지.
2. Film: 본체 반지름50 mm, 아래로 내려오는100 mm 카트리지3개.
   폭24→12 mm(원위50 mm taper), 가정8×0.05 mm 필름, 연속 접촉면,
   양쪽 edge tendon과 equalizer. 외피/탄성 복원띠, root split clamp.
3. Selective: 동일 외형에0–30/35–65/70–100 mm 진공 pouch 세 개.
   5 mm bridge는 비재밍 유연부. 손상되는 외피와 적층 insert를 교체.
   세 회로가 모든 핑거의 동명 구간을 공유한다. 9개 포트지만 밸브3개이며
   핑거별 독립9구간 제어가 아니다. 역류/누설 전파와 배관 간섭은 미검증.

구간 봉합부가 모든 레이어를 강제로 접착하면 미끄럼과 강성 전환이 사라진다.
필름 distal 끝은 sleeve 안에서 미끄러지고 root clamp로 하중을 전달하도록
설계했다. 실제 seal강도·층 고정·압력 균일도·마찰은 모두 실측 필요.

## 산출물과 검증 수준

concept_v2의 rest.obj/prescribed_close.obj/stack_section.obj, geometry.scn,
parameters.json 및 SVG/PNG는 동일 생성기의 기하를 사용한다.
prescribed curl0.77 rad와당김1.155 mm는 기구학 가정,SOFA 변형 결과가 아니다.
표면315점/480삼각형, 중복/퇴화 삼각형 면적 검사와 실제 SOFA 로딩 PASS.
막/쉘 변형, jamming층간 마찰, 실제 접촉압·파지 Gate는 NOT RUN.
Matching SDK에 IO.Mesh가 없어 초기로딩 FAIL을 보존하고 같은 OBJ좌표를
XML에 직접 넣는 독립v2로 수정했다. bending spring 라이브러리도 현재 SDK에
없어 membrane FEM만 넣고 shell이 완성됐다고 하지 않는다.

다음 모델은 membrane+검증된 bending항 또는 shell/strip ROM의 폭 방향
DOF를 가져야 한다. 폭만 커진 Beam으로 대체하지 않는다. Shell patch의
강체운동/곡률에너지/메시수렴 후 native 표면 접촉과 결합한다. 공통 friction
시간 Gate는 별도로 유지하고 최종 파지 최적화는 차단한다.

## 수치 선별 결과

추가 기구학 계산에서 R20 구체의 첫 접촉은 curl≈0.776699 rad,
기하학적 tendon 당김≈1.16505 mm다(재료좌표0.05 mm 표본).
기존0.77 rad 도면은 아직 간격0.306284 mm로 **접촉 전**이다.
sequence.svg는첫접촉기하를별도표시하고JAM단계에서도같은형상을쓴다.
이 값은 힘·마찰·복원·감싸기 접촉각을 계산한 결과가 아니다.

가정 E=250,폭24 mm 일정한 EB 독립 계산에서 OFF EI=0.5 F·mm².
가정 강성배수16일 때 근위30 mm만 ON한 유효 강성비2.60374,전체ON16.
이는 압력 보정값/실측치/실제 tapered shell 파지결과가 아니다. 이 조건의
전체ON EI=8은 기존 두 등가 Beam의합 EI≈21.333보다 작다. 넓은 필름이
무조건 하중 지지력이 우수하다는 가설은 현재 근거가 없다.
