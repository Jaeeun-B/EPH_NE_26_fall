# 06 MARINA 공개자료 대조 (갈래 노트)

## 새 방향과의 관계

- 팀 spec(팀 내부 자료, 2026-10-06 수신)의 사업, 원자로, 연료염, 배수계통, 오프가스, 탑재 선박 항목이 공개 출처로 어디까지 뒷받침되는지 적은 노트입니다. 채원(선원항: 열출력, 연료염 조성, 오프가스 구성)과 재은(통합: spec 값의 출처 표기)이 씁니다.
- Xe 단일 타겟 결정 이후에도 유효합니다. 공개된 오프가스 6단 구성에 "장기지연 Xe holdup" 단이 따로 있어(6.12) Xe 전용 베드라는 새 방향과 맞습니다. 이 단과 새 방향의 베드를 같은 것으로 보는 것은 이 노트의 해석입니다. "단수명 Xe·Kr holdup" 단은 Kr을 다루지 않는 새 방향에서는 범위 밖입니다.
- 베드 제원(He 유량, 베드 질량, 치수)은 어떤 공개 자료에도 없습니다(6.12). 정현의 Thomas 입력과 재은의 베드 모듈 크기는 계속 ORNL 참조값(`08_오프가스_선원항.md`)과 KAERI PSA 자료(`10_Xe_베드모듈.md`)에 기댑니다.
- 센추리 발표(KNS 2026 춘계 Q워크숍)는 게시물로 존재가 확인됐지만 슬라이드를 열지 못했습니다(6.26). 이중베드 여부, 베드 크기, 재생 대 교체가 담겼을 가능성이 가장 큰 공개 자료입니다.

- 갈래: 원자력 원격조작(해양 원자로 배경), 선량 모델(선원항 입력값의 출처 판별)
- 근거: 연구 원자료 노트 `marina_public_sources.md`, `xe_bed_module.md` 2절, 보고서 "MARINA 반영 참고문헌 보강" 1절과 6절 (모두 저장소 밖). 원문 PDF나 기사와 다시 대조하지 않았습니다.
- 대조 대상: 팀 spec(팀 내부 자료, 2026-10-06 수신)의 A~H 섹션. spec 값은 상이 판정에 필요한 것만 적었습니다. 하단 오프가스 참조표(MSRE, MSDR, MSBR, 흡착제)는 `08_오프가스_선원항.md`, 연료처리 셀 치수는 `11_핫셀_공간치수.md`에서 다룹니다.
- 조사일: 2026-10-06 (센추리 게시물 확인은 2026-10-11 원자료 노트)
- 파일: 모든 문헌이 PDF 없음. 파일명은 `refs/README.md` 표의 임시 이름입니다.
- 위치 표기: KNS 논문은 절, 표, 그림 번호로 적었습니다. 기사는 쪽 구분이 없어 "기사 본문"과 게재일로 적었습니다(02 2.9의 웹 기사 표기와 같음). 원자료에 위치가 기록되지 않은 수치는 싣지 않고 항목 이름만 "확인 못 한 것"에 적었습니다.
- 결과 표기: 확인(공개 출처 값과 일치), 상이(출처 값이 다름), 미발견(공개 출처를 찾지 못함), 부분(일부만 확인).

## 갈래 요약

- 사업 기간, 사업비, 일정, AiP 3건, 출력, 모듈 질량, 연료염 조성과 물성, 배수계통 제원은 공개 출처와 대부분 일치합니다. 연료염 물성과 배수계통 묶음은 KAERI 배수계통 논문 한 편(6.13)과 정확히 맞아 1차 출처로 쓰기 좋습니다.
- 노심 설계 묶음(반사체 두께, BeO 물성, HALEU와 염소 장전량, 노외 체적, 목표 운전기간, 연소도)은 KAERI 공개 논문에서 찾지 못했습니다. 반사체 60 cm와 내부 배리어 두께는 KAIST 연구(6.17)에 나오는 값입니다.
- 오프가스 6단 구성은 KAERI 류용희 외(2024, 6.12)와 문장 단위로 일치합니다. 이 논문에는 베드 사이징 수치가 하나도 없습니다.
- 원격 매니퓰레이터와 핫셀은 KAERI 논문 4편과 기사 어디에도 언급이 없습니다. 공개된 유지보수 개념은 "선내 크레인으로 주요 기기 유지보수와 교체"뿐입니다(6.2).
- 유도값 시트의 산술은 프로젝트 자체 재계산과 일치했습니다(보고서 1절 "유도값 시트" 소절). 고칠 것은 입력 가정이며 `08_오프가스_선원항.md`에 정리했습니다.

## spec 항목별 대조표 (A~H 섹션)

괄호 안 번호는 아래 "문헌별 정리"의 소절입니다.

