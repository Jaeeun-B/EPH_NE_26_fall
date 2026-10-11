# 02 부품 TID 내성과 예산 (갈래 노트)

- 갈래: 선량 모델(TID, 부품 내성)
- 근거: 연구 원자료 노트 `component_tid.md`와 보고서 "방사선 환경 로봇 경로계획 참고문헌" (둘 다 저장소 밖). 논문 원문과 직접 대조하지 않았습니다.
- 조사일: 2026-10-06 (원자료 노트 기준)
- 파일: 모든 문헌이 PDF 없음. 파일명은 `refs/README.md` 표의 임시 이름입니다.
- 위치 표기: 쪽 번호가 없는 웹 자료는 표, 그림, 절 번호 또는 "초록"으로 적었습니다. 위치를 댈 수 없는 수치는 싣지 않고 소절의 "확인 못 한 것"에 항목 이름만 적었습니다.

## 갈래 요약

기계 부품(모터 권선 절연, 윤활제, O-링, 커넥터)의 시험 자료는 MGy 급으로, 이 프로젝트가 다루는 Gy 영역 선량보다 몇 자릿수 위에 있어 사실상 제약이 되지 않습니다. 실제로 예산을 좌우하는 것은 반도체가 들어간 부품(제어 전자부, 인코더 전자부, 카메라 센서, MCU)입니다. 상용 마이크로컨트롤러는 몇백 Gy에서 고장납니다. 다만 그 값은 0.09~0.18 Gy/s 라는 선박 환경보다 훨씬 높은 선량률의 빔 시험에서 얻은 것이라 설계 한계가 아니라 자릿수 기준점으로만 쓸 수 있습니다.

## 프로젝트와의 관계

- 부품별 `TID_max`(`config/components.json` 계열, 소재 파트의 `component_inputs.xlsx`)를 채울 때 상한 후보와 자릿수 기준을 제공하는 갈래입니다. 단 아래 공백 때문에 표의 많은 값은 이 갈래에서 공급되지 않습니다.
- `B_k = TID_max / N_ex` 분할 규칙의 선례는 찾지 못했습니다(아래 "예산 분할 선례").
- 차폐 투과율 `S_k`는 이 갈래에 표가 없습니다. 원자료 노트는 인용 대신 NIST XCOM이나 몬테카를로로 직접 계산하라고 권합니다.

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

- 우리와 다른 점: MGy 급이라 Gy 영역과 거리가 큽니다. 대응 방식은 시험 후 재료 교체(폴리이미드)이고 교체 일정 계산이 아닙니다.
- 확인 못 한 것: 보고서 번호 확인.

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
- 확인 못 한 것: 빔 에너지. 표별(Table 1, 2, 3) 값의 정확한 대응은 원자료에 쪽 범위로만 적혀 있습니다.

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

## 갈래 전체에서 확인 못 한 것

- 레졸버와 인코더, 브러시리스 모터 드라이브, FPGA, KUKA iiwa 급 관절 전자부, 하모닉 드라이브 본체에 대한 Gy 단위 값은 읽지 못했습니다.
- IAEA-TECDOC, IEC 60544, NASA/JPL 핸드북의 폴리이미드와 PEEK 절연 한계는 확보하지 못했습니다. 검색에서 열람 가능한 사본이 나오지 않았습니다.
- 납이나 텅스텐의 투과율 표, 반가층(Co-60, Cs-137)을 담은 핸드북은 찾지 못했습니다. NIST XCOM이나 몬테카를로로 직접 계산하는 편이 낫습니다.
- 원자료 노트의 해석: 카메라 `C0x` 행에는 Gy 영역의 기준(상용, 2차 인용)과 10 kGy(Mirion 센서)를 상하 경계로 둘 수 있으나, 후자는 벤더 주장입니다. 이는 임시 앵커이며 설계 한계가 아닙니다.
- 반도체를 담은 말단 부품이 먼저 한계에 닿는다는 정성적 근거로 `01_선량인지_경로계획.md` 1.1의 Zhang 2020이 있습니다(고장 부품이 관절 7의 광학 인코더). 위치 있는 수치는 1.1에만 있습니다.

## 예산 분할 선례 (`B_k = TID_max / N_ex`)

- **선례 없음.** 수명 TID 한계를 교환 횟수나 임무 횟수로 나눈 문헌은 찾지 못했습니다.
- 가장 가까운 것: CERN FGClite의 단일 수명 선량 요구(2.6), Mirion의 교체형 센서(2.5), Nancekievill의 연간 5 kGy(Si) 기준(2.7). ITER PDD 2.9는 수치 기준이 없습니다(2.12).
- 원자료 노트의 판단: 이 규칙은 단순 분할이므로 저자의 설계 선택으로 제시하고, 참고문헌 목록에는 "선례 없음"이라고 적는 것이 적절합니다. 부정 결과는 완전하지 않습니다. IAEA-TECDOC, IEC 60544, NASA/JPL, ORNL, KNS와 KAERI 문서는 읽지 못했습니다.
- 관련 프로젝트 문서 위치는 `00_확인필요_목록.md` (c)에 적었습니다.
