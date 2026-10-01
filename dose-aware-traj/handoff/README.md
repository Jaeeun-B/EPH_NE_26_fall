# E 파트 인계 파일 (2026-10-01)

경로계획(Dose-aware trajectory optimization) 파트가 다른 파트와 주고받을 데이터의 형식입니다. 각 폴더의 README에 요청 사항과 작성 방법이 있습니다.

| 폴더 | 받는 파트 | 내용 | 회신 받을 것 |
|---|---|---|---|
| `01_radiation` | 방사선 | 선량 격자 규격, 메타데이터 양식, 샘플 격자, `dose_model.py`, 점검 도구 | 베드 제거 전/후 선량 격자 + 메타데이터 |
| `02_layout` | 전체 | 핫셀 좌표계와 배치 초안 | 포스터 도면과 다른 치수 |
| `03_materials` | 소재 | 부품별 차폐·TID 입력 양식 (xlsx) | 채운 `component_inputs.xlsx` |
| `04_control` | 제어 | 공통 파라미터, 2관절 축약 모델, 추종오차 양식 | 채운 `e_track_template.csv` |

모든 파일은 `02_layout/hotcell_layout.json`의 좌표계(원점 로봇 베이스 바닥 중심, 단위 m)를 기준으로 합니다. 선량 단위는 Gy/h, 누적선량은 Gy입니다.
