# 선량 격자 폴더

- `python scripts/01_make_virtual_grids.py` 를 실행하면 가상 격자 `dose_grid_{pre,post}_N{25,50,100}.npy` 와 메타데이터가 생긴다 (git에는 올리지 않음).
- 방사선 파트 격자를 받으면 `dose_grid_pre.npy`, `dose_grid_pre_meta.json`, `dose_grid_post.npy`, `dose_grid_post_meta.json` 이름으로 이 폴더에 넣고
  `python scripts/check_dose_grid.py data/dose_grids/dose_grid_pre.npy` 로 점검한 뒤
  `python scripts/06_run_b0.py --field grid --N 0` 처럼 `--N 0` 을 주면 이 파일들을 쓴다.
