# 공통 파라미터 (제어 파트용)

경로계획(PyBullet 7축)과 제어(Simscape 1~2관절) 모델이 같은 값을 쓰도록 하나의 파일로 관리합니다. 값을 바꿀 일이 생기면 이 파일을 고치고 `params_version`을 올립니다.

## 파일

| 파일 | 내용 |
|---|---|
| `shared_params.json` | 로봇 관성·한계, 공구, 운반물, 경사 조건, 2관절 축약 모델 |
| `e_track_template.csv` | 제어 파트가 채워 줄 경사 조건별 추종오차 양식 |
| `traj_b0.csv` | B0 기준선 궤적 예시 (S1~S6 전체, 7축 각도·각속도·각가속도·토크, 100 Hz) |
| `traj_b0_A2A4.csv` | 위 궤적에서 A2, A4만 뽑은 것 (Simscape 2관절 입력용) |

MATLAB에서 읽기:

```matlab
p = jsondecode(fileread('shared_params.json'));
r = p.reduced_2dof;
l1 = r.link1.length;  m1 = r.link1.mass;  lc1 = r.link1.com_along_link;  I1 = r.link1.inertia_about_com;
```

## 2관절 축약 모델 (`reduced_2dof`)

7축 중 중력 토크를 가장 크게 받는 A2(어깨 피치)와 A4(팔꿈치 피치)만 남기고, 나머지 관절을 0으로 고정한 채 링크를 묶은 값입니다.

| 항목 | link1 (A2→A4) | link2 (A4→TCP) |
|---|---|---|
| 길이 [m] | 0.42 | 0.626 (플랜지까지 0.526) |
| 질량 [kg] | 9.85 | 11.5 (공구 1.5 kg 포함) |
| 관절에서 질량중심까지 [m] | 0.157 | 0.290 |
| 질량중심 기준 관성 [kg·m²] | 0.225 | 0.405 |
| 토크 한계 [N·m] | 320 | 176 |

- 운반물: 사용 후 베드 9.0 kg, 신규 베드 8.0 kg, A4에서 0.856 m 위치의 점질량 (S3, S4 운반 중에만)
- 부호: A4 축은 A2 축과 반대 방향(`A4_axis_sign_relative_to_A2 = -1`)입니다. 평면 모델의 두 축을 같은 방향으로 잡으면 q2 = −A4, 토크도 부호를 바꿉니다.
- 질량·관성 출처: RobotLocomotion/models의 iiwa14 URDF (KUKA 데이터시트 총중량 30 kg과 맞음). 토크·속도·가속도 한계도 같은 파일 값입니다.

## 경사 조건 (`inclination_envelope`)

선박 기관 설계 기준(46 CFR 58.01-40)을 준용했습니다. 해양 원자로 전용 요건이 확인되면 바꿉니다.

| case | 횡동요 roll | 종동요 pitch |
|---|---|---|
| level | 0° | 0° |
| static_port / static_stbd | ±15° | 0° |
| dyn_pp, dyn_pm, dyn_mp, dyn_mm | ±22.5° | ±7.5° |

중력 벡터는 `g_ship = R_y(pitch)ᵀ R_x(roll)ᵀ [0, 0, −9.81]` (선체 고정 좌표계 기준)로 회전시킵니다. 1차 버전은 준정적 근사입니다.

## 요청 사항

1. 경사 조건별 최대·RMS 추종오차를 `e_track_template.csv`에 채워 주세요. 경로계획 쪽은 장애물 여유거리를 `d_safe + e_track`으로 잡습니다. 제어 성능이 좋을수록 더 좁은 저선량 통로를 쓸 수 있게 됩니다.
2. `traj_b0_A2A4.csv`로 Simscape 모델을 한 번 돌려 봐 주세요. 배치 초안과 가상 선원 기준의 예시라 값은 바뀌지만 형식은 이대로 갑니다.
   - 열: `t`[s], `stage`(S1~S6), `carrying`(운반 중인 베드: spent/new/빈칸), 각도[rad], 각속도[rad/s], 각가속도[rad/s²], 토크[N·m]
   - 토크는 경사 0도, 운반 중인 베드를 포함한 7축 역동역학 값입니다 (5샘플마다 계산, 나머지는 빈칸)
   - 체류 구간(S2, S5)은 1초 간격으로 같은 자세가 반복됩니다
3. 축약 모델을 손목을 굽힌 자세 기준으로 다시 묶어야 하면 말해 주세요. 같은 코드로 바로 계산할 수 있습니다.
