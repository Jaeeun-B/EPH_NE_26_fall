# 환경 설정 (Apple Silicon Mac 기준)

M1~M4 맥북에서 처음부터 따라 하는 순서입니다. 30분 정도 걸립니다. 모든 명령은 **터미널** 앱에서 입력합니다.

PyBullet과 TOPP-RA는 Apple Silicon용으로 미리 빌드된 pip 패키지가 없어서, pip로 바로 설치하면 컴파일하다가 실패하기 쉽습니다. 그래서 PyBullet은 conda-forge에 올라와 있는 빌드를 쓰고, TOPP-RA만 pip로 컴파일합니다. (macOS, Apple M4 Pro, Python 3.11에서 이 순서로 설치해 전체 스크립트가 도는 것을 확인했습니다. 2026-10-02)

---

## 1. Xcode 명령줄 도구 설치

TOPP-RA를 컴파일할 때 C 컴파일러가 필요합니다.

```bash
xcode-select --install
```

창이 뜨면 설치를 누릅니다. `already installed`가 나오면 이미 있는 것이니 넘어가면 됩니다.

## 2. Miniforge(conda) 설치

conda가 이미 있으면 (`conda --version`이 나오면) 3단계로 넘어갑니다.

```bash
cd ~/Downloads
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash Miniforge3-$(uname)-$(uname -m).sh
```

- 약관은 스페이스로 넘기고 `yes`
- 설치 위치는 엔터 (기본 `~/miniforge3`)
- 마지막에 `conda init`을 할지 물으면 `yes`

**터미널을 완전히 닫고 새로 엽니다.** 프롬프트 앞에 `(base)`가 보이면 성공입니다.

## 3. 프로젝트 폴더 준비와 가상환경 만들기

받은 `dose-aware-traj.zip`을 원하는 곳에 풉니다. 예시는 `~/Projects`입니다.

```bash
mkdir -p ~/Projects
cd ~/Projects
unzip ~/Downloads/dose-aware-traj.zip
cd dose-aware-traj
```

가상환경을 만듭니다. `environment.yml`에 필요한 패키지가 모두 적혀 있습니다 (5분 안팎).

```bash
conda env create -f environment.yml
conda activate eph
```

프롬프트 앞이 `(eph)`로 바뀌면 됩니다. **앞으로 터미널을 새로 열 때마다 `conda activate eph`를 먼저 입력합니다.**

## 4. 설치 확인

```bash
python scripts/00_check_env.py
```

모든 줄이 `[ok]`이고 마지막에 `환경 준비 완료`가 나오면 끝입니다.

- `toppra`만 `[선택] 없음`으로 나오면: 4-1 참고. 나머지 코드는 그대로 돌아갑니다.
- `pybullet`이 `[없음]`이면: `conda install -c conda-forge pybullet`

### 4-1. toppra 설치가 실패했을 때

```bash
xcode-select -p                            # 경로가 나와야 함. 안 나오면 1단계 다시
pip install cython numpy
pip install --no-build-isolation toppra
```

그래도 안 되면 건너뛰어도 됩니다. 이 경우 시간 매개변수화가 대체 방식으로 바뀌어 B0 궤적이 조금 느려지고, 토크 제약은 계산 중이 아닌 사후 점검으로만 확인됩니다.

## 5. 순서대로 실행

프로젝트 폴더(`dose-aware-traj`)에서 실행합니다. 결과는 `outputs/`에 쌓입니다.

