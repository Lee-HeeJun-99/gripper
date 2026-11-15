# GRASP 04 — 100mm 다층

**PASS:** 동일 matched SDK의8층 cold-start dt/base/half/quarter, 기존1e-3 잔차 기준.
**승계:** 기존2·4층/8층 static·mesh·extended 증거는 이전 버전 hash 검증으로 보존.
**NOT RUN:** 신규 접촉/파지 모델 전체의8층 확장, 대회전 다층 실물 타당성.

이전 표준 Euler 작은 증분 소실과 보상 Euler 개선을 재작성하지 않았다.
`CompensatedEulerPositions`는 해당 구조 시험에만 사용했다. 자유 물체 파지에는 적용하지 않았다.
기존180s 및 이번 installed-engine300s quarterdt timeout은 보존한다. 이전 실패를 PASS로 덮지 않는다.
observer 출력 간격.0125s 일정(각 dt의stride25/50/100), 같은12s/하중/질량/강성으로 재실행했다.
matched-source patched headless SDK와 그 SDK로 빌드한 구조 plugin만 사용, wall cap480s.

|dt s|끝단 처짐 mm|상대 잔차|판정|
|---|---:|---:|---|
|.0005|.0006035676548299951|1.64997285879e-5|PASS|
|.00025|.0006035680703937243|2.15210500660e-5|PASS|
|.000125|.0006035682805915869|1.69381328055e-5|PASS|

quarter/base 처짐 상대차1.03677e-6(.000103677%)로 .1% 진단선 통과.
quarter wall227.603s,최종속도2.12737e-7,tail drift8.95866e-7,max회전4.4574e-5rad.
`final_checks/structural.json`의 독립 ForceAudit 합산과 원래 recorder R의 차이는 세 조건 모두0.
자유DOF와 root 반력 분리, 상대 모멘트 약2e-8. Solver 잔차와 물리력 잔차를 혼동하지 않는다.
이 검사는8층/k100/현재 작은 평면 회전 연구 조건이며 모든8층 구동/접촉의 인증은 아니다.

## 독립 FEM 비교 (SOFA 결과와 구분)

`tools/grasp_fem_study.py`:21노드 EB,층수2/4/8,k0/1/100의4가지 단면 가정,36계산 모두
normalized residual<1e-3 및 작은 회전 범위 PASS. `fem/summary.json`에 개별A/I/재료량/비율/민감도 보존.

- 기존 등가단면: 각 층 A=.7322329862910148mm²,I=.04266666666666668mm⁴. 실제8×.4 사각 단면이 아니다.
- 각 층 사각 단면 고정:폭8,t=.4; 층수에 비례하여 총 재료량 증가.
- 총 단면적6.4mm² 고정: t=.4,폭16/L로 변경; 적층 높이는 변한다.
- 전체 적층 높이.8/폭8 고정: t=.8/L, A=8t,I=At²/12; 총 재료량도 고정되지만 개별EI는 변한다.

이 네 비교를 같은 물리 문제로 합산하지 않는다. E200/250/300,k.1/1/10,pitch.36/.4/.44 민감도도 별도 계산.
pitch-only 변경을 실제 필름 두께/단면 변경이라고 부르지 않는다. PET 실측값0건.
새 FEM은 결과 구조/가정의 명확화를 위한 독립 참고이며 SOFA 접촉 수렴성을 대신하지 않는다.
