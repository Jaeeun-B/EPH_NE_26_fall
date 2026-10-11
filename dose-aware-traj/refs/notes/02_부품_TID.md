# 02 부품 TID 내성과 예산 (갈래 노트)

- 갈래: 선량 모델(TID, 부품 내성)
- 근거: 연구 원자료 노트 `component_tid.md`와 보고서 "방사선 환경 로봇 경로계획 참고문헌" (둘 다 저장소 밖). 논문 원문과 직접 대조하지 않았습니다.
- 2026-10-11 보강: 연구 원자료 노트 `component_tid_gaps.md`(공백 보충), `heavy_robots.md` Q3, 보고서 "MARINA 반영 참고문헌 보강" 5절, 팀원 입력 `_input_서현_1006.txt`. 2.1, 2.2, 2.8을 갱신하고 2.13~2.32를 추가했습니다.
- 조사일: 2026-10-06 (원자료 노트 기준)
- 파일: 모든 문헌이 PDF 없음. 파일명은 `refs/README.md` 표의 임시 이름입니다.
- 위치 표기: 쪽 번호가 없는 웹 자료는 표, 그림, 절 번호 또는 "초록"으로 적었습니다. 위치를 댈 수 없는 수치는 싣지 않고 소절의 "확인 못 한 것"에 항목 이름만 적었습니다.

## 갈래 요약

기계 부품(모터 권선 절연, 윤활제, O-링, 커넥터)의 시험 자료는 MGy 급으로, 이 프로젝트가 다루는 Gy 영역 선량보다 몇 자릿수 위에 있어 사실상 제약이 되지 않습니다. 실제로 예산을 좌우하는 것은 반도체가 들어간 부품(제어 전자부, 인코더 전자부, 카메라 센서, MCU)입니다. 상용 마이크로컨트롤러는 몇백 Gy에서 고장납니다. 다만 그 값은 0.09~0.18 Gy/s 라는 선박 환경보다 훨씬 높은 선량률의 빔 시험에서 얻은 것이라 설계 한계가 아니라 자릿수 기준점으로만 쓸 수 있습니다.

2026-10-11 보강 후의 요약: 공백이던 부품 중 숫자가 채워진 것은 iiwa 7 관절 7 광학 엔코더(전자부 포함) 164.55 Gy 고장(2.13), 홀 센서(400 Gy(Si)까지 무고장, 2.22)와 AMR 센서(2.21), 내방사선 레졸버-디지털 변환 체인(1 MGy 초과, 2.18, 2.19), 플래시 FPGA(2.20), 상용 카메라(150 Gy 전후 고장, 2.15), BK7 광학유리(4.9 kGy에서 이미 큰 손실, 2.28), 케이블 절연 재질별 값(2.23, 2.24)입니다. 메시지는 그대로입니다. **관절 전자부의 방어 가능한 TID_max는 100~300 Gy대이고 손목 카메라는 약 150 Gy, 케이블은 PTFE나 FEP를 쓰면 1~3 kGy, 아니면 100 kGy 이상**입니다(원자료 노트의 추론, 보고서 5절). 하모닉 드라이브, 토크 센서, 스트레인 게이지의 Gy 값은 이번에도 찾지 못했습니다. 단위는 출처 그대로이며 Gy(Si), Gy(SiO2), Gy(air)는 서로 바꿔 쓸 수 없고 환산 계수는 확보하지 못했습니다.

## 프로젝트와의 관계

- 부품별 `TID_max`(`config/components.json` 계열, 소재 파트의 `component_inputs.xlsx`)를 채울 때 상한 후보와 자릿수 기준을 제공하는 갈래입니다. 단 아래 공백 때문에 표의 많은 값은 이 갈래에서 공급되지 않습니다.
- `B_k = TID_max / N_ex` 분할 규칙의 선례는 찾지 못했습니다(아래 "예산 분할 선례").
- 차폐 투과율 `S_k`는 이 갈래에 표가 없습니다. 원자료 노트는 인용 대신 NIST XCOM이나 몬테카를로로 직접 계산하라고 권합니다. 2026-10-11 보강에서 NIST 질량감쇠계수로 계산한 납과 텅스텐 협빔 반가층을 2.31에 넣었습니다.
- 서현의 계획(팀원 입력 2026-10-06)은 부품별 TID_lim = 문헌 고장선량 / RDM(2)입니다. 이 노트는 "문헌 고장선량" 쪽 후보를 줍니다. RDM = 2라는 관행 자체의 출처는 이 조사 범위에서 확인하지 않았습니다(`00_확인필요_목록.md`). 고장선량 값은 대부분 높은 선량률 시험에서 얻은 것이라 선량률 효과(ELDRS, 어닐링) 때문에 자릿수 기준점으로 써야 합니다(2.13, 2.21, 2.22의 선량률 비교).
- Xe 단일 타겟 결정은 이 갈래의 TID 값에 영향을 주지 않습니다. 영향을 주는 것은 선원 스펙트럼입니다. Xe-133 위주(저에너지)로 냉각된 베드라면 얇은 국부 차폐가 통하지만, 고에너지 감마(Cs-138 등)가 남으면 cm 단위 차폐가 필요합니다(2.31, `08_오프가스_선원항.md`).

## 문헌별 정리

### 2.1 Noguchi et al. (2013) 　검증: verified (Table 1). 보고서 번호는 페이지에 없음

- 서지: "Irradiation test progress for the ITER maintenance robot", JAEA 보고서 BB2013-1301(번호는 URL 기준, 페이지에는 없음). https://jopss.jaea.go.jp/pdfdata/BB2013-1301.pdf
- 파일: `noguchi2013_iter_maintenance_robot` (PDF 없음)
- 한 줄 요약: ITER 유지보수 로봇 부품의 방사선 시험 경과 보고입니다.
- 프로젝트와의 관계: 기계부 한계의 상한을 제공합니다. MGy 급이라 Gy 영역의 예산에는 비제약임을 보이는 근거입니다.
- 방법: 부품별 조사 시험. 개선형 AC 서보 모터는 시험 진행 중입니다.

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| 상용 모터 8 MGy에서 절연 파괴로 고장 | 상용 AC 서보 모터 | Table 1 |
| 전기 커넥터 100 MGy | | Table 1 |
| 근접센서 >26 MGy | | Table 1 |
| 윤활 그리스 10 MGy | O-링과 통합 시험은 대기 중 | Table 1 |
| O-링 20 MGy | 카탈로그 기준 | Table 1 |
| 렌즈 접착제 3 MGy | | Table 1 |
| 영상 광섬유 3.1 MGy | | Table 1 |
| 카메라 2 MGy | 카탈로그 기준 | Table 1 |
| 브레이크 케이블이 8 MGy(500 Gy/h)에서 파손, 폴리이미드로 교체 | 폴리올레핀 피복 균열과 ETFE 절연 박리로 도체 노출 | Fig. 2 |

