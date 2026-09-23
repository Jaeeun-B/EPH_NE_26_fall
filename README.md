# EPH_NE_26_fall - Git 사용 가이드

이 저장소는 EPH engineering team이 각자 작업한 코드를 공유하고 기록으로 남기기 위한 작업소입니다.

**`main` 브랜치에는 직접 작업하지 않고, 반드시 자신의 개인 브랜치에서만 작업합니다.**
**PR(Pull Request) 및 merge 요청, 즉 `main` 브랜치로의 합병은 임의로 진행하지 말고 항상 카톡방으로 먼저 연락하세요.**

---

## 1. Git 설치

### macOS

1. 터미널(Terminal) 앱을 엽니다. (`Cmd + Space` → "터미널" 검색)
2. 아래 명령어로 Git이 이미 설치되어 있는지 확인합니다.
   ```bash
   git --version
   ```
   버전이 바로 출력되면 이미 설치된 것입니다. 설치 안내 창이 뜨면 그대로 따라가 설치를 완료하세요.
3. 버전이 뜨지 않는다면 [Homebrew](https://brew.sh)로 설치합니다.
   ```bash
   brew install git
   ```

### Windows

1. [git-scm.com](https://git-scm.com/download/win) 에서 Windows용 설치 파일을 내려받습니다.
2. 설치 마법사를 실행하고, 대부분의 옵션은 기본값(Next)으로 진행해도 됩니다.
   - "Adjusting your PATH environment" 단계는 권장 옵션(Git from the command line and also from 3rd-party software)을 선택하세요.
3. 설치가 끝나면 시작 메뉴에서 **Git Bash**를 실행합니다. Windows에서는 명령 프롬프트(cmd) 대신 **Git Bash**를 사용하는 것을 권장합니다. (아래 명령어들은 macOS 터미널과 동일하게 동작합니다.)
4. 설치 확인:
   ```bash
   git --version
   ```

---

## 2. 최초 1회 설정 (macOS / Windows 공통)

이름과 이메일을 등록해야 커밋 기록에 본인 이름이 정확히 남습니다.

```bash
git config --global user.name "본인 이름 또는 GitHub ID"
git config --global user.email "GitHub에 등록한 이메일"
```

---

## 3. 저장소 클론(복제)하기

작업할 폴더로 이동한 뒤 저장소를 내 컴퓨터로 복제합니다.

```bash
git clone https://github.com/Jaeeun-B/EPH_NE_26_fall.git
cd EPH_NE_26_fall
```

GitHub 로그인을 요구하면 계정 정보(또는 Personal Access Token)를 입력합니다.

---

## 4. 본인 브랜치로 이동하기

**`main` 브랜치에서 직접 작업하지 않습니다.** 항상 자신의 이름으로 된 브랜치로 이동한 뒤 작업을 시작하세요.

원격에 본인 브랜치가 이미 만들어져 있다면:

```bash
git checkout 본인브랜치이름
```

예시: `git checkout Jaeeun-B`

본인 브랜치가 아직 없다면 새로 만듭니다.

```bash
git checkout -b 본인브랜치이름
git push -u origin 본인브랜치이름
```

> 지금 어느 브랜치에 있는지 확인하려면 언제든 `git branch` 를 입력하세요. `*` 표시가 있는 브랜치가 현재 위치입니다.

---

## 5. 작업 후 저장하고 공유하기 (add → commit → push)

코드를 수정한 뒤에는 다음 순서로 진행합니다.

1. **변경 사항 확인**
   ```bash
   git status
   ```
2. **변경된 파일 스테이징**
   ```bash
   git add .
   ```
   특정 파일만 올리고 싶다면 `git add 파일이름` 처럼 지정할 수 있습니다.
3. **커밋(기록 남기기)**
   ```bash
   git commit -m "무엇을 했는지 짧게 설명"
   ```
   예: `git commit -m "로그인 화면 UI 초안 작성"`
4. **본인 브랜치에 푸시(업로드)**
   ```bash
   git push
   ```
   처음 푸시하는 브랜치라면 `git push -u origin 본인브랜치이름` 을 사용하세요.

---

## 6. 다른 사람 작업 / main 최신 내용 가져오기

`main`의 최신 내용을 내 컴퓨터로 가져오고 싶을 때:

```bash
git checkout main
git pull
```

이후 본인 브랜치로 돌아가 `main`의 최신 내용을 반영하고 싶다면:

```bash
git checkout 본인브랜치이름
git merge main
```

---

## 7. 브랜치 규칙 요약

| 규칙 | 설명 |
|---|---|
| `main`에 직접 커밋/푸시 금지 | 항상 본인 브랜치에서만 작업 |
| 브랜치 이름 = 본인 이름 | 예: `Jaeeun-B`, `Seohyun-Y` |
| 커밋 메시지는 짧고 명확하게 | 무엇을 했는지 한눈에 알 수 있도록 |
| main에 합치고 싶을 때 | GitHub에서 Pull Request(PR)를 생성해 리뷰 후 병합 |
| **PR 및 merge 요청 (= main 브랜치 합병)** | **절대 임의로 진행하지 말고, 항상 카톡방으로 먼저 연락하기!** |

---

## 8. 자주 발생하는 문제

**Q. `git push`를 했는데 오류가 난다 (`rejected`, `non-fast-forward` 등)**
원격 브랜치가 로컬보다 최신 상태일 수 있습니다. 먼저 최신 내용을 받아온 뒤 다시 푸시하세요.
```bash
git pull
git push
```

**Q. 실수로 `main` 브랜치에서 작업을 시작했다**
커밋하기 전이라면 바로 본인 브랜치로 옮길 수 있습니다.
```bash
git checkout -b 본인브랜치이름
```

**Q. GitHub 로그인 시 비밀번호가 거부된다**
GitHub는 비밀번호 대신 Personal Access Token(PAT)을 요구합니다. GitHub 계정 설정 → Developer settings → Personal access tokens 에서 발급받아 비밀번호 자리에 입력하세요.

**Q. 다음에 뭘 해야 할지 모르겠다**
`git status`를 습관적으로 자주 입력하세요. 지금 상태와 다음에 할 일을 안내해 줍니다.

---

궁금한 점이 있으면 팀 채널에 편하게 물어보세요.
