# VS Code에서 Claude Code로 이 프로젝트 다루기

이 저장소에는 Claude Code 설정이 들어 있습니다. 설치하고 폴더를 열면 바로 쓸 수 있습니다.

## 1. 설치 (한 번만)

### VS Code 확장

VS Code에서 `Cmd + Shift + X` → "Claude Code" 검색 → Anthropic이 만든 것을 설치합니다. 이 확장은 CLI를 함께 들고 있어서 채팅 패널만 쓸 거면 추가 설치가 필요 없습니다.

### 터미널에서도 쓰려면

VS Code 안의 터미널에서 `claude` 명령을 쓰려면 따로 설치합니다.

```bash
brew install --cask claude-code
```

설치 확인:
```bash
claude --version
```

## 2. 폴더 열기

**중요합니다.** VS Code에서 열 폴더는 저장소 루트가 아니라 `dose-aware-traj`입니다.

```
EPH_NE_26_fall/
└── dose-aware-traj/   ← 이 폴더를 연다
```

이 폴더에 `CLAUDE.md`와 `.claude/`가 있어서, 여기서 열어야 설정이 적용됩니다. 저장소 루트를 열면 팀 공용 README만 읽고 이 프로젝트 규칙은 못 읽습니다.

```bash
cd ~/Desktop/workspace/26_02/EPH_BJE/EPH_NE_26_fall/dose-aware-traj
code .
```

처음 열면 VS Code가 추천 확장을 설치할지 묻습니다. 설치하면 Python, Jupyter, 마크다운, PDF 뷰어가 함께 들어옵니다.

### Python 환경 지정

`Cmd + Shift + P` → "Python: Select Interpreter" → conda 환경 `eph`를 고릅니다. 이걸 해두면 VS Code 터미널이 자동으로 `conda activate eph` 상태가 됩니다.

## 3. 무엇이 들어 있나

```
dose-aware-traj/
├── CLAUDE.md              ← Claude가 매번 먼저 읽는 규칙
├── .claude/
│   ├── settings.json      권한 설정 (팀 공유)
│   ├── agents/            전문 에이전트 5종
│   └── commands/          슬래시 명령 6종
├── .vscode/               VS Code 설정
├── docs/
│   ├── invariants.md      항상 성립해야 하는 조건
│   ├── adr/               결정 기록
│   ├── run_log.md         실행 기록
│   └── *.md               분석 문서
└── refs/                  논문 PDF와 정리 노트
```

### 에이전트 5종

전문 분야별로 나눠 둔 하위 작업자입니다. 그냥 평소처럼 말하면 Claude가 알아서 부릅니다. 직접 부르고 싶으면 이름을 말하면 됩니다.

| 이름 | 하는 일 | 이렇게 말하면 불림 |
|---|---|---|
| `result-verifier` | 문서 수치가 실제 결과와 맞는지 검증 | "수치 확인해줘", "문서랑 맞는지 봐줘" |
| `planner` | 구현 전 계획 수립 (코드를 못 고침) | "P3 어떻게 구현할지 계획해줘" |
| `paper-reader` | PDF 논문 읽고 노트 작성 | "이 논문 정리해줘" |
| `handoff-checker` | 다른 파트가 보낸 파일 점검 | "격자 받았는데 확인해줘" |
| `doc-updater` | 결과 바뀐 뒤 문서 수치 갱신 | "문서 갱신해줘" |

`planner`에게 일부러 읽기 권한만 줬습니다. 계획을 세우라고 했는데 코드부터 고치는 일을 막기 위해서입니다.

### 슬래시 명령 6종

채팅창에 `/`를 치면 목록이 뜹니다.

| 명령 | 하는 일 |
|---|---|
| `/run-all` | 전체 파이프라인 실행하고 수치 요약 |
| `/check` | 문서 수치를 실제 결과와 대조 |
| `/new-grid <경로>` | 방사선 격자 받았을 때 점검하고 반영 |
| `/adr <주제>` | 결정 기록 한 장 작성 |
| `/log-run` | 방금 실행 결과를 run_log에 기록 |
| `/weekly` | 팀 회의용 진행 상황 정리 |

## 4. 실제로 쓰는 흐름

### 회의 전

