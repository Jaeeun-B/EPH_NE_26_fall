# 05 MSR 오프가스, 흡착 베드, 선량 계산 (갈래 노트)

- 갈래: 선량 모델(선원항, 베드 형상과 질량, 점커널 검증), 원자력 원격조작(베드 크기 선례)
- 근거: 연구 원자료 노트 `msr_offgas.md`와 보고서 "방사선 환경 로봇 경로계획 참고문헌" (둘 다 저장소 밖). 논문과 보고서 원문과 직접 대조하지 않았습니다.
- 조사일: 2026-10-06 (원자료 노트 기준)
- 파일: 모든 문헌이 PDF 없음. 파일명은 `refs/README.md` 표의 임시 이름입니다.
- 위치 표기: ORNL 보고서의 쪽은 원자료 노트가 읽을 수 있었던 **인쇄 쪽 번호**입니다(1960년대 스캔의 OCR 잡음이 큼). 인쇄 쪽 종류가 불분명한 곳은 그렇게 적었습니다. 단위는 원문대로(lb, ft, ft3, in., Ci, r/hr, mr/hr, F)이고, 원자료나 보고서가 환산해 둔 값만 괄호로 병기했습니다. 위치를 댈 수 없는 수치는 싣지 않았습니다.
- ORNL 보고서는 모두 openmsr/msr-archive 저장소의 사본(ORNL 원본의 복사본)에서 읽었고 OSTI 기록과는 대조하지 않았습니다.

## 갈래 요약

- MSRE 주 흡착 베드는 약 60 kg이 아닙니다. 병렬 2기의 베드가 각각 숯 약 1,455 lb(약 660 kg)를 담고(TM-728 §12.4.1, 인쇄 p.375), 어느 문서에서도 60 kg이라는 값은 나오지 않았습니다. 이 불일치는 `00_확인필요_목록.md` (b)에 정리했습니다.
- 로봇이 다룰 만한 크기의 MSRE 관련 베드는 라인 524의 15.8 lb(약 7.2 kg) 베드와 1,092 g 유기 증기 트랩 둘뿐입니다(ORNL-4037). 주 베드를 카트리지식으로 교체한 기록은 없습니다.
- 읽은 선원항은 스트림 수준이고 **베드 표면이나 거리별 선량률(Gy/h)은 읽지 못했습니다.** 따라서 프로젝트의 절대 선량은 검증된 값이 아니라 모델 값입니다.

## 프로젝트와의 관계

- 선량 모델 갈래: 선원항(Kr-85만인지, 단수명 핵종과 제동복사를 넣는지)이 10/5 회의 안건이었습니다(`handoff/01_radiation/README.md`, `docs/2026-10-06_진행공유.md`). 이 갈래는 그 선택이 자릿수로 차이 난다는 근거를 줍니다.
- 선량장 메타데이터에 베드의 붕괴 시간(마지막 가동 후 경과)을 반드시 적어야 합니다. 현재 `handoff/01_radiation/dose_grid_meta_template.json`의 해당 필드 유무는 `00_확인필요_목록.md` (b)에서 점검 항목으로 적었습니다.
- 가반하중 비교: 프로젝트의 9 kg 축소 카트리지는 7.2 kg 라인 베드와 같은 자릿수이고, 실규모 주 베드(약 660 kg)는 문서의 60 kg 가정의 약 11배입니다(보고서의 산술).

## 문헌별 정리

### 5.1 Robertson, ORNL-TM-0728 (MSRE 설계 보고서 Part I) 　검증: verified (본문, OCR 노이즈)

