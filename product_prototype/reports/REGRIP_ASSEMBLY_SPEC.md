# 초기 어셈블리 사양 — NOT FABRICATION READY

기준 파일:drawings/candidate_v3/assembly.scad와 config.json.
개별 part 선택은 SCAD의 part 변수:skin,rail_left,rail_right,palm,mount,
clamp,guide,anchor,pulley,coupling,motor_plate. explode=15는 Clamp 분해 표시.
이는 CAD 설계 소스이며 CAD kernel 렌더/STEP 변환은 실행되지 않았다.

## 부품 연결

1. Palm annulus R64/R30,두께8mm,z5..13. Root radius50,3x120도.
2. Mount는 Palm 하부와 z5에서 접한다. Palm 볼트는 세계 Z축 방향.
3. Cartridge Root Clamp는 Skin 상면에서 시작한다.5x36x3mm,M3
   임시 clearance3.4mm,local x2.5/y±14. Clamp 볼트는 Skin normal 방향.
4. Skin0.1와 Rails0.5를 연속 접착한다고 가정한다. 레이어 재밍이 아니다.
5. 양측 가이드 위치10/30/50/70/90/98mm. OD3/ID1.2,Wire radius0.25mm는
   모두 설계 입력이다. 실제 공급 재료/가이드 반경/찢김 강도 미확정.
6. 말단 앵커,가이드 지지대,풀리 R8,커플링 bore6은 후보 소스만 있다.
   실제 모터 샤프트,베어링,모터 플레이트 지지대,브랜치 배관은 미완료.

초기 소스의 Palm–Mount 축 불일치,Clamp–Skin/브래킷 겹침,반사 좌표계와
오른쪽 Rail STL winding을 검토·수정했다. 과거 버전은 보존했다.
CAD kernel Boolean 간섭 검사와 동작 전 범위 하드웨어 검사가 필요하므로
ASSEMBLY VERIFIED가 아니다. Guide 지지대는 Native FEM에서 모델링하지
않았고 가이드는 질량 없는 BarycentricMapping 점이다.

## 구동과 조립 순서

Skin/rail 절단→접착 지그/평면도 확인→Root Clamp 체결→Mount/Palm 체결→
가이드/앵커 장착→두 와이어 독립 장력 확인→카트리지 교체 시험→
저속 무부하→고정 물체→중력/하중 시험 순서. 실제 하드웨어는 구동하지 않았다.

6개 Native CableConstraint에 같은 변위 명령을 쓴다. 실제 공통 Motor,
Mechanical Equalizer,Passive Differential이나 폐루프 장력 제어가 아니다.
모터 토크/속도/스트로크/전류·센서·팀원 정보는 미확정. Native 단일 핑거
5mm 실험의 Peak 장력 약3.67N/와이어는 가정 모델의 요구량일 뿐 모터 사양이
아니다. 이 수치로 부품 구매·안전·취성물 파손 여부를 승인하지 않는다.

## 조건부5일 제작 작업

Day1 소재·액추에이터·규정 확인,쿠폰/와이어 시험과 치수 확정.
Day2 Palm/Clamp/Cartridge 가공 및 구동부 인터페이스.
Day3 독립 와이어 저속 구동,간섭·마찰·복원 측정.
Day4 물체별 접촉/유지/해제 시험과 실패 수정.
Day5 반복 운반·수리·시연 준비. 조달/장비/인원이 미확정이므로 일정 보장 아님.

STEP 생성은 FreeCAD 환경을 제공한 뒤 별도 새 경로에서 실행:

```bash
REGRIP_CAD_OUT=/absolute/new/output FreeCADCmd product_prototype/cad/export_freecad.py
```

FreeCAD 스크립트는 실행 검증 전이며,가이드 지지대/드라이브라인 전체 연결은
STEP 어셈블리에도 추가 구현이 필요하다. 입력값을 확정하지 않고 제작하지 않는다.