```
/weekly
```
git 기록, 실행 기록, ADR을 훑어서 "한 것 / 막힌 것 / 요청값 / 다음 주"를 정리합니다. 커밋과 실행 기록에 없는 것은 쓰지 않으므로, 과장되지 않습니다.

### 코드를 고친 뒤

```
/run-all
/check
```
먼저 전체를 돌리고, 그다음 문서 수치가 아직 맞는지 봅니다. 불일치가 나오면 `doc-updater`에게 고치게 합니다.

### 다른 파트에서 값이 왔을 때

```
/new-grid ~/Downloads/dose_grid_pre.npy
```
단위, 좌표계, 축 순서를 먼저 봅니다. 이런 건 틀려도 에러가 안 나고 조용히 틀린 숫자가 나오기 때문에 점검이 먼저입니다.

### 논문을 읽을 때

PDF를 `refs/`에 넣고 "이 논문 정리해줘"라고 합니다. 쪽 번호가 붙은 노트가 `refs/notes/`에 생깁니다.

### 새 알고리즘을 만들 때

"P3 자세 최적화 계획 세워줘"라고 하면 `planner`가 기존 코드를 읽고 계획을 씁니다. 계획을 보고 괜찮으면 "이대로 구현해줘"라고 합니다.

## 5. 권한 설정

`.claude/settings.json`에 적혀 있습니다.

**허용**: `python scripts/*` 실행, git 읽기 명령, 파일 보기. 매번 묻지 않습니다.

**금지**: `git push`, `git commit --amend`, `git reset --hard`, `git rebase`, `main` 브랜치 체크아웃, `rm -rf`, `git add -f`.

push를 막아 둔 것은 의도한 것입니다. 무엇이 올라가는지 직접 보고 올리세요. 커밋까지는 Claude가 해도 됩니다.

> 참고: 이 규칙은 Claude가 보통 쓰는 명령 형태를 막는 것이지 보안 장치가 아닙니다. `git -C . push`처럼 형태를 바꾸면 규칙을 비껴갈 수 있습니다. 실수를 줄이는 울타리로만 보세요.

목록에 없는 명령은 실행 전에 물어봅니다. 자주 쓰는데 매번 묻는 게 있으면 `.claude/settings.json`의 `allow`에 추가하세요. 나만 쓸 설정은 `.claude/settings.local.json`에 넣으면 git에 올라가지 않습니다.

## 6. 왜 이렇게 만들었나

Claude가 가장 자주 하는 실수 두 가지를 막는 데 초점을 뒀습니다.

**수치를 지어내는 것.** 이 프로젝트는 숫자가 결론입니다. 그래서 `CLAUDE.md`에 "확인한 값만 쓴다", "모르면 `미정 — <확인 방법>으로 확인 필요`라고 쓴다"를 규칙으로 박아 뒀고, `/check`로 언제든 대조할 수 있게 했습니다.

**확인하지 않고 다 됐다고 하는 것.** `result-verifier`와 `/run-all`에 "검증이 끝까지 돌지 못했으면 이상 없음이라고 보고하지 말 것"을 넣었습니다. 확인 못 한 것은 통과가 아닙니다.

여기에 더해, 선량 모델에서 조용히 틀리는 경우(단위, 축 순서, toppra 미사용)를 `docs/invariants.md`에 목록으로 만들어 검증이 매번 보게 했습니다.

작업 태도 네 가지 규칙은 [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills)에서, 계획과 검증 구조는 [everything-claude-code](https://github.com/giovanisp/everything-claude-code)의 PRD/ADR/verification 패턴에서 가져와 이 프로젝트에 맞게 줄였습니다.

## 7. 설정을 고치고 싶을 때

| 고치고 싶은 것 | 고칠 파일 |
|---|---|
| 프로젝트 규칙, 말투, 금지 사항 | `CLAUDE.md` |
| 나만 쓸 규칙 (git에 안 올라감) | `CLAUDE.local.md` |
| 에이전트 동작 | `.claude/agents/<이름>.md` |
| 슬래시 명령 | `.claude/commands/<이름>.md` |
| 권한 | `.claude/settings.json` (공유) 또는 `.claude/settings.local.json` (개인) |

에이전트 파일의 `description`이 "언제 이 에이전트를 부를지"를 결정합니다. 원하는 때에 안 불리면 `description`을 더 구체적으로 쓰세요.

고친 뒤에는 Claude Code를 다시 시작해야 반영됩니다.
