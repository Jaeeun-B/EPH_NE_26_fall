---
description: 방금 실행한 결과를 docs/run_log.md 에 기록한다
allowed-tools: Bash, Read, Edit, Glob
---

가장 최근 실행 결과를 `docs/run_log.md`에 한 줄 추가합니다.

## 값을 어디서 읽는가

기억하지 말고 파일에서 읽으세요.

- `outputs/b0/summary_b0.json`: `T_total_s`, `max_torque_utilization_envelope`, `min_clearance_plan_m`, `dose_share_by_kind`, `max_component`, `timing_methods`
- `outputs/b1/summary_b1.json`: 같은 항목
- `outputs/compare_b0_b1.csv`: B0 대비 변화
- `outputs/payload_check.csv`: 허용 최대 질량
- `git rev-parse --short HEAD`: 커밋
- 선량장 모드는 실행에 쓴 `--field` 값

## 기록 형식

`docs/run_log.md`의 표에 맨 아래 한 줄을 **추가**합니다. **기존 줄은 절대 고치지 마세요.** 과거에 그 값이 나왔다는 사실 자체가 기록입니다.

비고 칸에는 그때 무엇이 달랐는지 씁니다. 코드 변경, 새 입력값, 설정 변경 같은 것. 없으면 비웁니다.

## 이상이 있으면

`timing_methods`에 `toppra`가 없거나, 토크 사용률이 0.8을 넘거나, 여유거리가 d_safe 미만이면 비고에 분명히 적습니다. 정상인 척 기록하지 마세요. 나중에 이 표를 보고 판단하게 됩니다.