| 순서 | 명령 | 하는 일 | 확인할 것 |
|---|---|---|---|
| 1 | `python scripts/01_make_virtual_grids.py` | 가상 선량 격자 (25³, 50³, 100³) 생성 | `data/dose_grids/`에 파일 6쌍 |
| 2 | `python scripts/check_dose_grid.py data/dose_grids/dose_grid_pre_N50.npy` | 격자 형식 점검 | `결과: 통과`, quicklook 그림 |
| 3 | `python scripts/02_build_scene.py --gui` | 핫셀 장면과 로봇 확인 | PyBullet 창. 마우스로 돌려보고 창을 닫으면 종료 |
| 4 | `python scripts/03_validate_line.py` | 직선 통과 해석해 대조 | 시간 간격·격자 해상도별 오차 |
| 5 | `python scripts/04_validate_arc.py` | 참고문헌 3 조건 재현 | TCP 선량 오차 0.000% |
| 6 | `python scripts/05_solve_waypoints.py` | S1~S6 웨이포인트 IK | 19개 구간 표, 자세 그림 |
| 7 | `python scripts/06_run_b0.py --gui` | B0 기준선 계획·평가 후 재생 | 부품별 선량, 토크 사용률 0.8 이하, 재생 창 |
| 8 | `python scripts/07_run_b1.py` | B1 (점 로봇 A*) 계획·평가 | B0 대비 비교 |
| 9 | `python scripts/08_payload_check.py` | 베드 질량별 토크 점검 | 허용 최대 질량 |
| 10 | `python scripts/10_export_handoff.py` | 인계 파일 다시 만들기 | `handoff/` |

PyBullet 창 조작: 왼쪽 드래그 회전, 휠 확대, Ctrl(또는 Cmd)+드래그 이동. `--speed 3`처럼 재생 배속을 줄 수 있습니다.

## 6. VS Code에서 열기 (선택)

1. VS Code에서 `파일 > 폴더 열기`로 `dose-aware-traj` 선택
2. 확장 프로그램에서 `Python`(Microsoft) 설치
3. `Cmd+Shift+P` → `Python: Select Interpreter` → `eph` 가 들어간 항목 선택
4. 스크립트는 VS Code 아래쪽 터미널에서 `python scripts/...`로 실행 (GUI 창은 터미널 실행이 안정적입니다)

## 7. GitHub 저장소 만들기

팀 공유용이면 **Private** 저장소를 권장합니다.

```bash
cd ~/Projects/dose-aware-traj
git init
git add .
git commit -m "E part: environment, dose evaluation, B0/B1 baselines"
```

GitHub 웹사이트에서 `New repository` → 이름 `dose-aware-traj`, Private, README 추가 **안 함** → Create. 화면에 나오는 주소로:

```bash
git branch -M main
git remote add origin https://github.com/<내 아이디>/dose-aware-traj.git
git push -u origin main
```

비밀번호를 물으면 GitHub 계정 비밀번호가 아니라 **Personal Access Token**을 넣어야 합니다 (GitHub `Settings > Developer settings > Personal access tokens`). Homebrew가 있다면 `brew install gh` 후 `gh auth login`으로 로그인해 두면 토큰을 따로 다루지 않아도 됩니다.

`outputs/`와 생성된 격자(`data/dose_grids/*.npy`)는 `.gitignore`에 들어 있어 올라가지 않습니다. 스크립트로 언제든 다시 만들 수 있습니다.

## 8. 자주 막히는 곳

| 증상 | 해결 |
|---|---|
| `conda: command not found` | 터미널을 새로 열기. 그래도 안 되면 `source ~/miniforge3/bin/activate` 후 `conda init zsh` |
| `ModuleNotFoundError: datraj` | 프로젝트 폴더 안에서 `python scripts/...` 형태로 실행했는지 확인 |
| `ModuleNotFoundError: pybullet` | `conda activate eph`를 안 한 상태. 프롬프트 앞이 `(eph)`인지 확인 |
| PyBullet 창이 안 뜨거나 바로 꺼짐 | VS Code 대화형 창이 아닌 터미널에서 실행. 창을 닫아야 프로그램이 끝남 |
| 그림의 한글이 네모로 보임 | macOS 기본 글꼴(Apple SD Gothic Neo)을 자동으로 찾음. 다른 OS면 Noto Sans CJK 또는 나눔고딕 설치 |
| `웨이포인트를 풀지 못했습니다` | `config/hotcell_layout.json`이나 `config/task.json`을 바꾼 뒤라면 그 위치가 로봇 도달 범위 밖. 메시지의 구간 이름 확인 |
