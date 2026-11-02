# Numbers로 포스터 그림 다시 그리기

데이터: `outputs/poster/tables/E_poster_figure_data.xlsx` (시트별), 같은 내용의 CSV 4개
생성: `python scripts/14_poster_figures.py`

xlsx를 Numbers에서 열면 시트마다 탭 하나씩 생김. 표 하나가 그림 하나임.

## 0. 공통 스타일 (세 그림 모두)

- 색: 아래 HEX를 계열 채우기에 직접 입력 (포맷 사이드바 > 계열 > 채우기 > 색상 > 색상 팔레트의 HEX)

| 쓰임 | HEX |
|---|---|
| 주 계열 (카메라, 체류, 부품 기준 + 카메라) | `#2A78D6` |
| 대비 계열 (TCP, 근접 직선) | `#EB6834` |
| 세 번째 계열 (경로계획, 부품 기준) | `#1BAF7A` |
| TCP 합계 막대, 한계선 | `#898781` |
| 축 글자, 보조 글자 | `#52514E` |
| 격자선 | `#E1E0D9` |

- 글꼴: 패널 본문과 같은 글꼴 하나로 통일 (Mac에서는 Helvetica Neue 또는 Avenir Next). 패널 한 단이 약 125 mm라 차트 글자 10~11 pt, 축 제목 11 pt 이상
- 차트 배경·테두리·그림자 X, 3D X
- 격자선은 값 축 쪽만 얇게 (포맷 > 축 > 값 축 > 주 격자선, 가장 얇은 선, 색 `#E1E0D9`)
- 범례는 데이터와 겹치지 않는 빈 곳으로 끌어서 이동, 범례 테두리 X
- 마이너스 기호: Numbers 기본 표기 그대로 써도 됨

## 1. Fig. 1 부품별 누적선량 (시트 `Fig1_component_dose`)

표 구성
- `Label`: 부품 이름 + 합계 (예: `C09 Wrist camera  1.00`) -> 막대 끝에 합계를 따로 쓰지 않아도 됨
- `Dwell (unlock, lock, grasp)`, `Near-bed moves (5 cm/s)`, `Planned transfers`: 쌓을 값
- `TCP total (point-robot model)`: TCP 행에만 값이 있음 -> TCP만 회색 막대 하나로 보이게 하는 장치
- `Total`: 합계 수식 (차트에는 넣지 않음)

만드는 법
1) `Label` 열과 `Dwell`, `Near-bed moves`, `Planned transfers`, `TCP total` 4개 열을 선택 (`Component`, `Total` 열은 빼기)
2) 도구 막대 차트 > 2D > 누적 가로 막대 (Stacked Bar)
3) 계열 색: Dwell `#2A78D6`, Near-bed `#EB6834`, Planned `#1BAF7A`, TCP total `#898781`
4) 포맷 > 차트 > 간격: 막대 사이 30~40%
5) 값 축(가로): 최소 0, 최대 2.0, 단위 0.5. 축 제목 `Dose over one exchange (wrist camera C09 = 1, virtual source)`
6) 표는 TCP가 맨 위, C10이 맨 아래 순서로 되어 있음. 차트에서 순서가 거꾸로 나오면 표 행을 `Total` 기준으로 정렬 방향만 바꾸면 됨
7) 강조하고 싶으면 값 1.0 위치에 세로 점선 하나 (도형 > 선, 점선, `#898781`)

## 2. Fig. 2 개선 수단별 효과 (시트 `Fig2_levers`)

표 구성
- `Label`: 수단 + 가중합 J (예: `Camera mount optimization (J -25.8%)`)
- `Wrist camera C09 [%]`, `TCP (point-robot model) [%]`: 막대 2계열 (퍼센트 서식)
- `Weighted sum J [%]`: 이름표에 이미 들어 있음
- `C09 range low/high [%]`: 카메라 장착 위치의 제약 가정 범위 (카메라 행만)