- 2026-10-11 보강(`heavy_robots.md` Q3): 같은 자료가 ITER 블랭킷 정비 환경을 약 0.5 kGy/h, 목표 수명을 5 MGy(250 Gy/h로 2년)로 적는다고 원자료 노트가 옮겼습니다(위치는 원자료 노트가 Table 1과 함께 표기, 표 안인지 본문인지 재확인 필요). 원자료 노트는 이 자료를 RSJ 2013(일본로봇학회 학술강연회) 발표로 표기합니다.
- 우리와 다른 점: MGy 급이라 Gy 영역과 거리가 큽니다. 대응 방식은 시험 후 재료 교체(폴리이미드)이고 교체 일정 계산이 아닙니다.
- 확인 못 한 것: 보고서 번호 확인. 발표 매체(JAEA 보고서 번호 대 RSJ 2013 발표)의 관계.

### 2.2 Coloma et al. (2023) 　검증: verified

- 서지: "The effect of ionizing radiation on robotic trajectory movement and electronic components", Nuclear Engineering and Technology, DOI 10.1016/j.net.2023.07.041. https://orbilu.uni.lu/bitstream/10993/57345/1/tHE%20EFFECT.pdf
- 파일: `coloma2023_radiation_trajectory_electronics` (PDF 없음)
- 한 줄 요약: 빔 조사로 상용 마이크로컨트롤러와 서보의 고장 선량, 납 차폐 효과를 측정했습니다.
- 프로젝트와의 관계: 제어 전자부 `C0x` 행의 상한 후보이고 국소 납 차폐의 실측 이득 사례입니다.
- 방법: 빔 시험(선량률 0.09~0.18 Gy/s)에서 MCU와 서보를 조사하며 고장 선량과 궤적 오차를 기록했습니다.

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| ATmega328P 치명 오류 286.92 Gy (무차폐), 2 mm 납 차폐 시 1123 Gy까지 무고장 | 0.18 Gy/s | Table 1, p. 4194 |
| ATmega64M1 고장 282.15 Gy (0.09 Gy/s), 218.88 Gy (0.18 Gy/s) | | Tables 1-3, pp. 4194-4198 |
| ATmegaS64M1("내방사선" 정격 30 krad = 300 Gy) 고장 311.22 Gy, 감시 타이머 리셋 303.48 Gy | | Tables 1-3, pp. 4194-4198 |
| 서보 위치 편차와 궤적 진동이 선량에 따라 증가(관절 3이 최악), 한 번의 시험에서 FLASH 11,160 바이트 손상 | | Tables 1-3, pp. 4194-4198 |
| 납 2 mm의 보호 계수 약 3.9 (1123 / 286.92) | 원자료 노트의 계산. 해당 형상과 빔 에너지 한정 | Table 1, p. 4194 기반 계산 |
| 저자들이 납 차폐를 "more effective and economical"하다고 평가 | 내방사선 부품만 쓰는 방식과 비교 | p. 4201 |

- 차폐된 서보는 궤적 오차가 더 낮았다고 서술됩니다(위치 미상).
- 우리와 다른 점: 빔 시험의 높은 선량률입니다. 선량률 효과(ELDRS, 어닐링)가 있어 설계 한계가 아닌 자릿수 기준점으로만 씁니다. 보호 계수 약 3.9는 Co-60이나 다른 감마 스펙트럼으로 옮기려면 수송 계산이 필요합니다. 빔 에너지는 읽은 범위에서 확인되지 않았습니다.
- 2026-10-11 보강(프로젝트 자체 계산, `component_tid_gaps.md` Q8, 보고서 5절): 1.25 MeV에서 납 2 mm의 협빔 투과율은 0.875라서 Co-60 같은 광자라면 수명 연장은 약 1.14배에 그칩니다(2.31). 따라서 약 3.9배는 더 부드러운 스펙트럼이나 다른 형상에서 나온 값이고 Co-60이나 Cs-137 장에 적용하면 안 됩니다. 서현의 TID_lim 표(팀원 입력)가 쓰는 "납 2 mm 차폐 일반 MCU 1123 Gy 초과"도 같은 단서를 달아야 합니다.
- 서지 보충: 권과 쪽은 서현 입력(2026-10-06)이 Nucl. Eng. Technol. 55, 4191-4203으로 적었고, 이 노트의 쪽 표기(pp.4194~4201)와 범위가 맞습니다. 조사에서 직접 확인한 값은 아닙니다.
- 확인 못 한 것: 빔 에너지. 표별(Table 1, 2, 3) 값의 정확한 대응은 원자료에 쪽 범위로만 적혀 있습니다. 권과 쪽의 직접 확인.

### 2.3 Macha, Senajova, Giles, Calviani, Girard, Ferrari (2025) 　검증: verified

- 서지: "Effects of Radiation Dose on Lubricants: A Review of Experimental Studies", ACS Applied Materials & Interfaces, DOI 10.1021/acsami.4c21220. https://pmc.ncbi.nlm.nih.gov/articles/PMC11912217
- 파일: `macha2025_lubricant_dose_review` (PDF 없음)
- 한 줄 요약: 윤활제의 방사선 내성 실험 연구를 모은 리뷰입니다.
- 프로젝트와의 관계: 윤활제가 Gy 영역에서는 제약이 아니라는 근거입니다.
- 방법: 문헌 리뷰. 구간은 그림에 정리되어 있습니다.

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| 그리스: 불소계 0.2~2.0 MGy(연화, 오일 분리), 광유계 0.1~>10 MGy(연화 또는 경화), PPE 1~100 MGy | | Figs. 4, 6, 8 (그림별 대응 미상) |
| 오일: 불소계 2~50 kGy(산도 상승, 부식성 생성물), 에스터 30 kGy~1 MGy, 광유 30 kGy~30 MGy, 실리콘 0.05~15 MGy(겔화), PPE 1~100 MGy | | Figs. 4, 6, 8 (그림별 대응 미상) |
| 건식 윤활제: PTFE <150 kGy(사슬 절단, 마찰 증가), MoS2 <1 MGy, 흑연 1~5 MGy | | Figs. 4, 6, 8 (그림별 대응 미상) |

- 우리와 다른 점: 리뷰이고 부품 수준이 아닙니다. 하모닉 드라이브 본체의 Gy 값은 아닙니다.
- 확인 못 한 것: 그림 번호와 윤활제 종류의 정확한 대응.

### 2.4 Goiffon et al. (2018) 　검증: verified (초록만)