| spec No. | 항목 | 결과 | 공개 출처와 위치 |
|---|---|---|---|
| 1 | 명칭 MARINA | 부분 | 명칭은 확인(6.3, 6.4 기사 본문). 영문 풀이(Marine Nuclear Reactor)는 미발견 |
| 2 | 개발 주관 | 부분 | 사업명은 "용융염원자로 원천·혁신기술개발사업"(6.1 보도자료 본문). "사업단" 조직명은 미발견, 기사는 "이동형 PD"로 표기(6.2) |
| 3 | 참여기관 | 부분 | 삼성중공업, HD한국조선해양, HMM 세 곳은 함께 "설계 단계에 참여"로 묶임(6.2). KRISO는 삼성중공업과 고속 선형, 배치 설계 담당으로 확인(6.3). 센추리는 KNS 2026 춘계 Q워크숍 발표자로 확인되나 발표 내용은 미열람(6.26) |
| 4~5 | 사업 기간, 사업비 | 확인 | 2023~2026년(6.3, 6.1), 290억원(6.3 기사 본문. 6.1에는 금액 없음) |
| 6~9 | 일정 | 확인 | 개념설계 2026, 기본설계와 실증, 인허가 준비 2027~2032, 인허가 2033~2034, 건조 2035(6.2 기사 본문). 예타 보도는 2035 시험선 착수, 2037 개발 완료, 2040 첫 수주(6.5) |
| 10 | 후속 국가사업 | 확인(명칭 조정) | 8,900억원(6.2). 공식 명칭 "탄소중립 선도 해양용 용융염원자로 기술개발사업", 예타 최종 대상(6.6). K-문샷 12대 미션(6.7) |
| 11 | AiP 실적 3건 | 확인 | LNG선 ABS와 라이베리아 기국(6.1), 15,000TEU ABS(6.3, 6.11. 수여일 자체는 미확인), 자동차운반선 LR 7,000 CEU(6.7, 6.10) |
| 12 | 원자로 형식 | 부분 | NaCl-KCl-UCl3(6.13 §2), BeO 환형 배치(6.14, 절 번호 미기재). "감속 반사체 MSFR" 분류는 KAIST 계열 학술지 제목의 표현(6.28) |
| 13~14 | 열출력, 전기출력 | 확인 | 100 MWth, 35 MWe(6.2 기사 본문), "100-MW K-MSR"(6.12 §2.4) |
| 15 | 열효율 | 미발견(유도값) | 출력 두 값의 비이며 명시한 출처 없음 |
| 16 | 출구온도 | 확인 | "약 620℃"(6.2 기사 본문) |
| 17 | 운전 압력 | 미발견 | 6.10의 "near-atmospheric"은 MIT 원자로 설명이라 인용 불가 |
| 18 | 연료 무교체 기간 | 상이 | 수치를 쓴 공개 출처는 25~30년(6.4 기사 본문). spec의 기간을 쓴 출처는 미발견 |
| 19 | 목표 운전기간 | 미발견 | 국내 유사 연구 설정은 KAIST 25 EFPY(6.17 §2.2), FNC 28년(6.20 §2.1). 그 밖의 설정값(6.19, 6.22, 6.23)은 위치 미기재로 싣지 않음 |
| 20~21 | 모듈 질량, 차폐 질량 | 확인 | 모듈 약 300 t, 그중 200 t 이상이 차폐(6.2 기사 본문, 구경회 박사 발언) |
| 22 | 차폐 방식 | 부분 | 기사 요약에만 나오고 원문 문장은 미확보, 재질과 두께는 미공개(6.2) |
| 23~24 | 탑재, 유지보수 | 확인 | 엔진룸 직접 탑재, 선내 크레인으로 유지보수와 교체(6.2 기사 본문). 매니퓰레이터와 핫셀 언급은 없음 |
| 26~27 | 노심 형상, 유동 | 미발견 | FNC의 반구 캡 노심(6.20 §2.1, Fig. 1)은 MARINA 자료가 아님 |
| 28 | 반사체 재질 | 부분 | BeO 사용만 확인(6.14). 대안 재질은 국내 연구 동향과 맞지만 MARINA 공식 대안이라는 근거 없음 |
| 29 | 반사체 두께 | 상이 | spec의 60 cm는 KAIST 연구의 MgO 반사체 두께(6.17 §2.2). BeO 두께는 FNC 95~100 cm(6.19 Table 1, 5) |
| 30~31 | BeO 밀도, 열전도도 | 미발견 | |
| 32 | 내부 배리어 | 부분 | SS316 8 mm와 Inconel 625 0.8 mm는 KAIST 연구값(6.17 §2.2). KAERI는 Inconel 625를 부식 방지 후보로만 언급(6.14) |
| 33 | 반응도 제어 | 부분 / 미발견 | KAIST 연구 노심의 B4C 드럼 7개(6.17 §3.3). MARINA 방식과 비상정지판은 미발견 |
| 37 | 연료염 조성 | 확인 | 42.9-20.3-36.8 mol%(6.13 §2) |
| 38 | 농축도 | 부분 | 19.75 wt%는 KAERI 조성을 쓰는 FNC 연구(6.19 Table 1)에서 확인. KAERI 논문에서는 직접 확인 못 함 |
| 41~42 | 밀도, 점도(605 °C) | 확인 | 6.13 Table I |
| 43 | 핵설계 평균 연료염 온도 | 미발견 | KAIST 연구의 "900 K isothermal" 설정(6.17 §2.1)은 조성이 다른 혼합염 |
| 44~46, 48 | HALEU, 염소, 노외 체적, 연소도 | 미발견 | KAIST 혼합염 설계는 HALEU 12.35 t, 73.90 MWd/kgU로 다름(6.17 Table III). 출처로 의심되는 학술지 2편은 본문 접근 불가(6.28) |
| 47 | FSL 체적 | 확인 | 11.23 m3(6.13 Table III) |
| 50 | 산화환원 제어 | 미발견 | |
| 51 | 예열 목표온도 | 부분 | 온도 값은 6.14 본문 문장과 일치(절 번호 미기재). "1일 이내"는 미확인 |
| 52~53 | 1차계통, 이중화 | 확인 | 순환펌프와 열교환기 이중화(6.2 기사 본문) |
| 54~60 | 배수계통 | 확인 | FSL 높이 3.320 m, 등가직경 2.075 m, 배수탱크 2.7 m x 2.7 m, 배수관 0.127 m, 경사 3°와 경사부 5 m(6.13 Table III), 배수 목표 약 10분(6.13 §5.1), 동결밸브 2개(6.13 §2). 동결밸브 추가 제원은 6.15 |
| 61~62 | 비상정지, 잔열 제거 | 확인 | 6.2 기사 본문 |
| 63 | 동력변환 | 부분 | K-MSR을 기준로로 둔 KAIST 연구(6.16). 냉각염 융점은 미확인. "확정 사양 미확인" 비고는 유지 |
| 64~67 | 구조재료 | 확인 | 316H(6.15 Table 1, 6.14), 특수 표면처리(6.2 기사 본문) |
| 68 | 오프가스 구성 | 확인 | 6단 구성 원문 문장과 일치(6.12 §2.4, Fig. 4). spec의 "할로겐"은 원문 "halide" |
| 69 | 운반, 커버 가스 | 부분 | 마지막 단 "He storage tank"로 간접 확인(6.12) |
| 70~71 | 참조 노형, 계통 형태 | 확인 / 표기 적절 | 논문은 MSDR과 MSBR만 "closed system"으로 기술(6.12 §2.2~2.3) |
| 72~73 | Kr-85 처리, FP 제거 최소화 철학 | 미발견 | 오프가스 논문에 해당 서술 없음. Xe 단일 타겟 결정 이후 No.72는 참고만(Kr) |
| 75 | 흡착베드 제원 | 확인(미공개) | He 유량, 베드 질량과 치수, 온도와 압력 모두 없음(6.12) |
| 76~81 | 탑재 선박 | 확인 | 15,000TEU, 2기, 23 kn 이상(6.2), 25 kn급 선형, 중앙 배치(6.3, 6.11 기사 본문) |
| 82 | LNG선 적용 | 확인 / 상이 | 174,000 m3(6.8 기사 본문). 6.9는 이전 ABS 연구를 인용해 145,000 m3 |
| 84~85 | 기타 활용, 규제 동향 | 확인 | 6.2 기사 본문. IAEA ATLAS 출범은 `07_선박경사_기준.md` |

