# 선량 격자 인계 규격 v1.0 (방사선 파트용)

경로계획(E) 파트가 받는 선량장 데이터의 형식입니다. 이 형식만 맞으면 E 파트 코드는 수정 없이 파일만 바꿔 끼워 결과를 다시 냅니다.

## 요청 사항

1. 격자 2개
   - `pre_removal`: 교체 전. 사용 후 Bed A 포함 (S1 접근, S2 해제 구간에 사용)
   - `post_removal`: Bed A를 들어낸 뒤. Bed B, 배관 등 나머지 선원 (S3~S6 구간에 사용)
2. 격자마다 `dose_grid_pre.npy` + `dose_grid_pre_meta.json` 처럼 같은 이름의 쌍으로
3. S3 반출 구간에서는 로봇이 사용 후 베드를 들고 움직이므로 정적 격자로 표현할 수 없습니다. 메타데이터의 `sources`에 Bed A 선원의 위치·모양·세기를 적어 주세요. E 파트가 `dose_model.py`로 매 시점 계산합니다. 더 정밀한 모델(자체 차폐, 체적 선원 등)이 있으면 `dose_model.py`의 함수 이름과 인자는 그대로 두고 내부만 바꿔 주면 됩니다.
4. 보내기 전에 점검 도구로 확인

```bash
pip install numpy matplotlib
python check_dose_grid.py dose_grid_pre.npy
```

`[오류]`가 없고 `결과: 통과`가 나오면 됩니다. 함께 저장되는 `*_quicklook.png`에서 빨간 점선(meta에 적은 선원)이 배치도의 베드·배관 위에 겹치는지 눈으로 확인해 주세요. 어긋나 있으면 축 순서나 원점이 틀린 것입니다.

## 파일

| 파일 | 내용 |
|---|---|
| `dose_grid_meta_template.json` | 메타데이터 양식. 복사해서 값만 바꿔 쓰면 됩니다 |
| `sample/dose_grid_pre.npy`, `_meta.json` | 가상 선원으로 만든 샘플 (형식 참고용, 값은 의미 없음) |
| `sample/dose_grid_post.npy`, `_meta.json` | 위와 같음, 베드 제거 후 |
| `sample/*_quicklook.png` | 점검 도구가 만드는 단면 그림 예시 |
| `dose_model.py` | 선량률 함수 인터페이스와 참조 구현 (점·선 선원, 1/r² 해석식) |
| `check_dose_grid.py` | 점검 도구 |
| `dose_grid.py`, `layout_plot.py`, `viz_style.py` | 점검 도구가 쓰는 모듈 |
| `hotcell_layout.json` | 좌표계와 배치 초안 (02_layout과 같은 파일) |

## 격자 규약

가장 자주 틀리는 부분은 축 순서와 원점입니다.

- **좌표계**: `hotcell_layout.json`의 `hotcell_world`. 원점은 로봇 베이스 바닥 중심, x는 로봇에서 베드 쪽, y는 그 왼쪽, z는 위. 단위 m.
- **축 순서** `axis_order = "xyz"`: `arr[i, j, k]` 는 좌표 `(x0 + i*dx, y0 + j*dy, z0 + k*dz)` 의 값입니다. numpy로 만들 때 `np.meshgrid(x, y, z, indexing="ij")`를 쓰면 이 순서가 됩니다. 기본값 `indexing="xy"`를 쓰면 x와 y가 뒤바뀝니다.
- **노드 기준** `sample_location = "node"`: 값은 격자점 위의 값이고, `origin`은 `arr[0, 0, 0]`이 놓인 좌표입니다. 복셀 중심값으로 계산했다면 origin을 복셀 중심 좌표로 적어 주세요.
- **단위** `Gy/h`, **매질** 기본 `Si`. 로봇 부품의 TID(Gy)와 바로 비교하기 위해 Sv가 아닌 Gy를 씁니다. 다른 매질로 계산했다면 `medium`에 적어 주세요.
- **범위**: 최소 x −0.8~1.2, y −1.0~1.0, z 0~1.5 m (핫셀 내부). 넘치는 것은 괜찮습니다.
- **해상도**: 간격 0.02 m(축마다 100점 수준)를 권장합니다. 아래 검증 결과 참고.
- **자료형**: float32 권장 (100³ 격자 1개 약 4 MB).
- **값**: 0 이상, NaN 없음.

## 해상도 권장 근거

점선원 옆을 직선으로 지나갈 때의 누적선량을 해석해와 비교했습니다 (방향과 위치를 무작위로 바꿔 24회, 3선형 보간).