- 서지: R. C. Robertson, "MSRE Design and Operations Report, Part I: Description of Reactor Design", ORNL. 12장이 오프가스 계통입니다. 연도는 읽은 쪽에 없고 약 1965로 추정할 뿐 unverified입니다. https://media.githubusercontent.com/media/openmsr/msr-archive/master/docs/ORNL-TM-0728.pdf
- 파일: `robertson_ornl_tm0728_msre_design` (PDF 없음)
- 한 줄 요약: MSRE 오프가스 계통과 숯 베드 설계의 1차 자료입니다.
- 프로젝트와의 관계: 베드 형상, 질량, 설계 기준의 출처입니다. 프로젝트 문서의 "ORNL 참고 베드 60 kg"과 비교해야 합니다.
- 방법: 해당 없음(설계 기술). 베드는 304 스테인리스 용접 구조이고 모든 이음매를 X선 검사했으며, 물이 찬 피트에 잠겨 있습니다.

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| 주 베드 2기가 병렬이고 각각 전체 오프가스 부하를 처리할 수 있음. 각 베드는 수직 구간 2개 | | §12.4.1, 인쇄 p.375 |
| 구간 구성: 1/2 in. sched 10 관 80 ft, 이어서 3 in. sched 10 관 80 ft, 이어서 6 in. sched 10 관 80 ft(입구 쪽이 가는 관). 수직 구간 전체 높이 약 20 ft | OCR 해석 주의 | §12.4.1, 인쇄 p.375 |
| 베드당 총 부피 44 ft3, 충전 숯 약 1,455 lb (약 660 kg), 벌크 밀도 0.53 g/cc, Pittsburgh PCB 6x16 | 숯 종류 표기는 이 보고서에서 "PGB"로 읽혀 OCR 불확실 | §12.4.1 인쇄 p.375, Table 12.1 인쇄 p.357("1450 lbs") |
| 구간당 약 22 ft3(약 330 kg). 4개 구간 중 임의의 2개가 연속 오프가스 유량 약 4.25 L/min을 처리 가능, 구간 최대 유량 2.1 L/min | | 인쇄 pp.365, 375 |
| 보조 베드 숯 585 lb (약 265 kg). Table 12.1은 530 lb, 16 ft3로 상충(해소 못 함) | 간헐 배기용, 6 in. sched 10 관의 U자 구간 2개, 다리 약 19.2 ft | 인쇄 pp.375-376, Table 12.1 |
| 설계 기준: 10 MW, 펌프 보울 50 gpm 바이패스(핵분열 기체 완전 제거), 헬륨 스윕 최대 6,000 L/24 h(STP), 최소 보유 Xe 90일과 Kr 7.5일, 숯 최대 온도 250 F 가정, 냉각수 최대 약 85 F, 헬륨 약 4.2 L/min | | §12.4.1, 인쇄 p.370 |
| 펌프를 떠나는 가스 약 280 Ci/s (10 MW, 헬륨 4 L/min). 약 2시간 배관 보유 후 수냉 베드로. 베드 하류 헬륨에 유의한 동위원소는 Kr-85, Xe-131m, Xe-133뿐. 최대 Kr-85 방출 5 Ci/day | | 인쇄 p.357 |
| 베드 앞 보유 체적 설계 13 ft3(설계 유량에서 약 1.5 h, 최소 1 h): 셀 내 약 6 ft3(4 in. sched 40 관 68 ft)와 숯 베드 셀의 20 ft U자관 3개(3 in. sched 10) 약 7 ft3. 가스 비출력 0.15 W/cc 가정 | | §12.3, 인쇄 pp.369-370 |
| 베드 셀: 지름 10 ft, 깊이 22.7 ft의 물이 찬 피트, 18 in. 바라이트 콘크리트 덮개(2블록). 한 곳에서는 "최소 5.5 ft 차폐"라고도 서술 | 베드는 물에 잠김. 두 서술이 같은 보고서에 공존 | 차폐 절(인쇄 쪽 불분명) |
| 오프가스 라인 524의 4 in. 납 차폐, 벤트 하우스에서 숯 베드로 가는 라인 위 17 in. 강판, 벤트 하우스 라인 위 5 ft 바라이트 블록 | 단수명 희가스의 감마 차폐 | 차폐 절(인쇄 쪽 불분명) |