- 서지: IEEE Transactions on Nuclear Science, DOI 10.1109/TNS.2017.2765481. https://researchportal.sckcen.be/en/publications/total-ionizing-dose-effects-on-a-radiation-hardened-cmos-image-se/ (HAL 사본은 열리지 않았습니다.)
- 파일: `goiffon2018_rad_hard_cmos_sensor` (PDF 없음)
- 한 줄 요약: ITER 원격조작용 내방사선 CMOS 이미지 센서 시제품의 TID 시험입니다.
- 프로젝트와의 관계: 카메라 센서의 상한 후보입니다.
- 방법: 10 MGy, 최대 1 Grad(SiO2)까지 조사했습니다.

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| 10 MGy, 최대 1 Grad(SiO2)까지 감도와 판독 잡음에 유의한 열화 없음. 주 열화는 암전류 증가이며 화소 배치와 암전류 배출로 완화 | 내방사선 설계 시제품 | 초록 |

- 우리와 다른 점: 내방사선 설계 시제품이라 상용 카메라(COTS)와 다릅니다.
- 확인 못 한 것: 초록 수준만 읽었고 표나 쪽 위치가 없습니다.

### 2.5 Mirion SC985 데이터시트 　검증: verified (벤더 자료, 날짜 미확인)

- 서지: Mirion IST-Rees SC985 compact colour shielded camera module spec sheet. https://assets-mirion.mirion.com/prod-20220822/cms4_mirion/files/pdf/spec-sheets/sc985-compact-color-shielded-camera-module.pdf
- 파일: `mirion_sc985_camera_datasheet` (PDF 없음)
- 한 줄 요약: 차폐 카메라 모듈의 사양서입니다.
- 프로젝트와의 관계: 카메라 `C0x` 행의 상한 후보이고 선량 한계 부품(센서)을 교체하는 설계의 선례입니다.
- 방법: 벤더 사양 서술.

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| 센서 10 kGy (1 Mrad), 최대 선량률 1 kGy/h | 벤더 사양 | pp. 1-2 |
| 센서 외 나머지 부품 1 MGy까지 | 벤더 사양 | pp. 1-2 |
| 텅스텐 차폐 사용(두께는 명시 없음), 센서 교체 용이 | 낮은 소유 비용이 설계 의도 | p. 1 |

- 우리와 다른 점: 벤더 주장입니다.
- 확인 못 한 것: 데이터시트 날짜, 차폐 두께.

### 2.6 Todd, Uznanski (arXiv:1607.01573) 　검증: verified (제목, 저자). 연도 미확인

- 서지: "Radiation Risks and Mitigation in Electronic Systems" (CERN). https://arxiv.org/pdf/1607.01573 . 연도는 arXiv 번호로 2016이라고 추정할 뿐 페이지에서 확인되지 않았습니다.
- 파일: `todd_cern_radiation_risks` (PDF 없음)
- 한 줄 요약: CERN 전자 시스템의 방사선 위험과 완화 방법입니다.
- 프로젝트와의 관계: 수명 선량 하나를 요구 사양으로 두는 방식의 비교 사례입니다.
- 방법: FGClite 전원 변환기 제어기의 모든 부품이 수명 선량 이후에도 사양을 유지해야 하며 유형 시험과 배치 시험으로 보증합니다.

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| 약 200 Gy 이후에도 사양 유지, 수명 25년 초과 | FGClite 제어기의 모든 부품 | 4.7절, p. 16 |
| 유형 시험과 배치 시험으로 보증(교체 일정 방식이 아님) | | 2.2절, pp. 5-8 |

- 우리와 다른 점: 수명 요구이고 교환 횟수 분할이 아닙니다.
- 확인 못 한 것: 연도.

### 2.7 Nancekievill (2017) 　검증: verified (초록만)

- 서지: "The Radiation Tolerance and Development of Robotic Platforms for Nuclear Decommissioning", 박사논문, University of Manchester. https://research.manchester.ac.uk/en/studentTheses/the-radiation-tolerance-and-development-of-robotic-platforms-for-/
- 파일: `nancekievill2017_robot_tolerance_thesis` (PDF 없음)
- 한 줄 요약: 해체용 로봇 플랫폼의 방사선 내성 평가와 개발입니다.
- 프로젝트와의 관계: 예상 연간 선량을 기준으로 평가하는 접근의 선례입니다.
- 방법: 상용 부품을 예상 연간 선량 기준으로 평가했습니다.

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| 예상 연간 선량 5 kGy(Si)를 기준으로 평가. 전압 레귤레이터와 IMU가 TID에 취약 | | 초록 |

- 우리와 다른 점: 연간 선량 기준이고 교환 횟수 분할이 아닙니다.
- 확인 못 한 것: 부품별 Gy 값은 읽지 못했습니다.

### 2.8 Nagatani et al. (West 2022가 인용한 값) 　검증: partial (2차 인용)

- 서지: Nagatani, Kiribayashi, Okada et al., "Emergency response to the nuclear accident at the Fukushima Daiichi Nuclear Power Plants using mobile rescue robots", J. Field Robotics, DOI 10.1002/rob.21439. https://synapsesocial.com/papers/W1950970151 . 연도는 목록에 2012, West 2022의 인용에 2011로 달라 확정하지 못했습니다.
- 파일: `nagatani2012_fukushima_rescue_robots` (PDF 없음)
- 한 줄 요약: 후쿠시마 정찰 로봇의 사고 대응 보고입니다.
- 프로젝트와의 관계: 카메라와 라이다의 보수적 기준 선량을 West 2022가 이 논문을 인용해 적었습니다.
- 방법: 해당 없음(원문 미열람).
- 쓸 수 있는 수치: 없음. 감마선 후 카메라와 라이다 고장 가능성의 기준 선량이 West 2022에 2차 인용되어 있으나 West 2022 안의 위치를 댈 수 없고 원문도 읽지 못해 싣지 않았습니다.
- 우리와 다른 점: 2차 값이며 연도가 문헌마다 다릅니다.
- 2026-10-11 보강(`component_tid_gaps.md` Q4): Zhang 2020은 Quince 방사선 시험을 J. Field Robotics 논문이 아니라 "Nagatani et al. (2011)"로 인용하고 선량 값은 적지 않습니다. 같은 Quince의 1차 그룹 자료인 Kawatsuma와 Asama(2.14)는 카메라 고장 선량을 West 2022가 Nagatani 2011을 인용해 적은 값과 다르게 적습니다(두 값 모두 위치가 없어 싣지 않음). 원자료 노트는 1차 그룹 쪽이 더 잘 뒷받침된다고 봅니다(`00_확인필요_목록.md` (e)). J. Field Robotics 논문의 연도(온라인 2012 대 권호 2013), 권, 쪽은 이번에도 확인하지 못했습니다.
- 확인 못 한 것: 원문 전체. 초록에서도 선량 자료는 읽지 못했습니다.

### 2.9 NEI Magazine (2020), Resolve Optics 　검증: verified (업계지, 벤더 주장)

