---
description: 전체 파이프라인을 순서대로 실행하고 핵심 수치를 요약한다
argument-hint: "[model|grid] (기본 model)"
allowed-tools: Bash, Read, Glob
---

전체 파이프라인을 실행합니다. 선량장 모드: `$1` (비었으면 `model`)

## 순서

아래를 차례로 돌립니다. **앞 단계가 실패하면 멈추고 보고하세요.** 실패를 넘기고 다음으로 가지 마세요.

```
python scripts/00_check_env.py
python scripts/01_make_virtual_grids.py
python scripts/03_validate_line.py
python scripts/04_validate_arc.py
python scripts/05_solve_waypoints.py
python scripts/06_run_b0.py
python scripts/07_run_b1.py
python scripts/08_payload_check.py
```

`$1`이 `grid`면 `06`, `07`에 `--field grid --N 100`을 붙입니다. `--gui`는 붙이지 마세요. 창이 떠서 멈춥니다.

## 실행 중 반드시 확인할 것

- `06`, `07`의 계획 구간이 `[toppra]`로 찍히는가. `[quintic]`이면 토크 제약이 빠진 것이고 결과가 무효입니다. 이 경우 보고 맨 위에 적으세요
- 토크 사용률이 0.8 이하인가
- 경고 메시지(글꼴, 수렴 실패, NaN)가 있는가

## 보고 형식

```
## 실행 결과
전부 통과 / N번째에서 실패

## 핵심 수치
| 항목 | 값 | 이전 값 대비 |
|---|---|---|
| B0 총 작업시간 | | |
| B0 토크 사용률 | | |
| B0 최대 선량 부품 | | |
| 체류/직선/계획 비중 | | |
| B1 이동 구간 변화 | | |
| 허용 최대 베드 질량 | | |

## 문서와 다른 점
docs/와 README의 수치 중 이번 결과와 어긋나는 것

## 경고와 이상
```

이전 값은 `docs/run_log.md`의 마지막 줄과 비교합니다. 다 끝나면 `docs/run_log.md`에 이번 실행을 한 줄 추가하세요.