미발견 항목은 흩어져 있지 않습니다. No.19, 29~31, 43~46, 48은 서로 맞물린 노심 설계 묶음으로 보이고 KAERI 공개 KNS 논문에는 없으므로, KAIST 학술지 논문이나 비공개 자료에서 왔을 가능성이 있습니다(원자료 노트의 추론). 출처를 확인하기 전까지는 "공개 원문 미확인"으로 표시하는 것이 안전합니다.

## spec 정정 요약 (A~H 섹션)

보고서 1절 "고쳐야 할 spec 항목" 표 중 이 노트 범위의 것입니다. 참조표 항목(MSRE 280 Ci/s 기준 출력, Xe/Kr 비, MSDR 보고서 번호, He 유량, 딸핵종 등)은 `08_오프가스_선원항.md`, 연료처리 셀 치수는 `11_핫셀_공간치수.md`에 있습니다. spec을 고치는 것은 팀 결정 사항이며 이 노트는 고치지 않았습니다.

| 보고서 # | spec 위치 | 수정안 요지 | 근거 |
|---|---|---|---|
| 5 | No.3 참여기관, G 섹션 출처 | 2026-10-06 보고서는 "센추리 삭제 또는 출처 미확인"을 권했으나, 2026-10-11 원자료 노트가 KNS 게시물을 찾아 **센추리 표기는 유지 가능**. 출처를 "김화평(센추리), KNS 2026 춘계 Q워크숍(2026-05-06) 발표"로 적고, G 섹션 6단 구성의 문장 출처는 류용희 외(2024)로 병기 | 6.26, 6.12 |
| 6 | No.3 참여기관 | "삼성중공업, HD한국조선해양, HMM 설계 단계 참여"로. HMM을 "자문"으로 요약한 추출 결과도 있었으나 원문 문장은 세 곳을 함께 묶음 | 6.2 |
| 7 | No.18 무교체 기간 | "선박 운용기간(25~30년) 동안 무교체"로 고치거나 두 값을 병기하고 No.19와의 관계를 명시 | 6.4 |
| 8 | 유도 시트 Cl-37 농축도 | 공개 근거 없음. 공개 연구 사례(6.22)는 다른 값을 씀(위치 미기재). 출처를 붙이거나 민감도 입력으로 | 6.22 |
| 11 | No.29, 32, 43 | "KAIST 해양 MSFR 연구 설정값(MARINA 공개값 아님)"으로 표기. 60 cm는 MgO 두께 | 6.17 |
| 12 | No.10 사업명 | "탄소중립 선도 해양용 용융염원자로 기술개발사업" | 6.6 |
| 17 | No.82, No.11 ③ | 174,000 m3 유지, 145,000 m3는 각주. ③에 "7,000 CEU PCTC, HD한국조선해양, HD현대중공업, 현대글로비스, 지마린서비스 참여" 추가 | 6.8, 6.9, 6.7 |
| (추가) | No.1, 17, 19, 30~31, 44~46 | 고칠 값은 없고 "공개 출처 미확인" 표기만 붙임 | 대조표 |

## 문헌별 정리

### 6.1 한국원자력연구원 보도자료 (2025-09-09) 　검증: verified

- 서지: 한국원자력연구원, 「원자로로 가는 배, 첫발을 떼다」, 보도자료, 2025-09-09. https://kaeri.re.kr/kntc/board/view?linkId=12638&menuId=MENU00326
- 파일: `kaeri2025_press_lng_aip` (PDF 없음)
- 한 줄 요약: KAERI와 삼성중공업의 MSR 추진 LNG운반선 AiP(ABS, 라이베리아 기국) 보도자료입니다.
- 프로젝트와의 관계: spec No.2(사업명), No.4(기간), No.11 ①의 1차 출처입니다.

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| 사업명 "용융염원자로 원천·혁신기술개발사업", 2023~2026, 과기정통부와 해수부 | 2026년까지 해양용 MSR 개념설계 완료 목표 | 보도자료 본문 |
| MSR 100 MWth 1기, 선박 수명 동안 연료 교체 없이 운용 | LNG운반선 AiP, Gastech 2025 발표 | 보도자료 본문 |

- 우리와 다른 점: 사업비 금액은 이 보도자료에 없습니다.
- 확인 못 한 것: ABS 본사 원문 보도자료(2차 보도로만 확인).

### 6.2 해양한국 (2026-06-30) 　검증: verified

- 서지: 류지훈, 「한국원자력연구원 'K-문샷 미션, SMR 선박 개발' 설명회」, 해양한국, 2026-06-30(설명회는 2026-06-10). https://www.monthlymaritimekorea.com/news/articleView.html?idxno=57175
- 파일: `haeyang2026_kaeri_briefing` (PDF 없음)
- 한 줄 요약: KAERI 설명회 보도이며 MARINA 공개 사양이 가장 많이 담긴 기사입니다.
- 프로젝트와의 관계: spec의 출력, 출구온도, 모듈과 차폐 질량, 탑재 방식, 유지보수 개념, 일정의 출처입니다. 재은에게는 "선내 크레인으로 유지보수와 교체"가 공개된 유일한 원격 작업 개념이라는 점이 중요합니다.

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| 열출력 100 MWth, 전기출력 35 MWe, 출구온도 약 620℃ | MARINA 모듈 | 기사 본문 |
| 모듈 약 300 t, 그중 200 t 이상이 차폐 구조물 | 구경회 박사 발언 | 기사 본문 |
| 개념설계 2026, 기본설계와 실증, 인허가 준비 2027~2032, 인허가 2033~2034, 건조 2035 | | 기사 본문 |
| 후속 사업 8,900억원 | | 기사 본문 |
| 15,000TEU 컨테이너선에 모듈 2기, 23노트 이상 | | 기사 본문 |