- 서지: NEI Magazine, 2020-07-24. https://www.neimagazine.com/news/resolve-optics-supports-visual-inpection-in-nuclear-environments-8042527/
- 파일: `neimag2020_resolve_optics` (PDF 없음)
- 한 줄 요약: 방사선 환경용 렌즈 업체의 소개 기사입니다.
- 프로젝트와의 관계: 렌즈 유리 갈변이 카메라 성능을 제한한다는 정성 근거입니다.
- 방법: 해당 없음(제품 소개).

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| 세륨 도핑 유리나 합성 실리카는 100,000,000 rad (1 MGy)까지 변색 없음 | 벤더 주장 | 웹 기사 본문(단일 페이지, 쪽 구분 없음) |

- 우리와 다른 점: 벤더 주장입니다. 일반 유리의 갈변 시작 선량은 없습니다.
- 확인 못 한 것: 일반(비 Ce) 유리의 갈변 시작 선량.

### 2.10 Li, Qiu, Zheng, Cao (2015) 　검증: verified (초록만)

- 서지: "Testing of harmonic drive degrading under radiation environment", Int. J. Mechatronics and Automation 5(2/3). https://www.inderscience.com/offer.php?id=75944
- 파일: `li2015_harmonic_drive_irradiation` (PDF 없음)
- 한 줄 요약: 하모닉 드라이브의 방사선 열화 시험입니다.
- 프로젝트와의 관계: 하모닉 드라이브 내성의 약한 근거입니다.
- 방법: X선 노출 전후 시험. 초록은 짧은 시간 작동에서는 조사 환경에 내성이 있다고 서술합니다.
- 쓸 수 있는 수치: 없음(초록에 선량 수치 없음).
- 우리와 다른 점: 단시간 X선 시험입니다.
- 확인 못 한 것: 선량, 본문 전체.

### 2.11 Kurbanova et al. (2023) 　검증: verified

- 서지: Polymers, DOI 10.3390/polym15061340. https://pmc.ncbi.nlm.nih.gov/articles/PMC10051403/
- 파일: `kurbanova2023_peek_ebeam` (PDF 없음)
- 한 줄 요약: 전자빔을 쬔 PEEK의 마찰과 마모 연구입니다.
- 프로젝트와의 관계: PEEK가 Gy 영역 선량보다 훨씬 위에서 안정하다는 참고입니다.
- 방법: 전자빔 조사 후 트라이볼로지 시험.
- 쓸 수 있는 수치: 없음. kGy 구간별 마모 변화와 열화 온도 값이 원자료에 있으나 표나 쪽 위치가 없어 싣지 않았습니다.
- 우리와 다른 점: 트라이볼로지 연구이며 케이블 절연 한계가 아닙니다.
- 확인 못 한 것: 위치가 붙은 수치.

### 2.12 ITER Plant Design Description 2.9 (원격 보수) 　검증: verified (페이지 표기 기준)

- 서지: ITER G A0 FDR 1 R1.0, 2001-07-13(페이지 표기). https://www.fusion.qst.go.jp/ITER/FDR/PDD/PDD_2_09_RH.pdf
- 파일: `iter_pdd_2_09_remote_handling` (PDF 없음)
- 한 줄 요약: ITER 원격 보수 설계 기술서입니다.
- 프로젝트와의 관계: 수치 기준이 있는지 확인하려고 본 문서이고, 없음이 확인되었습니다.
- 방법: 해당 없음.

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| 수치 기준 없음. 내방사선성 근거는 "needs to be demonstrated by further R&D" | 수명 선량이나 교체 기준 | 2.9.5절, p. 19 |

- 우리와 다른 점: 수치 기준 없이 추가 R&D로 입증하라는 서술뿐입니다.
- 확인 못 한 것: 문서 전체(해당 절 위주로만 확인).

### 2.13 Zhang, Hutson, Knighton, Herrmann, Scott (2020) TID 관점 추가 (01 1.1과 같은 문헌) 　검증: verified (본문)

- 새 문헌이 아닙니다. 01 1.1에서 위치가 없어 싣지 못한 고장 시 누적선량과 시험 시간이 `component_tid_gaps.md`와 `heavy_robots.md`에서 표와 절 위치와 함께 확인되어 여기에 TID 관점으로 옮깁니다. 서지 보충: Frontiers in Robotics and AI 7:6, 2020-02-06 게재.

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| 관절 7 누적 164.55 ± 1.09 Gy에서 정지(동적 91.83 Gy + 정적 72.72 Gy) | Co-60, 말단 선량률 동적 9.71 Gy/h, 정적 9.68 Gy/h | Table 2 (선량률은 Table 1) |
| 같은 시점 다른 관절 누적: J6 33.55, J5 24.00, J4 20.08, J3 13.27, J2 8.30, J1 6.91 Gy | 작동 유지 | Table 2 |
| 고장 원인은 관절 7 광학 엔코더, 오류 메시지 "encoder error torque sensor", "safe axis position invalid" | 토크 센서와 엔코더 계통이 함께 고장, 스트레인 게이지는 따로 분리되지 않음 | 4.3절 |
| 동적 시험 5시간 후 관절 2 제어 오차 표준편차가 약간 증가 | | Fig. 8, 4.2절 |
| 관절 누적선량을 추적해 "at say 75% of its dose-to-failure lifetime"에 예방정비나 부품 교체 | 권고 | 5절 |
| 선택적 차폐가 적은 비용으로 수명을 크게 늘릴 수 있음, 광학 엔코더 대신 리졸버나 로터리 엔코더 권고 | | 5.1절 |

- 프로젝트 자체 계산(원자료 노트): Zhang 규칙을 그대로 쓰면 iiwa 손목의 정비 시점은 약 123 Gy(0.75 x 164.55)입니다. 논문에 이 숫자로 적힌 값은 아닙니다.
- 원자료 노트의 추론: LED와 포토다이오드 소자가 1 MGy를 견디는데(2.29) iiwa 엔코더가 약 165 Gy에서 고장 났으므로 고장 지점은 광학 소자가 아니라 신호처리 전자부(ASIC, MCU, 안전 로직)일 가능성이 높습니다. 논문은 고장 부품을 분해하지 않았습니다.
- 확인 못 한 것: 선량 매질(Gy(air) 대 Gy(water))이 읽은 부분에 적혀 있지 않습니다. 단일 개체 시험입니다. 선원 방사능, 로봇과 선원 거리, 총 노출 시간은 원자료에 값이 있으나 절이나 표 위치가 없어 01 1.1과 같이 싣지 않았습니다.

### 2.14 Kawatsuma, Asama (2016) 일본로봇학회지 　검증: verified