만드는 법
1) `Label`, `Wrist camera C09 [%]`, `TCP (point-robot model) [%]` 3개 열 선택
2) 차트 > 2D > 가로 막대 (Bar)
3) 계열 색: C09 `#2A78D6`, TCP `#EB6834`
4) 값 축: 최소 -100%, 최대 5%, 단위 20%. 축 제목 `Dose change vs. B0 (time-optimal baseline) [%]`
5) 포맷 > 계열 > 값 레이블 켜기, 위치는 막대 끝 바깥, 소수점 1자리
6) TCP 막대는 대부분 0%라 안 보임 -> 그게 메시지임. 값 레이블 `0.0%`가 보이게 두고, 캡션에 "TCP unchanged" 명시
7) 카메라 범위(-81 ~ -72%)는 오차 막대로 넣기보다 캡션에 쓰는 것을 권장 (Numbers 오차 막대는 계열 전체에 같은 설정이 걸려서 한 막대에만 넣기 번거로움)

## 3. Fig. 3 설계 방식별 모듈 질량 (시트 `Fig3_module_mass`, `Fig3_summary`)

표 구성
- `Exchange interval [days]`: 3.25~20일, 0.25일 간격 (등간격이라 꺾은선 차트로 그려도 x 간격이 맞음)
- 설계 방식 3열 [kg]: TCP 기준 / 부품 기준 / 부품 기준 + 카메라 배치
- `KR 120 limit [kg]`, `KR 210 / KR 300 limit [kg]`: 모든 행이 같은 값 -> 수평 한계선으로 그려짐
- `Fig3_summary`: 로봇별 최대 교체 간격, 7일 간격 모듈 질량, 연간 교체 횟수 (수식)

만드는 법 (분산형 권장: x가 진짜 숫자 축)
1) `Fig3_module_mass` 시트 전체 선택 (6개 열, 첫 열이 x)
2) 차트 > 2D > 분산형 (Scatter). 분산형은 기본으로 모든 계열이 첫 열을 x로 같이 씀 (데이터 참조 편집(Edit Data References) > 아래 막대 팝업 > X 값 공유(Share X Values)에 체크 표시)
3) 포맷 > 계열: 연결선 직선, 데이터 기호 없음
4) 계열 색과 선: TCP 기준 `#EB6834`, 부품 기준 `#1BAF7A`, 부품 기준 + 카메라 `#2A78D6` (선 굵기 2.5~3 pt)
5) 한계선 2개: 색 `#898781`, 점선, 1 pt. 범례에서는 지우고 선 오른쪽 끝에 텍스트 상자로 `KR 120 limit 120 kg`, `KR 210 / KR 300 limit 145 kg`
6) 축 크기: x 최소 3, 최대 20, 주 단계 2일 간격 / y 최소 50, 최대 260, 25 kg 간격
7) 축 제목: x `Exchange interval = bed operating time [days]`, y `Module mass [kg] (sorbent + vessel + W shield)`
8) KR 120과 만나는 점 강조: `Fig3_summary`의 `Max interval with KR 120 [days]`(5.26, 7.12, 9.84일)를 텍스트 상자로 표시 (`5.3 d`, `7.1 d`, `9.8 d`, 각 계열 색)

대안 (꺾은선)
- x가 0.25일 등간격이라 꺾은선(Line)으로 그려도 모양은 같음
- 다만 x가 범주로 취급돼 눈금 레이블이 68개 생기므로 분산형이 더 깔끔함

## 4. Keynote나 다른 도구로 옮길 때

- Numbers 차트를 복사해서 Keynote에 붙이면 편집 가능한 차트로 들어감
- 인쇄용 고정 그림이 필요하면 파일 > 내보내기 > PDF
- Python으로 만든 그림(`outputs/poster/fig*.svg`, `fig*.pdf`)도 그대로 쓸 수 있음. Numbers 그림과 섞어 쓸 때는 색과 글꼴만 맞추면 됨

## 주의

- Fig. 1~2는 가상 선원 기준 상대값. 축 제목이나 캡션에 "virtual source, relative" 표시를 빼지 말 것
- Fig. 3은 상한 추정 (방출분율 1, 자체차폐·빌드업 없음)
- 표 값을 손으로 고치지 말고, 바꿀 일이 있으면 스크립트를 다시 돌려서 새 표를 받을 것