- 정성 사실: 엔진룸 직접 탑재 모듈, 순환펌프와 열교환기 이중화, 자연순환과 공기 냉각 기반 피동 안전계통, 선내 크레인으로 주요 기기 유지보수와 교체, 특수 표면처리로 부식 저항성 확보 개발 중, 쇄빙선과 해상 데이터센터 등 활용 검토. 삼성중공업, HD한국조선해양, HMM 세 곳이 함께 "설계 단계에 참여"로 묶여 있습니다.
- 우리와 다른 점: 기사이며 설계 문서가 아닙니다. 매니퓰레이터와 핫셀 언급은 없습니다.
- 확인 못 한 것: "다중 방사선 차폐" 원문 문장(요약에만 나옴), 크레인 용량, 모듈 인출 경로.

### 6.3 ZDNet Korea (2026-07-16) 　검증: verified

- 서지: 박희범, 「용융염원자로(MSR) 컨테이너선 개념설계, 미국서 기본승인 획득」, ZDNet Korea, 2026-07-16. https://zdnet.co.kr/view/?no=20260716202107
- 파일: `zdnet2026_container_aip` (PDF 없음)
- 한 줄 요약: 15,000TEU 컨테이너선 개념설계의 ABS AiP 보도입니다.
- 프로젝트와의 관계: spec No.1, 3(KRISO), 4~5, 11 ②, 76~81의 출처입니다.

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| 개념설계 사업 기간 2023~2026년, 사업 예산 290억원 | | 기사 본문 |
| 25노트급 고속 선형, 원자로 중앙 배치(파랑 영향과 충돌 위험 최소화) | | 기사 본문 |

- 우리와 다른 점: 기사에 "운전 온도 600~700도"라는 범위 표현도 있으나 spec 출구온도의 출처는 6.2입니다.
- 확인 못 한 것: AiP 수여일.

### 6.4 이코노믹리뷰 (2026-09-29) 　검증: verified

- 서지: 장지현, 「정부, 2035년 'SMR 선박' 건조 착수…K조선 "이젠 실증·규제 싸움"」, 이코노믹리뷰, 2026-09-29. https://www.econovill.com/news/articleView.html?idxno=752182
- 파일: `econovill2026_smr_ship` (PDF 없음)
- 한 줄 요약: 정부의 SMR 선박 추진 계획 보도입니다.
- 프로젝트와의 관계: spec No.18(무교체 기간)이 다르다는 근거입니다.

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| 선박의 일반적인 운용기간 25~30년 동안 핵연료 무교체 | | 기사 본문 |
| 모듈 한 기당 전기출력 35 MW | | 기사 본문 |

- 우리와 다른 점: 기사에 나오는 기술투자펀드 금액은 MARINA 사업비와 별개입니다.
- 확인 못 한 것: 해당 없음.

### 6.5 SBS Biz (2026-04-07) 　검증: verified

- 서지: 박연신, 「원자력 선박 개발 '막차'…MSR, 예타 마지막 관문 진입」, SBS Biz(다음 게재), 2026-04-07. https://v.daum.net/v/20260407070602760
- 파일: `sbsbiz2026_msr_preliminary` (PDF 없음)
- 한 줄 요약: 해양용 MSR 사업의 예타 대상 선정 보도입니다.
- 프로젝트와의 관계: 일정의 다른 표현(시험선 기준)입니다.

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| 2035 시험선 건조 착수, 2037 개발 완료, 2040 첫 수주 | 예타 관련 보도 | 기사 본문 |

- 우리와 다른 점: spec 일정(6.2)과 기준 시점이 다릅니다.
- 확인 못 한 것: 해당 없음.

### 6.6 연합뉴스, 사이언스타임즈 게재 (2026-04-08) 　검증: partial (기자명 미확인)

- 서지: 「국산 원자력선박 2037년 띄운다…MSR 예타 막차」, 연합뉴스(사이언스타임즈 게재), 2026-04-08. https://www.sciencetimes.co.kr/nscvrg/view/menu/255?searchCategory=226&nscvrgSn=261682
- 파일: `yonhap2026_msr_preliminary` (PDF 없음)
- 한 줄 요약: 후속 사업의 공식 명칭과 예타 대상 선정 보도입니다.
- 프로젝트와의 관계: spec No.10 사업명 정정의 근거입니다.
- 쓸 수 있는 수치: 없음. 공식 명칭 "탄소중립 선도 해양용 용융염원자로 기술개발사업", 정부 R&D 예비타당성조사 최종 대상 선정(기사 본문).
- 우리와 다른 점: 해당 없음.
- 확인 못 한 것: 기자명.

### 6.7 아시아경제 (2026-06-08) 　검증: verified

- 서지: 정일웅, 「원자력연 "글로벌 선급협회 'MSR' 적용 대형 화물선 개념설계 기본 승인"」, 아시아경제, 2026-06-08. https://view.asiae.co.kr/article/2026060809131055154
- 파일: `asiae2026_pctc_aip` (PDF 없음)
- 한 줄 요약: 자동차운반선 LR AiP와 K-문샷 선정 보도입니다.
- 프로젝트와의 관계: spec No.10(K-문샷), No.11 ③의 출처입니다.

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| 7,000 CEU급 MSR 적용 자동차운반선, LR AiP | 참여: HD한국조선해양, HD현대중공업, 현대글로비스, 지마린서비스, KAERI | 기사 본문 |

- 우리와 다른 점: 해당 없음.
- 확인 못 한 것: LR 원문 보도자료.

### 6.8 문화일보 (2025-09-09) 　검증: verified

- 서지: 최지영, 「삼성중공업·원자력연구원, 원자로로 가는 LNG운반선 최초 기본승인」, 문화일보, 2025-09-09. https://www.munhwa.com/article/11531803
- 파일: `munhwa2025_lng_aip` (PDF 없음)
- 한 줄 요약: LNG운반선 AiP 국문 보도입니다.
- 프로젝트와의 관계: spec No.82의 출처입니다.

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| LNG운반선 174,000 m3 | | 기사 본문 |