- 우리와 다른 점: 선박 소형 카트리지와 다른 용접 고정식 구조입니다. 완전한 베드는 용접되고 물에 잠긴 20 ft 배관 조립체이므로 로봇이 다룰 카트리지가 아닙니다(원자료 노트의 해석).
- 확인 못 한 것: 보고서 연도. 같은 보고서 안의 상충(585 lb 대 530 lb 및 16 ft3, 입구 배관 본문 1/2 in. 대 Table 12.1의 1-1/2 in.). 차폐 절의 정확한 쪽. 베드 안의 Kr과 Xe 재고(Ci). 이는 TM-728의 Figs. 12.3-12.5와 Table 12.2에 있으나 추출하지 않았습니다. 동적 흡착계수(cm3/g)와 가동 중 실측 베드 온도. 원출처로 추정되는 Vroom의 "MSRE Off-Gas Line and Charcoal Bed Shielding Report"와 Smith의 "Shielding of Off-Gas Lines"(ORNL MSR-61-125, TM-728 참고문헌 목록의 항목 169와 171)는 입수하지 못했습니다.

### 5.2 ORNL-TM-0732 Part V (안전 해석 보고서) 　검증: verified (본문). 저자는 OCR 불완전

- 서지: "Reactor Safety Analysis Report", MSRE Design and Operations Report의 Part V(OCR에 Beall, Haubenreich 등이 일부 깨져 읽힘). https://media.githubusercontent.com/media/openmsr/msr-archive/master/docs/ORNL-TM-0732.pdf
- 파일: `ornl_tm0732_safety_analysis` (PDF 없음)
- 한 줄 요약: MSRE 안전 해석이고 오프가스 보유일수와 희석 가정을 담고 있습니다.
- 프로젝트와의 관계: 보유일수 가정(TM-728과 다름)과 가스 부피 안 선량률 경험식의 출처입니다.
- 방법: 숯 보유 후 굴뚝 공기로 희석해 굴뚝 Kr-85 농도를 맞추는 안전 해석.

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| 숯 보유 최소 Kr 6일, Xe 72일 | TM-728의 7.5일과 90일보다 보수적 | §1 |
| 굴뚝 공기 약 18,000 cfm으로 희석해 굴뚝에서 Kr-85를 1e-7 uCi/cc로 | | §1 |
| 굴뚝 배출에 유의한 동위원소로는 Kr-85만 남음(소량의 Xe-131m, Xe-133 포함) | | §1 |
| 가스 부피 안 선량률 경험식 r/hr = 935 x uCi/cm3 x MeV | 무한 매질 근사 | 부록 |

- 우리와 다른 점: 구역 배경 추정(블로어 하우스 쪽과 전기 서비스 구역의 mr/hr 값)은 가동 기준 추정이고 베드 값이 아니라 싣지 않았습니다(쪽을 추적하지 않음).
- 확인 못 한 것: 쪽 번호. 구역 배경 값의 정확한 위치.

### 5.3 ORNL-4037 (MSR 프로그램 반기 보고서, 1966.8 종료 기간) 　검증: verified (해당 절)

- 서지: MSR Program Semiannual Progress Report, period ending Aug 31, 1966. https://media.githubusercontent.com/media/openmsr/msr-archive/master/docs/ORNL-4037.pdf
- 파일: `ornl4037_msr_semiannual_1966` (PDF 없음)
- 한 줄 요약: MSRE 운전 중 쓰인 소형 숯 베드와 유기 증기 트랩, 주 베드 운전 문제를 보고합니다.
- 프로젝트와의 관계: 로봇이 다룰 만한 크기의 베드 선례이고, 보조 베드를 교체용으로 설계한 사례입니다. 프로젝트 9 kg 카트리지의 방어 가능한 선례는 여기까지입니다.
- 방법: 해당 없음.

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| 라인 524 베드: 3 in. sched 10 관 9 ft를 머리핀 모양으로 구성, 숯 15.8 lb (약 7.2 kg), 벌크 밀도 0.47 g/cm3, 100 cm3/min 헬륨에서 보유 Kr 약 2.5일, Xe 약 30일 | 추정 | §2.8-2.9, pp.75-78 |
| 라인 522 유기 증기 트랩: 1 in. IPS 관 13 ft 4 in.(읽은 대로), 숯 1,092 g, 0.5 g/cm3, 수냉. Kr과 Xe 베타 붕괴열만으로 0.1 kW/liter 추정 | | §2.8-2.9, pp.75-78 |
| 숯의 열은 주로 크립톤, 제논, 그 딸핵종의 베타 붕괴에서 나옴. 설계자는 필터 앞에서 생긴 딸핵종이 모두 부유해 필터로 옮겨진다는 최악 가정을 씀 | | §2.8, p.75 |
| 주 베드 입구(강철솜 구역) 압력강하가 반복 상승해 약 주 1회 역취입으로 해소. 입구가 막힌 보조 베드를 "원자로 정지 시간을 최소로 하며 설치와 연결할 수 있는" 교체 베드로 설계 | 정지 시간 최소화가 설계 의도. 활성 이탈은 굴뚝 모니터에서 Kr-85 외에는 없었음 | Ch. 1, pp.45-47 |

