# CLOSURE campaign 진행 기록

기준20249c953a7eef30f5574e4e7d1ce7cb098505f6, 새브랜치 development/regrip-contact-closure-optimization.
실제ROOT/새raw/build는 외장디스크 안의 ReGrip/results/closure_20261115 및 build/closure_20261115.
시작시 기존GRASP2286항목 무결성 오류0. 기존원본/골든/이전raw와SDK바이너리 보존.
신규.gitignore 규칙은 비물리적 메타데이터 변경이며 이전compiled physics source는 변경하지 않는다.

## 실제 완료

- 별도 models/closure ActiveIntervalContact: sphere exact active interval,Gauss8/16/32,
  독립 고정material-history grid(.01mm). 이동Gauss점 자체에 이력을 붙이지 않는다.
- 독립 C++18DOF moving-boundary FD max8.37317628427e-12,query순수성/정지100commit creep0,
  작용반작용/좁은활성구간/다항식적분 PASS. 초기namespace미지정/경고 수정후빌드.
- 독립SciPy기준 적분차수8/16/32 maxabs오차1.69e-11/3.22e-12/3.78e-13;
  기존균등샘플링 aliasing과 분리. 실제SOFA첫11/q8 tip이아닌물체이동.000931672mm/잔차1.93e-6.
- 기존matched SDK의 headers/exports만 별도.runtime/closure_sdk로설치하고같은build라이브러리를연결;
  새플러그인 재빌드/단위PASS,ldd 설치SOFA혼합없음. 기존SDK라이브러리를덮어쓰지않음.
- 측정된새접촉patch 렌치 rank6;inscribed8-ray cone strict-origin PASS.
  그러나현재법선력한계±Tz 요구(5e-6 F·mm)는LP불가능. rank6/closure/유한하중지지를구분.
- Beam닫힌일경로는 distal-frame고정대조군에서약1e-16 상대일;
  proximal-frame회전시유의한비보존순환과cross-derivative불일치관측. 전체potential을임의정의하지않음.

## 진행 중

11/21/41×Gauss8/16/32,history spacing절반,dt절반,반복실행;
matched SDK 동일조건±F/±T 12개와24s해제·복원. 실제결과만수집하며미완료는PASS아님.
Native접촉은구현/API/질량/topology실패를보존하며원인분리중. 파지최적화아직BLOCKED.

## 자원 정책

장시간시간적분4 child상한(각pool2),짧은독립진단1개/컴파일2job 별도상한.
물리child4GiB/최대480s/core dump0/timeout kill-reap. 기존DB/raw덮어쓰기없음.
전체campaign은고유실험유한리스트,무한재시도금지. 실물측정0건.

## 유한 campaign 종료 시점 추가 기록 (이전 기록 보존)

- 실제76개 물리trial metrics와별도diagnostics 수행. 실패대조군·초기실패·timeout도보존.
- 2핑거11개 접촉수렴 비교 PASS;41노드q16↔32차.053853%,mesh11↔41차.5973045%,dt차.02602475%.
- 2핑거±Tz FAIL을physical3finger배치로비교. 3핑거12국소유지/해제복원 PASS,
  그러나전체moment FAIL/공간history수렴FAIL. q41고차2회+독립retry1회각480s한계,추가무한재시도안함.
- 고정반력까지재구성한3핑거Y모멘트2.26294929813e-5,live27960step fieldaudit로Beam원인분리.
  Layer토크합≈1.94e-12,cable각≤6.1e-18,contact≈3.96e-20. 가상보정torque추가안함.
- Native0buffer실패후명시적.001/.0005mm buffer둘다지속반력. impulse/dt검증,차.00712443%.
- Beam프레임회전닫힌일의비보존순환확인,전체에너지BLOCKED. 완화/임의potential/미구현0대입없음.
- Python73,C++신규3/기존5,신규커널ASan/UBSan/LSan PASS. 이전실패LSan sandbox로그도보존.
- matchedSDK600시점골든2회 PASS,원본Python600FREE/전단과XML비교 PASS(과도응답,정적평형아님).
- matchedSDK2×120000step/2unload memory bounded PASS,FD판정오류는별도audit에서수정근거기록.
- 3finger실측2401frame 재생 PASS. Headless원칙유지,실제GUI/실물측정없음.
- 100mm Optuna 신규0trial,BLOCKED를기록. 이전30mm24COMPLETE/3PRUNED를새결과로표시하지않음.
- 코드d3a343d까지기능단위로컬커밋. 최종보고/해시/재개명령보존후문서커밋,원격push없음.