- 우리와 다른 점: 6.9와 선박 크기가 다릅니다.
- 확인 못 한 것: 해당 없음.

### 6.9 Nuclear Engineering International (2025-09-11) 　검증: partial (저자 표기 불명확)

- 서지: "Nuclear LNG ship design approved", NEI, 2025-09-11. https://www.neimagazine.com/news/nuclear-lng-ship-design-approved/
- 파일: `neimag2025_nuclear_lng` (PDF 없음)
- 한 줄 요약: LNG운반선 AiP 영문 보도입니다.
- 프로젝트와의 관계: spec No.82의 상이 근거입니다.

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| 145,000 m3 | 이전 ABS 연구를 인용한 값 | 기사 본문 |

- 우리와 다른 점: 각주로 처리할 값입니다(원자료 노트의 판단).
- 확인 못 한 것: 저자.

### 6.10 World Nuclear News (2026-06-11) 　검증: partial (저자 미확인)

- 서지: "Nuclear-powered ship conceptual designs approved", WNN, 2026-06-11. https://www.world-nuclear-news.org/articles/nuclear-powered-ship-conceptual-designs-approved
- 파일: `wnn2026_conceptual_designs` (PDF 없음)
- 한 줄 요약: 자동차운반선 AiP와 MIT 원자로 AiP를 함께 다룬 영문 보도입니다.
- 프로젝트와의 관계: spec No.11 ③의 영문 출처입니다.
- 쓸 수 있는 수치: 없음(7,000 CEU는 6.7과 같음).
- 우리와 다른 점: 같은 기사의 "near-atmospheric operating pressure"는 MIT 원자로 설명이므로 MARINA 운전압력(spec No.17)의 근거로 쓰면 안 됩니다.
- 확인 못 한 것: 저자.

### 6.11 The Maritime Executive (2026-07-16) 　검증: partial (개인 저자 미표기)

- 서지: "Korean Containership with Molten Salt Nuclear Reactor Gets ABS Approval", 2026-07-16. https://maritime-executive.com/article/korean-containership-with-molten-salt-nuclear-reactor-gets-abs-approval
- 파일: `maritimeexec2026_containership_abs` (PDF 없음)
- 한 줄 요약: 컨테이너선 AiP 영문 보도입니다.
- 프로젝트와의 관계: 원자로 중앙 배치(spec No.80)의 영문 출처입니다.
- 쓸 수 있는 수치: 없음.
- 우리와 다른 점: 해당 없음.
- 확인 못 한 것: AiP 수여일.

### 6.12 Ryu, Kwak, Oh, Koo (2024) KNS 춘계 24S-599 　검증: verified

- 서지: Yonghee Ryu, Jinsung Kwak, Jinho Oh, Gyeong-Hoi Koo (KAERI), "Off-Gas System for K-MSR", Transactions of the KNS Spring Meeting, Jeju, 2024-05-09~10. https://www.kns.org/files/pre_paper/51/24S-599-류용희.pdf
- 파일: `ryu2024_kns_kmsr_offgas` (PDF 없음)
- 한 줄 요약: K-MSR 오프가스 계통의 예비 구성을 MSRE, MSDR, MSBR 경험에서 정리한 학회 논문입니다.
- 프로젝트와의 관계: spec G 섹션의 실제 문장 출처입니다. 채원(선원항)과 정현(베드 공정)에게는 "공개된 MARINA 오프가스 정보는 구성뿐"이라는 한계의 근거입니다.
- 방법: 해당 없음(구성 기술).

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| 6단 구성: decay tank 또는 holdup loop, halide/particulate/acidic species/aerosol trap, H2O/O2 trap, short-lived Xe and Kr holdup, long-delay Xe holdup, He storage tank | 100 MW K-MSR | §2.4, Fig. 4 |
| MSRE holdup 약 2시간(각 1시간), 숯 베드 Xe 90일 이상, Kr 7.5일 이상 | 참조 노형 요약 | §2.1 |
| MSDR 배수탱크 약 6시간 | 참조 노형 요약 | §2.2 |
| MSBR 배수탱크 약 2.3시간, 80% 버블 발생기 재순환, 나머지 90일 Xe holdup | 참조 노형 요약 | §2.3 |

- 우리와 다른 점: He 유량, 베드 질량과 치수, 온도와 압력이 없습니다. K-MSR 계통이 폐쇄형인지 명시하지 않고 MSDR과 MSBR만 "closed system"으로 기술합니다(§2.2~2.3). "각 1시간"이라는 표현은 ORNL 1차 출처(TM-728 §12.3)와 다르며 `08_오프가스_선원항.md`에 적었습니다.
- 확인 못 한 것: 후속 KNS 오프가스 논문(2024 추계~2026 춘계) 유무.

### 6.13 Yeo, Lee, Koo (2024) KNS 춘계 24S-327 　검증: verified

- 서지: Dongyeol Yeo, Chan Lee, Gyeong-Hoi Koo (KAERI), "Parametric study of the fuel salt drain system design of K-MSR", Trans. KNS Spring Meeting, Jeju, 2024-05-09~10. https://www.kns.org/files/pre_paper/51/24S-327-여동열.pdf
- 파일: `yeo2024_kns_kmsr_drain` (PDF 없음)
- 한 줄 요약: K-MSR 연료염 배수계통의 매개변수 연구입니다.
- 프로젝트와의 관계: 연료염 물성과 배수계통 묶음의 1차 출처입니다. 재은에게는 FSL 높이가 셀 높이 가정의 참고값이라는 점(spec No.54 비고)이 있습니다.

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| NaCl-KCl-UCl3 = 42.9-20.3-36.8 mol% | | §2 |
| 밀도 3331 kg/m3, 점도 0.002781 Pa·s | 605 °C | Table I |
| FSL 체적 11.23 m3, 높이 3.320 m, 등가직경 2.075 m | | Table III |
| 배수탱크 직경 2.7 m, 높이 2.7 m, 배수관 0.127 m(5 in.), 경사 3°, 경사부 5 m | | Table III |
| 배수 목표 약 10분 | | §5.1 |
| 동결밸브 2개(FSL 하부 1개, 배수탱크 전단 1개) | | §2 |