| 격자 간격 | 선원 10 cm 옆 | 15 cm | 20 cm | 30 cm | 50 cm |
|---|---|---|---|---|---|
| 8.3 cm (N=25) | 32% | 6.0% | 3.4% | 1.4% | 0.8% |
| 4.1 cm (N=50) | 3.2% | 1.4% | 0.7% | 0.3% | 0.1% |
| 2.0 cm (N=100) | 0.6% | 0.2% | 0.1% | 0.1% | 0.0% |

보간은 항상 과대평가 쪽으로 틀립니다. 해제·체결(S2, S5) 때 공구 끝이 베드에서 수 cm 거리까지 다가가므로, 이 구간의 Bed A 기여는 격자보다 `sources` 기반 해석식이 정확합니다. 그래서 `sources`에 베드 선원을 정확히 적어 주는 것이 중요합니다.

## 메타데이터 항목

| 항목 | 예 | 설명 |
|---|---|---|
| `schema_version` | `"1.0"` | 이 규격의 버전 |
| `grid_id` | `"rad_pre_v1"` | 격자 이름 |
| `state` | `"pre_removal"` | `pre_removal` 또는 `post_removal` |
| `data_file` | `"dose_grid_pre.npy"` | 짝이 되는 배열 파일 |
| `dtype` | `"float32"` | 배열 자료형 |
| `shape` | `[100, 100, 100]` | 배열 크기 (Nx, Ny, Nz) |
| `axis_order` | `"xyz"` | 고정 |
| `sample_location` | `"node"` | 고정 |
| `origin` | `[-0.8, -1.0, 0.0]` | `arr[0,0,0]`의 좌표 [m] |
| `spacing` | `[0.0202, 0.0202, 0.0202]` | 축별 간격 [m] |
| `frame` | `"hotcell_world"` | 고정 |
| `layout_version` | `"0.1-draft"` | 계산에 쓴 배치도 버전 |
| `quantity` | `"absorbed_dose_rate"` | 흡수선량률 (공기 커마율이면 `air_kerma_rate`) |
| `medium` | `"Si"` | 흡수선량 기준 매질 |
| `units` | `"Gy/h"` | 고정 |
| `shielding_included` | `false` | 구조물(베드 용기, 배관 벽 등) 차폐 반영 여부 |
| `sources` | 아래 참고 | 선원 목록 |
| `r_min` | `0.05` | 선원 반경 [m]. 이보다 가까운 거리는 이 값으로 계산 |
| `version`, `created_by`, `created_at`, `method`, `notes` | | 버전, 작성자, 작성일, 계산 방법, 가정 |

`sources` 항목 하나의 형식:

```json
{"id": "bed_A", "kind": "line", "start": [0.50, -0.28, 0.07], "end": [0.50, -0.28, 0.43],
 "strength": 1.0, "nuclides": [{"name": "Kr-85", "activity_Bq": 0.0}], "note": "근거"}
```

- `kind`: `point`(`position`), `line`(`start`, `end`), `polyline`(`points`)
- `strength`: 그 선원 전체를 1 m 거리의 점선원으로 봤을 때의 선량률 [Gy/h]
- `bed_A`라는 id는 그대로 써 주세요. S3 이동 선원 계산에서 이 id를 찾습니다.

## 격자 만드는 예시

```python
import numpy as np
from dose_grid import make_meta, save

origin = np.array([-0.8, -1.0, 0.0])
upper = np.array([1.2, 1.0, 2.0])
n = 100
spacing = (upper - origin) / (n - 1)
x, y, z = (origin[i] + spacing[i] * np.arange(n) for i in range(3))
X, Y, Z = np.meshgrid(x, y, z, indexing="ij")      # 반드시 "ij"
arr = my_dose_rate(X, Y, Z).astype(np.float32)     # Gy/h, 자체 계산 함수

meta = make_meta(grid_id="rad_pre_v1", state="pre_removal", data_file="dose_grid_pre.npy",
                 arr=arr, origin=origin, spacing=spacing, sources=[...],
                 layout_version="0.1-draft", created_by="이름", method="계산 방법")
save(arr, meta, ".")
```

## 10/5 회의에서 같이 정할 것

1. 선원항: Kr-85만 쓰는지. Kr-85는 감마 분기가 0.43%뿐이라 감마선량이 매우 작게 나올 수 있습니다. 교체 시점 베드에 남은 단수명 핵종(Kr-88, Xe-135 등)과 제동복사를 반영하는지.
2. 구조물 차폐(`shielding_included`)를 격자에 넣을지, 경로계획 쪽에서 가시선 감쇠로 넣을지.
3. 기준 감마 에너지 (소재 파트의 μ/ρ 선택과 맞춰야 합니다).

샘플 격자의 값은 가상 선원(Bed A 1.0, Bed B 0.5 Gy/h at 1 m 등)으로 만든 것이라 절대값에는 의미가 없습니다.