- 우리와 다른 점: 서비스 목적(역확산 보호와 유기물)이 주 보유 기능과 다릅니다. 쪽이 인쇄 쪽인지 PDF 쪽인지 원자료에 명시되지 않았습니다(`00_확인필요_목록.md` (e)).
- 확인 못 한 것: 해당 절 밖의 내용. 쪽 종류.

### 5.4 Adams, Browning (1958) ORNL/CF-584-14 　검증: partial (요약만)

- 서지: HRT(Homogeneous Reactor Test) 오프가스 보고서. https://digital.library.unt.edu/ark:/67531/metadc1018378/m2/1/high_res_d/4344036.pdf
- 파일: `adams1958_ornl_cf584_14_hrt` (PDF 없음)
- 한 줄 요약: 초기 HRT 숯 베드 설계 비교 자료입니다.
- 프로젝트와의 관계: 병렬 2기 구성의 선행 사례와 Xe가 Kr보다 훨씬 잘 흡착된다는 정성 비교.
- 쓸 수 있는 수치: 없음. 베드당 숯 양, Xe 대 Kr 흡착비, 계산된 Kr-85 방출량이 원자료에 있으나 쪽 단위로 확인하지 않아 싣지 않았습니다.
- 우리와 다른 점: 1958년 HRT이고 MSRE와 다릅니다.
- 확인 못 한 것: 쪽 단위 위치, 본문.

### 5.5 McFarlane et al. (2019) ORNL/TM-2019/1266, PNNL-28974 　검증: verified (서지, 요약)

- 서지: "Fission Product Volatility and Off-Gas Systems for Molten Salt Reactors", 2019-08. https://info.ornl.gov/sites/publications/Files/Pub129748.pdf
- 파일: `mcfarlane2019_offgas_volatility` (PDF 없음)
- 한 줄 요약: 현대 MSR의 핵분열 생성물 휘발과 오프가스 계통 개관입니다.
- 프로젝트와의 관계: 숯 베드에서 90일 붕괴 후 Kr-85가 선원항이라는 배경 근거입니다.

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| 숯 베드에서 방사성 핵종이 90일 붕괴하면 Kr-85가 선원항에서 가장 중요한 기여 핵종으로 남음 | | p.3 |
| 40 CFR 190.10의 Kr-85 한도 50,000 Ci/GW(e)-yr | | p.26 |

- 우리와 다른 점: MSRE 베드 질량이나 치수가 없습니다.
- 확인 못 한 것: 본문 전체.

### 5.6 McFarlane et al. (2020) ORNL/TM-2020/1602, PNNL-30159 　검증: verified (요약)