- 서지: 川妻, 淺間, 「市販CPU等半導体素子を使用したロボットおよび無人建設重機の耐放射線性評価と放射線環境下での管理方法」(Radiation Tolerance and Management Method of Robots and Unmanned Heavy Construction Machines using Semiconductors on the Shelf), 日本ロボット学会誌 34(8), 552-557 (2016), DOI 10.7210/jrsj.34.552. https://www.jstage.jst.go.jp/article/jrsj/34/8/34_34_552/_article , 본문 https://www.robot.t.u-tokyo.ac.jp/asamalab/publications/files/Cjj083.pdf
- 파일: `kawatsuma2016_jrsj_cots_radiation` (PDF 없음)
- 한 줄 요약: 후쿠시마 로봇과 무인 중장비의 상용 반도체 방사선 내성 평가와 선량 관리 방법입니다.
- 프로젝트와의 관계: 서현의 TID_lim 표에 쓸 1차 그룹 실측(카메라, CPU)과, `B_k` 규칙의 반쪽 근거(관리 목표를 넘기 전에 회로 교체)입니다.

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| JAEA 데이터베이스 요약: CPU와 메모리 20~100 Gy, CCD 10~100 Gy, 개별 반도체 약 1 kGy, 케이블과 오일(유기물) 약 10 kGy | 선량률 미기재 | Table 2 |
| 관리 목표: 무인 중장비 20 Gy, 일반 로봇 30 Gy, QUINCE 150~200 Gy | 적산선량계를 전자회로 근처에 붙여 관리, 목표를 넘기 전에 회로 교체 | Table 3 |

- 위치 미기재로 싣지 않은 값: QUINCE 2011-04 시험의 카메라 고장 선량과 평가값, CPU와 제어 반도체 내성, 투입 대수, 반도체 대 유기물 내성 비. 원자료 노트에 표나 쪽 위치가 없습니다. 이 가운데 카메라 고장 선량은 West 2022의 2차 인용값(2.8)과 다르며 원자료 노트는 1차 그룹인 이 문헌 쪽이 더 잘 뒷받침된다고 봅니다.
- 우리와 다른 점: 선량률이 표에 없습니다.
- 확인 못 한 것: QUINCE 값들의 쪽.

### 2.15 Cho, Jeong (2012) KNS 춘계, KAERI 카메라 온라인 조사 시험 　검증: verified

- 서지: Cho, Jeong (KAERI), "On-Line High Dose-Rate Gamma Ray Irradiation Test of the CCD/CMOS Cameras", 한국원자력학회 춘계학술발표회, 제주, 2012-05-17~18. https://kns.org/files/pre_paper/4/91조재완.pdf
- 파일: `cho2012_kns_camera_gamma` (PDF 없음)
- 한 줄 요약: 상용 CCD, CMOS 카메라를 약 150 Gy/h로 조사하며 작동을 본 시험입니다.
- 프로젝트와의 관계: 손목 카메라(C09) TID_max 후보의 국내 1차 자료입니다(서현).

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| 흑백 CCD 보드 카메라(2004)와 컬러 CCD 핀홀(2012), 컬러 CMOS 차량 블랙박스(2009)는 225 Gy 생존. 컬러 CCD "lipstick"(2006)은 모두 150 Gy 후 고장, Sony EVI-D100 PTZ(2002)는 150 Gy 후 고장. SD 메모리는 225 Gy 후에도 읽힘 | 약 150 Gy/h | Table 2 |

- 우리와 다른 점: 높은 선량률입니다. 후쿠시마 수소 폭발 후 선량률을 TEPCO 인용으로 적은 값이 있으나 위치가 없어 싣지 않았습니다.
- 확인 못 한 것: 해당 없음.

### 2.16 Sensors (2018) CMOS 이미지 센서 HD 카메라 선량률별 열화 　검증: partial (저자, 권, DOI 미확인)

- 서지: "Nuclear Radiation Degradation Study on HD Camera Based on CMOS Image Sensor at Different Dose Rates", Sensors (2018). https://doaj.org/article/15eb8fb3ea4e45e1b3544272d87d179c (PMC5855046 사본은 CAPTCHA로 막힘)
- 파일: `sensors2018_cmos_hd_camera_doserate` (PDF 없음)
- 한 줄 요약: 상용 CMOS HD 카메라의 선량률별 열화 연구입니다.
- 프로젝트와의 관계: 카메라가 "작동은 하지만 열화된" 점의 근거이고, 선량률 20 Gy/h를 넘으면 열화가 급증한다는 선량률 의존의 근거입니다.

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| 1, 10, 20, 50, 100 Gy/h로 바이어스 상태 조사, 20 Gy/h를 넘으면 열화율 급증, 10 Gy/h에서 8시간 측정 동안 작동하며 SNR 5 dB 감소 | 렌즈 외 무차폐, Co-60 | 초록 |

- 확인 못 한 것: 저자, 권, DOI, 높은 선량률에서의 누적선량.

### 2.17 Masi, Losito, Redaelli (2009) ICALEPCS, LHC 콜리메이터 제어 　검증: verified

- 서지: Masi, Losito, Redaelli, "Measured Performance of the LHC Collimators Low Level Control System", ICALEPCS2009, Kobe. https://proceedings.jacow.org/icalepcs2009/papers/wed001.pdf
- 파일: `masi2009_icalepcs_lhc_collimator` (PDF 없음)
- 한 줄 요약: LHC 콜리메이터 저수준 제어 계통의 성능 보고입니다.
- 프로젝트와의 관계: 레졸버는 변환 전자부를 원격 배치할 때만 강하다는 근거입니다(서현, 재은의 부품 배치).
- 쓸 수 있는 수치: 없음. 정성 사실: 스테핑 모터로 위치를 잡고 LVDT와 레졸버로 축을 감시하며, 콜리메이터 근처 방사선이 높아 조절과 제어 전자부를 최대 800 m 떨어진 안전 alcove에 둡니다(서론). 선량 값은 없습니다.

### 2.18 UKAEA (2024) Nucl. Eng. Technol., 내방사선 레졸버-디지털 변환 계통 　검증: partial (저자, DOI 미확인, 초록)

- 서지: "Functional Verification of Radiation Hardened Electronics for Robotics in Nuclear Environments", Nuclear Engineering and Technology (2024), UKAEA 출판 페이지(UKAEA-CCFE-PR(24)234). https://scientific-publications.ukaea.uk/?p=20141
- 파일: `ukaea2024_net_rhbd_resolver` (PDF 없음)
- 한 줄 요약: 설계 단계 내방사선(RHBD) 레졸버-디지털 변환 계통의 기능 검증입니다.
- 프로젝트와의 관계: 관절 위치 센서를 레졸버 계통으로 바꿀 때의 상한 근거입니다(서현, 유정의 로봇 개조 검토).

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| 동작 부품 정격 내성 1 MGy 초과, 각도 오차 약 0.05°, 상용 계통의 "drop-in replacement"로 제안 | | 초록 |

- 확인 못 한 것: 저자, DOI, 본문.

### 2.19 Cao et al. MAGICS 내방사선 SoC (AMICSA 2018 추정) 　검증: partial (매체와 연도가 문서에 없음)