- 우리와 다른 점: §5.2는 해양 적용을 일반적으로 언급할 뿐 경사 조건은 없습니다.
- 확인 못 한 것: 해당 없음.

### 6.14 Jeong, Koo, Kim (2024) KNS 춘계 24S-193 　검증: verified

- 서지: Joonho Jeong, Gyeong-Hoi Koo, Taewoo Kim (KAERI), "Preliminary Thermal Analysis of the K-MSR", Trans. KNS Spring Meeting, Jeju, 2024-05-09~10. https://www.kns.org/files/pre_paper/51/24S-193-정준호.pdf
- 파일: `jeong2024_kns_kmsr_thermal` (PDF 없음)
- 한 줄 요약: K-MSR 예비 열해석입니다.
- 프로젝트와의 관계: BeO 반사체 사용, 316H 용기, Inconel 625 부식 방지 후보, 예열 목표온도의 출처입니다.
- 쓸 수 있는 수치: 없음. 예열 목표온도 문장("target temperature on the surface contacting the molten salt fuel")과 "BeO is in annular space" 문장은 확인됐지만 원자료에 절 번호가 기록되지 않아 값을 싣지 않습니다.
- 우리와 다른 점: 해당 없음.
- 확인 못 한 것: 위 두 문장의 절 번호.

### 6.15 Lee, Lee, Koo, Yu (2025) KNS 춘계 25S-303 　검증: verified

- 서지: Sungbo Lee, Chan Lee, Gyeong-Hoi Koo (KAERI), Hyoungsuk Yu (KAIST), "Numerical evaluation of thermal behavior of freeze valve system for K-MSR", Trans. KNS Spring Meeting, Jeju, 2025-05-22~23. https://www.kns.org/files/pre_paper/53/25S-303-이승보.pdf
- 파일: `lee2025_kns_freeze_valve` (PDF 없음)
- 한 줄 요약: K-MSR 동결밸브의 열 거동 수치 평가입니다.
- 프로젝트와의 관계: 배수계통 보충 제원(spec에는 없음)입니다.

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| 평탄부 길이 100 mm, 단면 150 x 35 mm2, 개폐 목표 10분, 냉각 1.6 kW, 가열 200 W | 동결밸브 | §2.1~2.2, 결론 |
| 연료염 융점 470 °C, 구조재 SS316H | | §2.1~2.2, Table 1 |

- 우리와 다른 점: 해당 없음.
- 확인 못 한 것: 해당 없음.

### 6.16 Baek et al. (2025) KNS 춘계 25S-190 　검증: verified

- 서지: Jeong Min Baek et al. (KAIST), "Load-Following Analysis of a Molten Salt Reactor and Supercritical CO2 Power Cycle for Marine Propulsion", Trans. KNS Spring Meeting, Jeju, 2025-05-22~23. https://www.kns.org/files/pre_paper/53/25S-190-백정민.pdf
- 파일: `baek2025_kns_sco2_marine` (PDF 없음)
- 한 줄 요약: K-MSR을 기준로로 둔 해양 추진용 sCO2 사이클 부하추종 해석입니다.
- 프로젝트와의 관계: spec No.63의 출처입니다. 이 프로젝트에는 직접 쓰이지 않습니다.
- 쓸 수 있는 수치: 없음. 열출력 100 MW, 연료염 NaCl-KCl-UCl3, 냉각염 NaCl-KCl-MgCl2라는 설정이 있으나 원자료에 절 위치가 없습니다.
- 우리와 다른 점: KAIST 연구 설정이며 MARINA 확정 사양이 아닙니다.
- 확인 못 한 것: 냉각염 융점.

### 6.17 Lee, Kim (2025) KNS 춘계 25S-681 　검증: verified

- 서지: Young-June Lee, Yonghee Kim (KAIST), "A Feasibility Study on Burnable Absorber in a Long-Life Maritime Molten Salt Fast Reactor Using Chloride-Fluoride Hybrid Salt", Trans. KNS Spring Meeting, Jeju, 2025-05-22~23. https://www.kns.org/files/pre_paper/53/25S-681-이영준.pdf
- 파일: `lee2025_kns_maritime_msfr_ba` (PDF 없음)
- 한 줄 요약: 장수명 해양 MSFR(염화물-불화물 혼합염)의 가연성 흡수체 타당성 연구입니다.
- 프로젝트와의 관계: spec의 반사체 두께, 내부 배리어, 평균 연료염 온도가 MARINA 공개값이 아니라 이 연구의 설정값이라는 근거입니다.

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| MgO 반사체 60 cm, SS316 8 mm, Inconel 625 0.8 mm, 25 EFPY | KAIST 해양 MSFR 설정 | §2.2 |
| 900 K isothermal | KCl-UCl3-UF4 혼합염 | §2.1 |
| B4C 드럼 7개(5 cm B4C, B-10 90%) | | §3.3 |
| HALEU 12.35 t, 활성과 비활성 염 각각 2.06 m3, 25 EFPY에서 73.90 MWd/kgU | | Table III |

- 우리와 다른 점: 조성이 다른 혼합염이고 MARINA가 아닙니다.
- 확인 못 한 것: 해당 없음.

### 6.18 Kang, Lee (2024) KNS 춘계 24S-619 　검증: verified

- 서지: Moon Hyeok Kang, Jeong Ik Lee (KAIST), "Multiphase Sloshing Dynamics of Water and Molten Salt in Drain Tanks using OpenFOAM", Trans. KNS Spring Meeting, Jeju, 2024-05-09~10. https://www.kns.org/files/pre_paper/51/24S-619-강문혁.pdf
- 파일: `kang2024_kns_drain_sloshing` (PDF 없음)
- 한 줄 요약: 배수탱크 슬로싱 해석입니다.
- 프로젝트와의 관계: 국내 해양 MSR 연구도 정량 경사각을 쓰지 않는다는 확인입니다(유정의 선체 운동 조건 참고).
- 쓸 수 있는 수치: 없음. 해양 운전 환경을 배수탱크 설계에 고려해야 한다는 서술만 있고 롤, 피치 수치나 IACS, IMO 기준 인용은 없습니다.
- 우리와 다른 점: 해당 없음.
- 확인 못 한 것: 해당 없음.