- 서지: "Molten Salt Reactor Engineering Study for Off-Gas Management". https://info.ornl.gov/sites/publications/Files/Pub142799.pdf
- 파일: `mcfarlane2020_offgas_engineering` (PDF 없음)
- 한 줄 요약: MSR 오프가스 관리 공학 연구입니다.
- 프로젝트와의 관계: MSBR 오프가스 개략 규모 배경과 Kr-85 반감기 표기의 불일치 근거입니다.

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| 헬륨 312 L/min, 오프가스 붕괴열 21.3 MW | 1971년 MSBR 오프가스 개략도 | p.5 |
| Kr-85 반감기 10.76 y | 같은 보고서가 다른 값을 적음 | p.12 |
| Kr-85 반감기 10.73 y | 같은 보고서가 다른 값을 적음. NNDC는 10.739 y(5.9) | p.15 |

- 우리와 다른 점: 베드 질량, 흡착계수, 선량률이 없습니다.
- 확인 못 한 것: 본문 전체.

### 5.7 Andrews et al. (2021) 　검증: verified (서지만)

- 서지: Andrews, McFarlane, Chapel, Bull Ezell, Holcomb, de Wet, Greenwood, Myhre, Bryan, Lines, Riley, Felmy, Humrickhouse, "Review of molten salt reactor off-gas management considerations", Nuclear Engineering and Design 385 (2021-12-15), DOI 10.1016/j.nucengdes.2021.111529. https://impact.ornl.gov/en/publications/review-of-molten-salt-reactor-off-gas-management-considerations/
- 파일: `andrews2021_msr_offgas_review` (PDF 없음)
- 한 줄 요약: MSR 오프가스 관리 고려사항 리뷰입니다.
- 프로젝트와의 관계: 리뷰 인용용입니다.
- 쓸 수 있는 수치: 없음(전문 미확보).
- 우리와 다른 점: 해당 없음.
- 확인 못 한 것: 전문.

### 5.8 Andrews, McFarlane, Thallapally, INL GAIN MSR Integrated Off Gas Roadmap 　검증: verified (슬라이드)

- 서지: INL GAIN 슬라이드(무기재, 2026/05 업로드 경로). https://gain.inl.gov/content/uploads/4/2026/05/09-H.Andrews-MSR-Integrated-Off-Gas-Roadmap.pdf
- 파일: `andrews_inl_gain_offgas_roadmap` (PDF 없음)
- 한 줄 요약: MSR 오프가스 로드맵 슬라이드입니다.
- 프로젝트와의 관계: 단수명 Xe 핵종의 반감기를 제공합니다(초기 선원항 근거).

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| 반감기: Xe-135 9.1 h, Xe-135m 15.3 min, Xe-137 3.83 min, Xe-139 39.5 s | | 슬라이드 24 |
| Copenhagen Atomics가 업계 참여자로 열거됨 | | 슬라이드 5 |

- 우리와 다른 점: 벤더 설계 정보가 없습니다. Terrestrial Energy, Kairos, Copenhagen Atomics, ARPA-E의 검증 가능한 오프가스 베드 자료는 찾지 못했습니다.
- 확인 못 한 것: 슬라이드 날짜.

### 5.9 NNDC NuDat: Kr-85 　검증: verified

- 서지: Nuclear Data Sheets 116, 1 (2014). https://www.nndc.bnl.gov/nudat3/decaysearchdirect.jsp?nuc=85KR&unc=nds
- 파일: `nndc2014_kr85_decay_data` (PDF 없음)
- 한 줄 요약: Kr-85 붕괴 자료입니다.
- 프로젝트와의 관계: 선원항의 핵자료입니다. Kr-85만 남은 베드의 감마선량이 매우 작게 나오는 이유의 근거입니다.

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| 반감기 10.739 y | | NuDat 붕괴 검색 페이지 |
| 주 베타 분기 끝점 에너지 251.59 keV (99.563%), 부 베타 분기 47.65 keV (0.434%) | | NuDat 붕괴 검색 페이지 |
| 감마 513.997 keV, 강도 0.434% (0.00223 MeV/Bq-s) | | NuDat 붕괴 검색 페이지 |

- 우리와 다른 점: 해당 없음.
- 확인 못 한 것: Xe-133, Xe-131m, Xe-135, Kr-87, Kr-88의 감마 에너지와 수율은 찾지 못했습니다. 원자료 노트가 기억에서 쓴 Xe-133(81 keV)과 Xe-131m(164 keV)의 에너지는 핵자료로 확인되지 않아 싣지 않습니다. 제동복사 수율 자료도 찾지 못했습니다.