- 서지: Cao, Geys, Boons, Michiels, Verbeeck, Van Uffelen, Mont Casells, Broodryk, Meek (MAGICS Instruments, Fusion for Energy, Veolia Nuclear Solutions), "A rad-hard system-on-chips solution for closed-loop motion control". 파일명이 AMICSA 2018을 시사합니다. https://indico.esa.int/event/222/papers/2104/files/180-MAGICS_AMICSA_2018.pdf
- 파일: `cao2018_magics_radhard_soc` (PDF 없음)
- 한 줄 요약: 레졸버와 LVDT를 읽는 폐루프 모션 제어용 내방사선 ASIC 체인입니다.
- 프로젝트와의 관계: 2.18과 같은 방향의 근거입니다.

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| 목표 TID 100 Mrad(1 MGy) 초과. ITER 요구는 감마 총선량 100 Mrad, 중성자 플루언스 10^15 n/cm2 | 레졸버 자체의 선량 정격은 없음 | 초록, I절 |

### 2.20 Tung, Wang et al. (2008) Actel, MAPLD, ProASIC3 플래시 FPGA 　검증: verified

- 서지: Tung, Wang, Rezgui, Sun, Cronquist, McCollum (Actel), "A New Radiation Tolerant Field Programmable Gate Array Based on Non-Volatile Flash Configuration Switches", MAPLD 2008. https://nepp.nasa.gov/mapld_2008/presentations/p/Wang_Jih-Jong_mapld08_pres_1.pdf
- 파일: `tung2008_mapld_proasic3_tid` (PDF 없음)
- 한 줄 요약: 플래시 기반 FPGA의 TID 시험 발표입니다.
- 프로젝트와의 관계: 제어 전자부에 FPGA가 있을 때의 TID 후보입니다(서현).

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| A3P250-PQ208 코어는 리프레시로 106 krad(SiO2), 마진, 프로그래밍 회로는 40 krad(SiO2)까지 | X선 조사, 선량률 미기재 | 발표 본문 인용문, Fig. 17~18 |

- 원자료 노트의 추론: 현장에서 FPGA를 다시 프로그래밍해야 한다면 코어가 아니라 프로그래밍 회로 한계(400 Gy(SiO2))가 적용됩니다.

### 2.21 Sanz et al. (2012) Sensors 12(4), AMR 센서 감마 조사 　검증: verified

- 서지: Sanz, Fernández, Dominguez, Martín, Michelena, "Gamma irradiation of magnetoresistive sensors for planetary exploration", Sensors 12(4), 4447-4465 (2012), DOI 10.3390/s120404447. https://digital.inta.es:8443/jspui/bitstream/20.500.12666/633/1/Gamma%20irradiation%20of%20Magnetoresistive%20sensors%20for%20planetary%20exploration.pdf
- 파일: `sanz2012_sensors_amr_gamma` (PDF 없음)
- 한 줄 요약: Honeywell AMR 자기저항 센서의 Co-60 조사 시험입니다.
- 프로젝트와의 관계: 자기식 위치 감지 소자는 수백 Gy에서 거의 열화하지 않는다는 근거입니다.
- 쓸 수 있는 수치: 없음. Co-60, 5 krad(Si)/h로 최대 200 krad(Si)(2 kGy(Si))까지 조사해 소자별 감도 변화가 수 % 미만이었고 비통전 소자가 더 열화했다는 결과가 원자료에 있으나 표나 그림 위치가 기록되지 않았습니다.
- 확인 못 한 것: 소자별 값의 표 위치.

### 2.22 Forney, Campola (2019) NASA, OMH3075 홀 센서 TID 시험 보고 　검증: verified

- 서지: Forney (SSAI), Campola (NASA GSFC), "OMH3075 Hall Effect Sensor Total Ionizing Dose Test Report", NASA, 2019, NTRS 20200001205. https://ntrs.nasa.gov/api/citations/20200001205/downloads/20200001205.pdf
- 파일: `forney2019_nasa_omh3075_tid` (PDF 없음)
- 한 줄 요약: 홀 효과 센서의 TID 시험 보고서입니다.

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| 0, 1, 10, 20, 30, 40 krad(Si) 단계, 바이어스 5개와 무바이어스 5개 | MIL-STD-883 Method 1019, 0.6 krad(Si)/min | Table 2 |
| 40 krad(Si)(400 Gy(Si))까지 기능 오류, 열화, 큰 매개변수 변동 없음 | | 8절 |

### 2.23 LAPP T28 기술표: 방사선 내성 　검증: verified (벤더 문서, 연도와 쪽 미확인)

- 서지: LAPP, "T28 Technical Tables: Radiation resistance". https://contentmedia.lappcdn.com/e/lapp/BGy89cyYqvWz6YBbp4RG_g~~
- 파일: `lapp_t28_radiation_resistance` (PDF 없음)
- 한 줄 요약: 케이블 절연 재질별 감마 내성 표입니다.
- 프로젝트와의 관계: 로봇 케이블 행의 TID_max 근거입니다. PTFE나 FEP를 쓰는지가 결정적입니다(서현, 유정).

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| 파단신율이 미노화 대비 50% 이상 유지되는 최대 선량: PVC 8x10^5, PE-LD 1x10^5, XLPE 1x10^5, PUR 5x10^5, TPE-E 1x10^5, TPE-O 1x10^5, 실리콘 2x10^5, EPR 1x10^6, ETFE 1x10^5, FEP 3x10^3, PTFE 1x10^3 Gy | 폴리이미드와 PEEK는 없음 | T28 표 |

- 우리와 다른 점: 벤더의 대표값이며 선량률이 명시되지 않았습니다(높을 가능성). 산소가 있는 저선량률 장기 노출에서는 더 낮은 선량에서 열화할 수 있다는 것은 알려진 단서이나 출처로 확인하지 않았습니다.

### 2.24 Camuna Cavi 카탈로그 T28 (CERN CMS RPC 프로젝트 게시) 　검증: verified (벤더 문서, 연도 미기재)

- 서지: Camuna Cavi catalogue, technical table T28, pp.144-145 (파일명은 01.17을 시사). https://project-cms-rpc-endcap.web.cern.ch/RPC/ChambersandIntegration/Integration/RadiationExposure/Camuna%20Cavi%20Catalogue%2001.17.pdf
- 파일: `camunacavi_t28_catalogue` (PDF 없음)
- 한 줄 요약: 2.23과 같은 기준과 값을 IEC 60544-4 인용으로 제시하는 케이블 카탈로그입니다.

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| PVC, PE-LD, XLPE, PUR, EPR, PTFE, FEP, ETFE 값이 2.23과 같음, 기준 규격 IEC 60544-4 | 파단신율 50% 기준 | pp.144-145 |

### 2.25 Ferrari et al. (2023) IEEE TNS, "Radiation to Materials" at CERN 　검증: verified

