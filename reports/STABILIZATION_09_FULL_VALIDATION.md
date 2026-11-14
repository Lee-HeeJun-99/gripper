# 회귀/전체 검증

- 이전 전체 증거: 작업 전1061개 hash 검사 불일치0. 인수인계56개도 새 byte-for-byte PASS.
- 작업 후 이전 manifest 재검사는 .gitignore의 의도된 신규 raw 제외 규칙1건만 다르다. 물리 source/binary 변경은 없다.
- 기존30mm/600시점/45gate 및 finite kernel은 소스·바이너리 불변의 이전 검증을 승계한다.
- 새 isolated audit plugin으로2/4층 실행 회귀 PASS. 기존 모델/골든 수정 없음.
- C++ release clean build, actual18DOF Jx/Jv/K/B/kFactor/bFactor/objectivity PASS.
- ASan/UBSan own-unit PASS(detect_leaks=0); LSan 재시도 ptrace fatal BLOCKED; 전체 SOFA sanitizer NOT RUN.
- 새 Python5개 및 기존 integrated Python8개 실제 실행. 일부 테스트는 actual campaign fixtures를 사용한다.
- 초기 registration/build/mass/template 실패 로그는 보존한다. FAIL 삭제/재분류 성공 없음.
- 8층 static 및 compensated cold dynamic PASS, original standard-Euler FAIL 보존. Contact/grasp는 EXPERIMENTAL, 전체 energy BLOCKED.
- source/binary/artifact/report manifest는 STABILIZATION_EVIDENCE_MANIFEST.json.

세부 신규 checks는 grasp/gate.json 및 eight_search/validation.json을 따른다.
기존45gate에 신규 개수를 더해서 전체 모델이 인증된 것처럼 표현하지 않는다.

## 공통 증거/범위

환경: Ubuntu22.04.5, kernel6.8.0-138-generic, GCC11.4, CMake3.22.1,
Python3.10.20(robot_ws), SOFA v26.06.00(`/home/ubuntu/SOFA/v26.06.00`).
실물 측정값0건. 연구 단위 F/mm/s와 기존 E=250, A≈.732233mm², I=.0426667mm⁴를 사용한다.
기존 plugin/integrated/finite_rotation/multilayer 원본과 골든 파일을 변경하지 않았다.
raw: `results/stabilization_20261115/`; 작은 증거: `reports/stabilization_evidence/`.
설정/명령은 실험별 config.json/command.json/scene.scn, 결과는 metrics.json과 artifact hashes.
정적 잔차<1e-3, 병진/각속도<1e-5, tail drift<1e-4를 유지했다.
실행 성공과 평형/파지 검증을 구분한다. EXPERIMENTAL은 실물 인증이나 전체 모델 PASS가 아니다.
기존45 gate는 이전 소스/바이너리 무결성으로 승계하며 신규 모델에 합산하지 않는다.