### 6.19 Go, Yoon, Zee, Park (2024) KNS 춘계 24S-182 　검증: verified

- 서지: Yubin Go, Seong Jun Yoon, Sung-Kyun Zee, Tongkyu Park (FNC Technology), "A study of long-term cycle and sensitivity evaluation with NaCl-KCl-UCl3 fueled MSR core design", Trans. KNS Spring Meeting, Jeju, 2024-05-09~10. https://www.kns.org/files/pre_paper/51/24S-182-고유빈.pdf
- 파일: `go2024_kns_fnc_msr_cycle` (PDF 없음)
- 한 줄 요약: KAERI 조성 연료염을 쓴 FNC 노심의 장기 주기 연구입니다.
- 프로젝트와의 관계: spec 노심 묶음의 비교값입니다.

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| BeO 반사체 95~100 cm | FNC 노심 | Table 1, 5 |
| 농축도 19.75 w/o | | Table 1 |

- 우리와 다른 점: FNC 연구 노심입니다.
- 확인 못 한 것: 목표 운전기간 설정값의 위치.

### 6.20 Yoon et al. (2025) KNS 춘계 25S-390 　검증: verified

- 서지: Seong Jun Yoon et al. (FNC Technology), "Long-term Control of Excess Reactivity in Molten Salt Fast Reactors Using Pebble-type Burnable Poisons", Trans. KNS Spring Meeting, 2025-05-22~23. https://www.kns.org/files/pre_paper/53/25S-390-윤성준.pdf
- 파일: `yoon2025_kns_fnc_pebble_bp` (PDF 없음)
- 한 줄 요약: 페블형 가연성 독물질로 MSFR 잉여반응도를 제어하는 연구입니다.
- 프로젝트와의 관계: spec No.26의 반구형 노심이 이 연구 노심과 닮았다는 비교입니다.

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| 운전 28년, 노심 "Cylinder with hemispherical caps" | FNC 노심 | §2.1, Fig. 1 |

- 우리와 다른 점: MARINA 자료가 아닙니다.
- 확인 못 한 것: BeO 두께 값의 위치.

### 6.21 Go et al. (2025) KNS 춘계 25S-388 　검증: verified

- 서지: Yubin Go et al. (FNC Technology), "Core Design of Molten Salt Fast Reactor using PbO Reflector and Cycle Study", Trans. KNS Spring Meeting, 2025-05-22~23. https://www.kns.org/files/pre_paper/53/25S-388-고유빈.pdf
- 파일: `go2025_kns_fnc_pbo_reflector` (PDF 없음)
- 한 줄 요약: PbO 반사체 MSFR 노심 설계입니다.
- 프로젝트와의 관계: spec No.28의 대안 재질(PbO) 비교값입니다.

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| PbO 반사체 35 cm | FNC 노심 | Table 1 |

- 우리와 다른 점: MARINA 자료가 아닙니다.
- 확인 못 한 것: 해당 없음.

### 6.22 Chung, Yoon, Kim, Lee (2025) KNS 추계 25A-178 　검증: verified

- 서지: Hyunjun Chung, Jungbin Yoon, Serin Kim, Yoonhee Lee (전북대), "Preliminary Analysis of the Sensitivity of Neutronic Performance in a TRU-Loaded Molten Salt Fast Reactor Core for Marine Propulsion", Trans. KNS Autumn Meeting, Changwon, 2025-10-30~31. https://www.kns.org/files/pre_paper/54/25A-178-이윤희.pdf
- 파일: `chung2025_kns_tru_msfr` (PDF 없음)
- 한 줄 요약: TRU 장전 해양 추진 MSFR 노심의 민감도 예비 해석입니다.
- 프로젝트와의 관계: spec 유도 시트의 Cl-37 농축도 가정이 공개 연구와 다르다는 근거입니다.

쓸 수 있는 수치

| 값 | 조건 | 위치 |
|---|---|---|
| PbO 반사체 69.12 cm | | Table 1 |

- 우리와 다른 점: MARINA 자료가 아닙니다.
- 확인 못 한 것: Cl-37 농축도, 목표 운전기간, 농축도 설정값의 위치(원자료에 값은 있으나 위치 없음).

### 6.23 Yoon et al. (2026) KNS 춘계 26S-382 　검증: verified

- 서지: Jungbin Yoon et al. (KENTECH, 전북대), "Feasibility Study on Mitigation of Reactivity Swing via Utilization of Spent Fuel Rods with Molten Salt Fast Reactor Cores for Maritime Propulsion System", Trans. KNS Spring Meeting, Jeju, 2026-05-07~08. https://www.kns.org/files/pre_paper/55/26S-382-이윤희.pdf
- 파일: `yoon2026_kns_spent_fuel_msfr` (PDF 없음)
- 한 줄 요약: 사용후연료봉으로 해양 추진 MSFR의 반응도 변동을 줄이는 타당성 연구입니다.
- 프로젝트와의 관계: KAERI 조성 연료염을 쓰는 연구의 하나입니다(§2.1).
- 쓸 수 있는 수치: 없음(목표 운전기간과 농축도 값은 원자료에 위치 없음).
- 우리와 다른 점: MARINA 자료가 아닙니다.
- 확인 못 한 것: 해당 값의 위치.

### 6.24 Kim, Jo, Cho (2026) KNS 춘계 26S-654 　검증: verified

- 서지: HyeonJun Kim, SeungJae Jo, Jaehyun Cho (중앙대), "Radiation Dose Evaluation for Crew members in Nuclear-Powered Ship under Severe Shield Degradation Scenarios", Trans. KNS Spring Meeting, Jeju, 2026-05-07~08. https://www.kns.org/files/pre_paper/55/26S-654-김현준.pdf
- 파일: `kim2026_kns_crew_dose` (PDF 없음)
- 한 줄 요약: 차폐 열화 시나리오에서 원자력 선박 승조원 피폭 평가입니다.
- 프로젝트와의 관계: K-MSR을 제3자가 어떻게 가정하는지의 사례입니다. 서현(차폐)에게 참고가 될 수 있습니다.
- 쓸 수 있는 수치: 없음. 열출력, 선박 크기, 속력 가정이 있으나 원자료에 위치가 없고 논문 안 근거도 확인하지 못했습니다.
- 우리와 다른 점: 승조원 피폭이 대상입니다.
- 확인 못 한 것: 가정값의 위치와 근거.