- 서지: Ferrari, García Alía, Giles, Senajova, Pandini, Zenoni, Calviani, "'Radiation to Materials' at CERN", IEEE Trans. Nucl. Sci. (2023), DOI 10.1109/TNS.2023.3241785. https://iris.unibs.it/retrieve/f88a118a-211c-4b43-8a0a-ed79a5d60a60/Radiation_to_Materials_at_CERN.pdf
- 파일: `ferrari2023_tns_radiation_to_materials` (PDF 없음)
- 한 줄 요약: CERN의 재료 방사선 손상 연구 개관입니다.
- 프로젝트와의 관계: 고분자 일반 임계와 O-링 열화의 근거입니다.
- 쓸 수 있는 수치: 없음. 0.1 MGy가 다수 고분자의 유의 임계이고 1 MGy를 넘으면 위험하다는 서술, EPDM O-링이 2 MGy에서 심하게 열화했다는 결과, CERN 79-04, 79-08, 82-10 보고서 인용이 원자료에 있으나 쪽이나 절 위치가 없습니다.

### 2.26 CERN PS-IRRAD 방사선 손상 보고서 목록 　검증: verified (보고서 번호와 짧은 제목만)

- 서지: CERN PS-IRRAD, list of CERN radiation damage reports. https://ps-irrad.web.cern.ch/ps-irrad/assets/doc/extra/CERN_Radiation_Damage_Reports.pdf . LBL 미러 디렉터리(https://www-eng.lbl.gov/~ecanderssen/Radiation_Data)에 79-04, 89-12, 98-01 파일이 있으나 스캔이라 텍스트를 뽑지 못했습니다.
- 파일: `cern_psirrad_damage_reports_list` (PDF 없음)
- 한 줄 요약: CERN 재료 방사선 손상 보고서 시리즈 목록입니다(79-04와 89-12 케이블 절연, 79-08과 98-01 수지, 82-10 기타, 85-02 고전압 수지, 2001-006 접착제, 75-03, 83-08).
- 프로젝트와의 관계: 케이블 절연 재질별 한계의 1차 출처 후보입니다.
- 쓸 수 있는 수치: 없음(저자, 연도, 재질별 값 없음).

### 2.27 Goussarov, Doyle, Glebov, Berghmans (2007) Optical Engineering 46 　검증: verified (초록만)

- 서지: Goussarov, Doyle, Glebov, Berghmans, "Radiation-induced transmission degradation of borosilicate crown optical glass from four different manufacturers", Optical Engineering 46 (2007), DOI 10.1117/1.2722322. https://researchportal.sckcen.be/en/publications/radiation-induced-transmission-degradation-of-borosilicate-crown-/
- 파일: `goussarov2007_bk7_radiation` (PDF 없음)
- 한 줄 요약: 제조사가 다른 BK7 계열 광학유리의 방사선 투과 열화 비교입니다.
- 쓸 수 있는 수치: 없음. 조사 전에는 광학적으로 같은 유리들이 조사 중과 후에 다르게 거동한다는 서술(초록)만 있습니다.

### 2.28 Ioan (2016) Romanian Journal of Physics 61(5-6) 　검증: verified (DOI 미표시)

- 서지: Ioan, "Study of the Optical Materials Degradation Caused by Gamma Radiation and the Recovery Process by Controlled Heat Treatment", Romanian Journal of Physics 61(5-6) (2016). https://s3.cern.ch/inspire-prod-files-7/706b88fb49e286455832318ef68f242c
- 파일: `ioan2016_rjp_optical_gamma` (PDF 없음)
- 한 줄 요약: BK7과 TEMPAX 유리의 감마 조사 열화와 열처리 회복 연구입니다.
- 프로젝트와의 관계: 일반 유리 렌즈의 갈변 시작 선량이 4.9 kGy보다 낮다는 근거입니다(02 2.9의 "일반 유리 갈변 시작 선량" 공백을 일부 채움).

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| BK7 레이저 투과 상대 변화 633 nm에서 61.26%, 532 nm에서 97.01%(297.15 K) | 1.25 MeV 감마, 100 Gy/h, 선량 4.9, 14.6, 24.4 kGy | Table 1 |

- 원자료 노트의 추론: 렌즈 갈변은 kGy 이상이라 100~200 Gy대의 카메라 전자부 고장보다 늦게 옵니다.

### 2.29 Takeuchi et al. (2018) JAEA-Technology 2017-026 　검증: verified

- 서지: Takeuchi, Shibata, Hanakawa, Uehara, Ueno, Tsuchiya, Kumahara, Shibagaki, Komanome, 「光学部品のガンマ線照射劣化挙動(受託研究)」(Degradation Behavior of Optical Components by Gamma Irradiation), JAEA-Technology 2017-026 (2018 발행). https://jopss.jaea.go.jp/pdfdata/JAEA-Technology-2017-026.pdf
- 파일: `takeuchi2018_jaea_optical_gamma` (PDF 없음)
- 한 줄 요약: 광학 부품(LED, 포토다이오드, 유리)의 감마 조사 열화 시험 보고서입니다.
- 프로젝트와의 관계: 광학 엔코더의 발광, 수광 소자 자체는 1 MGy를 견딘다는 근거입니다(2.13의 추론).

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| LED 광속 손실과 포토다이오드 감도 손실은 반도체가 아니라 렌즈와 창의 갈변 때문, 포토다이오드 암전류는 1000 kGy에서 10 nA 미만 | 10 kGy/h로 1 MGy까지 | Figs. 4-10~4-21 |
| 용융 실리카는 10 kGy에서 약간 보라색으로 착색, 700 nm 이하 투과 약 20% 감소 | 20 °C | Fig. 4-23 |
| 사파이어와 합성 석영은 1000 kGy까지 유의한 손실 없음 | | Figs. 4-24, 4-25 |

### 2.30 NIST 질량감쇠계수 표 (05 5.10과 같은 자료) 　검증: verified

- 새 문헌이 아닙니다. 05 5.10 Hubbell과 Seltzer(NISTIR 5632)의 웹 표에서 납과 텅스텐 값을 읽었습니다. https://physics.nist.gov/PhysRefData/XrayMassCoef/ElemTab/z82.html , https://physics.nist.gov/PhysRefData/XrayMassCoef/ElemTab/z74.html

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| 납 μ/ρ(cm2/g): 0.5 MeV 0.1614, 0.6 MeV 0.1248, 0.8 MeV 0.0887, 1.0 MeV 0.07102, 1.25 MeV 0.05876, 1.5 MeV 0.05222. μ_en/ρ: 0.09128, 0.06819, 0.04644, 0.03654, 0.02988, 0.02640 | Z = 82 | Table 3 |
| 텅스텐 μ/ρ(cm2/g): 0.5 MeV 0.1378, 0.6 MeV 0.1093, 0.8 MeV 0.08066, 1.0 MeV 0.06618, 1.25 MeV 0.05577, 1.5 MeV 0.05000. μ_en/ρ: 0.07440, 0.05673, 0.04028, 0.03276, 0.02761, 0.02484 | Z = 74 | Table 3 |

### 2.31 반가층과 투과율 (프로젝트 자체 계산, 입력은 2.30)