### 5.10 Hubbell, Seltzer (1995) NISTIR 5632 　검증: verified

- 서지: "Tables of X-Ray Mass Attenuation Coefficients and Mass Energy-Absorption Coefficients 1 keV to 20 MeV for Elements Z = 1 to 92 and 48 Additional Substances of Dosimetric Interest", NIST, 1995-05. https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir5632.pdf
- 파일: `hubbell1995_nistir5632` (PDF 없음)
- 한 줄 요약: 질량감쇠계수와 질량에너지흡수계수 표입니다.
- 프로젝트와의 관계: 차폐 투과율 `S_k` 계산의 $\mu/\rho$ 출처 후보입니다. 값은 NIST 광자 상호작용 데이터베이스에서 오고 광전, 간섭성, 비간섭성, 쌍생성 기여를 포함합니다.
- 쓸 수 있는 수치: 없음(표 값을 옮기지 않음). 범위는 1 keV~20 MeV, Z = 1~92 및 선량 측정용 추가 물질 48종입니다(표제).
- 우리와 다른 점: 해당 없음.
- 확인 못 한 것: 해당 없음.

### 5.11 NIST XCOM 　검증: partial (페이지 존재만, 인용문 미독)

- 서지: NIST Photon Cross Sections Database(Berger, Hubbell 등). https://physics.nist.gov/PhysRefData/Xcom/Text/version.shtml
- 파일: `nist_xcom` (PDF 없음)
- 한 줄 요약: 감쇠계수 계산 웹 도구입니다.
- 프로젝트와의 관계: 투과율을 인용 대신 직접 계산하는 도구 후보입니다.
- 쓸 수 있는 수치: 없음.
- 우리와 다른 점: 해당 없음.
- 확인 못 한 것: 인용 서지(버전 이력 페이지의 존재만 확인).

### 5.12 Shultis, Faw: Handbook of Nuclear Engineering 장 　검증: partial (읽은 부분에서 선원 방정식 못 찾음)

- 서지: "Radiation Shielding and Radiological Protection", Handbook of Nuclear Engineering (D. G. Cacuci 편), Springer. https://www.mne.ksu.edu/~jks/books/Ch11fulltext.pdf
- 파일: `shultis_faw_handbook_ch` (PDF 없음)
- 한 줄 요약: 방사선 감쇠 계산의 기본 방법과 광자 감쇠 계산을 다룬 장입니다.
- 프로젝트와의 관계: 점커널 이론과 선선원 유도의 후보 출처입니다.
- 쓸 수 있는 수치: 없음. 가져온 본문 105,525자 중 앞 100,000자에서 선선원 방정식을 찾지 못했고 식 번호도 없습니다.
- 우리와 다른 점: 해당 없음.
- 확인 못 한 것: 선선원 식과 식 번호.

### 5.13 Shultis, Faw (2000) Radiation Shielding 　검증: unverified (기억만)

- 서지: American Nuclear Society, 2000 (1996년 Prentice Hall 판의 재판이라는 기억). ANS 상점 페이지는 도서 목차였고 이 책의 근거를 주지 않았습니다.
- 파일: `shultis_faw2000_radiation_shielding` (PDF 없음)
- 한 줄 요약: 점커널법, 선선원과 유한 선선원, 빌드업 계수를 다룬다고 기억되는 교재입니다.
- 프로젝트와의 관계: 원자료 노트는 유한 선선원의 시버트(Sievert)형 적분 유도를 이 교재에서 읽으라고 권합니다.
- 쓸 수 있는 수치: 없음. 장과 식 번호는 확인하지 못했습니다.
- 우리와 다른 점: 해당 없음.
- 확인 못 한 것: 원서 직접 확인이 필요합니다.

### 5.14 ANSI/ANS-6.4.3 　검증: unverified (지정 번호와 연도 미확인)