### 6.25 Kim, Kim (2025) KNS 추계 25A-317 　검증: verified

- 서지: Inyup Kim, Yonghee Kim (KAIST), "iMC-OpenFOAM Coupled Analysis of Passively-Cooled Molten Salt Fast Reactor", Trans. KNS Autumn Meeting, Changwon, 2025-10-30~31. https://www.kns.org/files/pre_paper/54/25A-317-김인엽.pdf
- 파일: `kim2025_kns_imc_openfoam` (PDF 없음)
- 한 줄 요약: 피동 냉각 MSFR의 결합 해석입니다.
- 프로젝트와의 관계: 농축도 표기를 확인한 연구의 하나입니다.
- 쓸 수 있는 수치: 없음(농축도 값은 원자료에 위치 없음).
- 우리와 다른 점: MARINA 자료가 아닙니다.
- 확인 못 한 것: 해당 값의 위치.

### 6.26 KNS 2026 춘계 Q워크숍 게시물 (김화평, 센추리) 　검증: verified (게시물). 발표자료 본문 미열람

- 서지: 「[26춘계] Q워크숍 해양용 용융염원자로(MARINA) 국내 개발 현황」, 한국원자력학회 게시물 103223, 워크숍 2026-05-06, 게시 2026-05-11. 발표: 박동규((주)미래와도전, 노심설계 전산코드 개발 현황), 김화평(센추리, MARINA MSR 및 Off-gas System 개발 현황). 첨부 download/33843(박동규), download/33844(김화평). https://www.kns.org/boards/view/confNotice/103223
- 파일: `kim2026_kns_qworkshop_marina_offgas` (PDF 없음)
- 한 줄 요약: MARINA 오프가스 계통 개발 현황 발표가 있었다는 학회 게시물입니다. 유정의 입력(2026-10-06)이 이 게시물을 가리켰습니다.
- 프로젝트와의 관계: spec No.3의 "센추리(오프가스 계통 발표)"에 공개 근거가 생겼습니다. 2026-10-06 보고서와 이전 원자료 노트의 "센추리 발표 미발견"은 이로써 정정됩니다. 베드 사양(이중베드 여부, 크기, He 유량, 재생 대 교체)이 담겼을 가능성이 가장 큰 공개 자료라 정현, 유정, 재은 모두에게 중요합니다.
- 쓸 수 있는 수치: 없음. 첨부 33844는 바이너리로 나와 읽지 못했고 게시물에는 "공개 허용된 발표자료만 게시"라는 안내만 있으며 초록이 없습니다.
- 우리와 다른 점: 해당 없음.
- 확인 못 한 것: 발표자료 본문 전체, 발표 제목의 정확한 문구(요약 도구가 "MIRINA"로 표기해 오타 가능성). 팀원이 브라우저로 직접 내려받아 확인할 것을 권합니다(`00_확인필요_목록.md`).

### 6.27 한국항공대 연구처 게시 공고 (2023-04-05) 　검증: partial (원 공고는 과기정통부와 해수부)

- 서지: 「2023년도 용융염원자로(MSR) 원천기술개발사업 신규과제(해양용 MSR 안전성 기술 개발) 공모」, 한국항공대 연구처 게시, 2023-04-05. https://research.kau.ac.kr/info/info_021.php?searchkey=&searchvalue=&code=s2201&page=2&selcode=118&mode=read&seq=40760
- 파일: `kau2023_msr_call_notice` (PDF 없음)
- 한 줄 요약: 원천기술개발사업 신규과제 공모 게시입니다.
- 프로젝트와의 관계: spec No.4의 공동 사업 구조 보조 근거입니다.
- 쓸 수 있는 수치: 없음. 과기정통부와 해수부 공동 사업, 5개 분야(노심, 연료와 재료, 계통, 안전성, 해양 적용)라는 정성 사실만 있습니다(게시 본문).
- 우리와 다른 점: 해당 없음.
- 확인 못 한 것: 해수부 원문 공고(접속 시간 초과).

### 6.28 서지 미확인 후보: KAIST 학술지 2편 　검증: unverified (검색 결과 목록만)

spec 노심 묶음(No.19, 29~31, 43~46, 48)의 출처로 의심되는 논문이지만 ScienceDirect가 robots로 막혀 저자, 권호, 본문을 읽지 못했습니다. 쓸 수 있는 수치와 위치는 없습니다.

- "Conceptual core design study of a maritime molten salt fast reactor", Annals of Nuclear Energy (PII S0306454925003883). https://www.sciencedirect.com/science/article/abs/pii/S0306454925003883 . 파일: `kaist_ane_maritime_msfr_core` (PDF 없음)
- "Neutronic design implications of chlorine isotopic enrichment in moderating-reflector molten salt fast reactors", Nuclear Engineering and Technology (PII S1738573326004444). https://www.sciencedirect.com/science/article/pii/S1738573326004444 . 파일: `kaist_net_cl37_enrichment` (PDF 없음)

## 갈래 전체에서 확인 못 한 것

- 센추리 발표자료 본문(6.26). 이 노트에서 가장 먼저 닫아야 할 항목입니다.
- "MARINA = Marine Nuclear Reactor" 풀이, "사업단" 조직명, 운전압력, 반구형 노심과 다공판, Mg 환원제, BeO 물성, 제어드럼과 비상정지판의 MARINA 공개 근거.
- 선체 운동 조건과 경사 시 배수, 자연순환 성능 평가. MARINA 공개 자료에는 "원자로 중앙 배치"라는 정성 서술뿐입니다(`07_선박경사_기준.md`).
- 크레인 용량, 해치와 모듈 인출 경로, 원격 유지보수 범위.
- 원자료 노트가 "함께 볼 만한 것"으로 적은 Progress in Nuclear Energy 후보(PII S0149197025004895)와 SCOPE-2(2025-11-04) 확장초록은 서지 일부만 확인되어 문헌 목록에 넣지 않았습니다.
- ABS, LR 본사 원문 보도자료와 해수부 원문 공고.