원자료 노트가 HVL = ln2 / (μ/ρ x ρ)로 계산했고 밀도는 핸드북 값(납 11.35 g/cm3, 텅스텐 19.3 g/cm3)을 가정했습니다(NIST 밀도표는 열지 않음). 협빔(좋은 기하) 값이고 빌드업을 넣지 않았으므로 실제 팔 안에서의 보호 효과는 이보다 작습니다. 서현의 NIST XCOM 차폐재 비교와 대조할 출발값입니다.

| 에너지 | 납 HVL | 텅스텐 HVL | 비고 |
|---|---|---|---|
| 0.5 MeV | 3.78 mm | 2.61 mm | |
| 0.6 MeV | 4.89 mm | 3.29 mm | |
| 0.662 MeV(Cs-137, 로그 보간) | 5.50 mm | 3.65 mm | |
| 0.8 MeV | 6.89 mm | 4.45 mm | |
| 1.0 MeV | 8.60 mm | 5.43 mm | |
| 1.25 MeV(Co-60 평균) | 10.39 mm | 6.44 mm | TVL 납 34.5 mm, 텅스텐 21.4 mm |
| 1.5 MeV | 11.69 mm | 7.18 mm | |

- 1.25 MeV 협빔 투과율: 납 2 mm 0.875, 5 mm 0.716, 10 mm 0.513, 텅스텐 2 mm 0.806, 10 mm 0.341. 0.662 MeV: 납 2 mm 0.777, 텅스텐 2 mm 0.684.
- 함의(보고서 5절): 1 MeV 이상 선원(Cs-138, 그리고 참고만(Kr)인 Rb-88)이 남는 경우 손목 전자부 국부 차폐는 cm 단위가 필요합니다. Xe-133(81 keV) 위주로 냉각된 베드라면 얇은 차폐가 통합니다. 81 keV의 감쇠계수는 이 표 범위 밖이라 XCOM으로 따로 구해야 합니다.

### 2.32 Tommasini, arXiv:1104.0802 (CERN) 　검증: verified (옮길 수 있는 선량 값 없음)

- 서지: Tommasini, "Dielectric insulation and high-voltage issues" (CERN), arXiv:1104.0802. https://arxiv.org/pdf/1104.0802
- 파일: `tommasini2011_dielectric_insulation` (PDF 없음)
- 한 줄 요약: 절연과 고전압 문제 강의록이며 선량 값은 CERN 보고서를 가리킵니다.
- 쓸 수 있는 수치: 없음.

## 갈래 전체에서 확인 못 한 것

- (2026-10-06 기준) 레졸버와 인코더, 브러시리스 모터 드라이브, FPGA, KUKA iiwa 급 관절 전자부, 하모닉 드라이브 본체에 대한 Gy 단위 값은 읽지 못했습니다.
- (2026-10-11 갱신) 위 중 인코더 모듈(2.13), 홀과 AMR 소자(2.21, 2.22), 내방사선 레졸버 변환 체인(2.18, 2.19), 플래시 FPGA(2.20)는 값이 생겼습니다. 여전히 없는 것: 상용 브러시리스 모터 레졸버 자체의 고장 선량, 상용 전력 MOSFET과 IGBT, 통합 모터 드라이버, Microsemi RTG4와 Xilinx, Intel FPGA(CERN RADWG, R2E, CHARM, ESA ESCIES 보고서는 검색에만 나옴), 하모닉 드라이브 본체(Li 2015 본문 미열람), 토크 센서, 포일 스트레인 게이지, 브리지 증폭기, 폴리이미드와 PEEK 케이블 절연의 50% 파단신율 선량, 선량률 효과 자료, UR, Kinova, Franka 등 다른 상용 팔의 감마 고장 선량.
- 팀원 입력(서현, 2026-10-06)의 TID_lim 표가 인용한 West et al. (2022) "Radiation tolerance of a small COTS single board computer for mobile robots", Nucl. Eng. Technol. 54(6), 2198-2203은 이 조사에서 읽지 못했습니다(검색에만 나옴). 표의 싱글보드 컴퓨터 값은 미검증입니다(`00_확인필요_목록.md`).
- IAEA-TECDOC, IEC 60544, NASA/JPL 핸드북의 폴리이미드와 PEEK 절연 한계는 확보하지 못했습니다. 검색에서 열람 가능한 사본이 나오지 않았습니다.
- 납이나 텅스텐의 투과율 표, 반가층(Co-60, Cs-137)을 담은 핸드북은 찾지 못했습니다. NIST XCOM이나 몬테카를로로 직접 계산하는 편이 낫습니다.
- 원자료 노트의 해석: 카메라 `C0x` 행에는 Gy 영역의 기준(상용, 2차 인용)과 10 kGy(Mirion 센서)를 상하 경계로 둘 수 있으나, 후자는 벤더 주장입니다. 이는 임시 앵커이며 설계 한계가 아닙니다.
- 반도체를 담은 말단 부품이 먼저 한계에 닿는다는 정성적 근거로 `01_선량인지_경로계획.md` 1.1의 Zhang 2020이 있습니다(고장 부품이 관절 7의 광학 인코더). 위치 있는 수치는 1.1에만 있습니다.

## 예산 분할 선례 (`B_k = TID_max / N_ex`)

- **선례 없음.** 수명 TID 한계를 교환 횟수나 임무 횟수로 나눈 문헌은 찾지 못했습니다(2026-10-11 보강 후에도 같음).
- 가장 가까운 것: CERN FGClite의 단일 수명 선량 요구(2.6), Mirion의 교체형 센서(2.5), Nancekievill의 연간 5 kGy(Si) 기준(2.7). ITER PDD 2.9는 수치 기준이 없습니다(2.12).
- 2026-10-11 보강으로 반쪽짜리 근거가 둘 생겼습니다. Zhang 2020은 관절 누적선량을 추적해 고장 선량의 약 75%에서 예방정비나 교체를 하라고 권하고(2.13, 5절), Kawatsuma와 Asama는 전자회로 근처에 적산선량계를 붙여 관리 목표를 넘기 전에 회로를 교체한 후쿠시마 관행을 적습니다(2.14, Table 3). 두 관행을 함께 인용하면 `B_k` 규칙에 방어 가능한 바탕이 생기지만, 작업 횟수로 나누는 부분은 여전히 프로젝트 고유의 배분 규칙으로 적어야 합니다(보고서 5절).
- 원자료 노트의 판단: 이 규칙은 단순 분할이므로 저자의 설계 선택으로 제시하고, 참고문헌 목록에는 "선례 없음"이라고 적는 것이 적절합니다. 부정 결과는 완전하지 않습니다. IAEA-TECDOC, IEC 60544, NASA/JPL, ORNL, KNS와 KAERI 문서는 읽지 못했습니다.
- 관련 프로젝트 문서 위치는 `00_확인필요_목록.md` (c)에 적었습니다.