- 서지: "Gamma-Ray Attenuation Coefficients and Buildup Factors for Engineering Materials" (1991판이라는 기억, Harima 등의 빌드업 자료가 보통의 출처). 가져온 ANS 상점 페이지가 이 표준이 아니라 도서 목차였습니다.
- 파일: `ans1991_6_4_3_buildup` (PDF 없음)
- 한 줄 요약: 빌드업 계수 표준으로 기억되는 문서입니다.
- 프로젝트와의 관계: 차폐 경우의 빌드업 데이터셋 후보입니다.
- 쓸 수 있는 수치: 없음.
- 우리와 다른 점: 해당 없음.
- 확인 못 한 것: 지정 번호, 연도, 내용.

## 갈래 전체: 선원항과 해석적 검증에 대한 정리

- 베드의 나이(마지막 가동 후 붕괴 시간)가 선원항을 지배합니다. Kr-85는 514 keV 감마 분기가 0.434%에 불과해(5.9), Kr-85만 남은 베드의 감마선과 제동복사 선량장은 가동 직후 1~2시간 된 스트림을 담은 베드보다 자릿수로 약합니다. 이는 원자료 노트의 추론이며, 노트는 그래서 선량 격자 메타데이터에 붕괴 시간을 적으라고 합니다.
- 베드 표면이나 거리별 선량률이 없으므로 프로젝트 선량은 모델 값입니다. 방사선 파트의 선량 격자가 올 때까지 상대 비교용으로만 표기해야 합니다.
- 해석적 검증용 공식(원자료 노트의 추론이며 Shultis와 Faw의 식 번호는 미확인): 점 등방 선원의 선량은 선속-선량 환산 계수를 곱해

$$D = \frac{S\,B(\mu r)\,e^{-\mu r}}{4\pi r^{2}}$$

이고, 유한 선선원은 이를 선을 따라 적분한 시버트형 적분입니다. 프로젝트의 기존 $1/r^2$ 검증은 차폐가 없는 극한입니다. 차폐가 있는 경우에는 $\mu/\rho$(5.10, 5.11)와 빌드업 데이터셋(5.14)이 필요합니다.
- 베드 크기 비교(보고서의 산술): 7.2 kg 라인 베드는 프로젝트 9 kg 카트리지의 약 0.8배이고, 실규모 주 베드 약 660 kg은 프로젝트 문서의 60 kg 가정의 약 11배입니다.
- 보조 베드 숯은 585 lb(약 265 kg)와 530 lb 두 값이 상충합니다(5.1). 원자료 노트가 적은 "265~295 kg" 범위는 530 lb의 환산과 맞지 않아 `00_확인필요_목록.md` (e)에 넣었습니다.

## 갈래 전체에서 확인 못 한 것

- MSRE 주 베드의 Kr-85와 Xe 재고(Ci), 동적 흡착계수, 가동 중 실측 베드 온도.
- 베드 표면과 거리별 선량률: Vroom 차폐 보고서가 가장 먼저 찾을 자료이며 OSTI 검색에서는 찾지 못했습니다.
- ORNL-TM-3884는 오프가스나 숯 보고서가 아니라 MSRE의 귀금속 이동에 관한 Kedl의 보고서이고(숯 언급 한 번), ORNL-4676은 1971.2 종료 반기 보고서(숯 언급 한 번), ORNL-4865는 MSRE 핵분열 생성물 거동(Compere 등)이며 숯 언급이 적습니다. 이 셋은 60 kg 값을 찾으려 훑었을 뿐 이 갈래의 문헌으로 정리하지 않았습니다. ORNL-4728과 TM-3524도 같은 목적으로 훑었습니다.
- Terrestrial Energy IMSR, Kairos, Copenhagen Atomics, ARPA-E 등 벤더 설계의 오프가스 베드 자료.
- OSTI나 ADAMS와 openmsr 사본의 대조.
- Shultis와 Faw의 선선원 식 번호, ANSI/ANS-6.4.3 서지, Xe-133과 Xe-131m 감마 에너지, 제동복사 수율.
