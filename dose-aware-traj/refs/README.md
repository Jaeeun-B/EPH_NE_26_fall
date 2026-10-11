# 참고문헌

PDF 원본은 이 폴더에 두되 **git에 올리지 않습니다.** 저작권이 있고 이 저장소는 공개입니다. `.gitignore`가 `refs/*.pdf`를 막고 있습니다.

커밋되는 것은 `refs/notes/`의 정리 노트뿐입니다. 노트에는 쪽 번호가 붙은 인용과 수치만 담고, 논문 전체를 옮겨 적지 않습니다.

## 쓰는 법

1. PDF를 `refs/`에 넣습니다. 파일명은 `저자연도_주제.pdf` 형식을 권합니다. 예: `kim2024_remote_maintenance.pdf`
2. Claude Code에서 "이 논문 정리해줘"라고 하면 `paper-reader` 에이전트가 읽고 `refs/notes/<파일명>.md`를 만듭니다
3. 아래 표에 한 줄 추가합니다

## 문헌 목록

| 파일 | 제목 | 쓰는 곳 | 노트 | 상태 | 서지 검증 |
|---|---|---|---|---|---|
| `zhang2020_radiation_tolerance_test` (PDF 없음) | Zhang, Hutson, Knighton, Herrmann, Scott (2020). Radiation Tolerance Testing Methodology of Robotic Manipulator Prior to Nuclear Waste Handling. Front. Robot. AI, 10.3389/frobt.2020.00006 | 원자력 원격조작, 선량 모델. 참고문헌 3 후보, 관절별 선량 구배 | `notes/01_선량인지_경로계획.md` | 정리 완료 | verified (본문) |
| `west2022_layered_costmaps` (PDF 없음) | West et al. (2022). Real-Time Avoidance of Ionising Radiation Using Layered Costmaps for Mobile Robots. Front. Robot. AI, 10.3389/frobt.2022.862067 | 경로계획, 선량 모델. 선량 = 경로 적분 정의 | `notes/01_선량인지_경로계획.md` | 읽는 중 | verified (본문). 식 번호는 요약 기준이라 재확인 필요 |
| `karamanlioglu2026_radiation_aware_path` (PDF 없음) | Karamanlıoğlu, Adar, Mısır, Ertekin (2026). Radiation-Aware Path Planning Framework for Mobile Robots in Dynamic Hazardous Environments. Sensors, 10.3390/s26154937 | 경로계획. 누적선량 비용항 선례 | `notes/01_선량인지_경로계획.md` | 참고만 | verified (초록) |
| `xiang2026_improved_astar_dwa` (PDF 없음) | Xiang, Zhou, Huo, Zhang, Zhang (2026). A Real-Time Path Planning Algorithm in Radiation Environments Based on an Improved A* Combined with the Dynamic Window Approach. Nucl. Sci. Eng. 200(10), 2302-2320, 10.1080/00295639.2025.2575538 | 경로계획. A*와 DWA에 선량 비용 결합 | `notes/01_선량인지_경로계획.md` | 참고만 | verified (초록) |
| `xiang2025_improved_aco` (PDF 없음) | Xiang, Zhou, Huo, Zhang, Gu (2025). A Dynamic Nuclear Radiation Environment Path Planning Method Based on an Improved Ant Colony Algorithm. Nucl. Technol. 211(11), 10.1080/00295450.2025.2457249 | 경로계획. 최소 누적선량 경로를 초기해로 사용 | `notes/01_선량인지_경로계획.md` | 참고만 | verified (초록) |
| `zhangde2023_multiobjective_aco` (PDF 없음) | Zhang De, Luo, Yin, Zou (2023). Multi-objective path planning for mobile robot in nuclear accident environment based on improved ant colony optimization with modified A*. Nucl. Eng. Technol. | 경로계획, 선량 모델. 몬테카를로 2층 비용 격자 | `notes/01_선량인지_경로계획.md` | 참고만 | verified (초록). 권, 쪽, DOI 미확인 |
| `yue2026_decommissioning_feasibility` (PDF 없음) | Yue, Tian, Wu, Liu, Su, Gu, Jiang (2026). A Path Planning Algorithm Considering the Feasibility Region of Nuclear Decommissioning Robots. Nucl. Sci. Eng. 200(5), 1250-1262, 10.1080/00295639.2025.2509471 | 경로계획. 해체 로봇 DC-A* | `notes/01_선량인지_경로계획.md` | 참고만 | verified (초록) |
| `zhangj2024_personnel_work_paths` (PDF 없음) | Zhang J., Chen, Ni, Zheng, Zhao, Tian, Jiang (2024). Optimization of Personnel Work Paths During Decommissioning of Nuclear Facilities. Nucl. Sci. Eng. 198(8), 1668-1681, 10.1080/00295639.2023.2257508 | 경로계획. 작업 순서를 TSP로 본 선량 최소화 | `notes/01_선량인지_경로계획.md` | 참고만 | verified (초록) |
| `adibeli2021_decommissioning_review` (PDF 없음) | Adibeli, Liu, Ayodeji, Awodi (2021). Path planning in nuclear facility decommissioning: Research status, challenges, and opportunities. Nucl. Eng. Technol. 53(11), 3505-3516, 10.1016/j.net.2021.05.038 | 경로계획. 리뷰, 문제 정의 인용 | `notes/01_선량인지_경로계획.md` | 읽는 중 | verified |
| `huang2023_uneven_terrain` (PDF 없음) | Huang, Shi, Zhou, et al. (2023). Autonomous navigation of mobile robot in radiation environment with uneven terrain. Int. J. Intell. Robot. Appl., 10.1007/s41315-022-00255-x | 경로계획. 방사선과 통과성 다층 costmap | `notes/01_선량인지_경로계획.md` | 참고만 | verified (초록). 공저자 전체 미확인 |
| `george2026_dose_aware_rrtstar_uuv` (PDF 없음) | George (2026). Dose Aware RRT* Path Planning Algorithm for UUV Inside Nuclear Spent Fuel and Reactor Pool. IEEE DataPort, 10.21227/d2a7-ex55 | 경로계획, 선량 모델. OpenMC 선량장과 RRT* 구성 참고 | `notes/01_선량인지_경로계획.md` | 참고만 | verified (데이터셋 페이지) |
| `zhangk2024_condition_awareness` (PDF 없음) | Zhang K. et al. (2024). Reinforced Safety-Related Condition Awareness in a Motion Planning System for Remote Manipulators in Nuclear Decommissioning. ICCRE 2024, 10.1109/ICCRE61448.2024.10589853 | 경로계획, 원자력 원격조작. 원격 매니퓰레이터의 방사선 노출 모니터링 | `notes/01_선량인지_경로계획.md` | 참고만 | verified (초록) |
| `zhangk2025_longreach_multiobjective` (PDF 없음) | Zhang K. et al. (2025). Experimental Tests of a Motion Planning System Based on Multi-Objective Optimisation for Nuclear Decommissioning Practice Using Long-Reach Systems. ERF 2024 vol. 2, 10.1007/978-3-031-76428-8_42 | 경로계획, 원자력 원격조작. 장거리 매니퓰레이터 다목적 계획 | `notes/01_선량인지_경로계획.md` | 참고만 | verified (초록). 선량 항 미확인 |
| `hu2025_fault_tolerant_astar` (PDF 없음) | Hu, Chen (2025). Application of improved A-star algorithm in fault-tolerant control of the robotic arm in the nuclear industry. Front. Mech. Eng., 10.3389/fmech.2025.1610923 | 경로계획, 원자력 원격조작. 방사선 유발 열화에 대한 결함허용 제어 | `notes/01_선량인지_경로계획.md` | 참고만 | verified (요약) |
| `noguchi2013_iter_maintenance_robot` (PDF 없음) | Noguchi et al. (2013). Irradiation test progress for the ITER maintenance robot. JAEA BB2013-1301 | 선량 모델(TID). 기계부 한계 상한 | `notes/02_부품_TID.md` | 정리 완료 | verified (Table 1). 보고서 번호는 페이지에 없음 |
| `coloma2023_radiation_trajectory_electronics` (PDF 없음) | Coloma et al. (2023). The effect of ionizing radiation on robotic trajectory movement and electronic components. Nucl. Eng. Technol., 10.1016/j.net.2023.07.041 | 선량 모델(TID). 제어 전자부 상한 후보, 납 차폐 효과 | `notes/02_부품_TID.md` | 정리 완료 | verified |
| `macha2025_lubricant_dose_review` (PDF 없음) | Macha, Senajova, Giles, Calviani, Girard, Ferrari (2025). Effects of Radiation Dose on Lubricants: A Review of Experimental Studies. ACS Appl. Mater. Interfaces, 10.1021/acsami.4c21220 | 선량 모델(TID). 윤활제 비제약 근거 | `notes/02_부품_TID.md` | 정리 완료 | verified |
| `goiffon2018_rad_hard_cmos_sensor` (PDF 없음) | Goiffon et al. (2018). Total Ionizing Dose Effects on a Radiation-Hardened CMOS Image Sensor Demonstrator for ITER Remote Handling. IEEE Trans. Nucl. Sci., 10.1109/TNS.2017.2765481 | 선량 모델(TID). 카메라 센서 상한 | `notes/02_부품_TID.md` | 참고만 | verified (초록만) |
| `mirion_sc985_camera_datasheet` (PDF 없음) | Mirion IST-Rees SC985 compact colour shielded camera module, 데이터시트 (날짜 미확인) | 선량 모델(TID). 카메라 상한 후보, 센서 교체 설계 | `notes/02_부품_TID.md` | 정리 완료 | verified (벤더 자료) |
| `todd_cern_radiation_risks` (PDF 없음) | Todd, Uznanski. Radiation Risks and Mitigation in Electronic Systems (CERN). arXiv:1607.01573 | 선량 모델(TID). 수명 선량 단일 요구 방식 비교 | `notes/02_부품_TID.md` | 읽는 중 | verified (제목, 저자). 연도 미확인 |
| `nancekievill2017_robot_tolerance_thesis` (PDF 없음) | Nancekievill (2017). The Radiation Tolerance and Development of Robotic Platforms for Nuclear Decommissioning. 박사논문, Univ. of Manchester | 선량 모델(TID). 연간 선량 기준 접근 | `notes/02_부품_TID.md` | 참고만 | verified (초록만) |
| `nagatani2012_fukushima_rescue_robots` (PDF 없음) | Nagatani, Kiribayashi, Okada et al. Emergency response to the nuclear accident at the Fukushima Daiichi Nuclear Power Plants using mobile rescue robots. J. Field Robotics, 10.1002/rob.21439 (West 2022가 인용한 값을 2차로만 확인) | 선량 모델(TID). 카메라와 라이다 보수적 기준(2차) | `notes/02_부품_TID.md` | 참고만 | partial (2차 인용). 연도 2011과 2012 혼재 |
| `neimag2020_resolve_optics` (PDF 없음) | NEI Magazine (2020-07-24). Resolve Optics supports visual inspection in nuclear environments | 선량 모델(TID). 렌즈 유리 갈변 | `notes/02_부품_TID.md` | 참고만 | verified (업계지, 벤더 주장) |
| `li2015_harmonic_drive_irradiation` (PDF 없음) | Li, Qiu, Zheng, Cao (2015). Testing of harmonic drive degrading under radiation environment. Int. J. Mechatron. Autom. 5(2/3) | 선량 모델(TID). 하모닉 드라이브 단시간 내성 | `notes/02_부품_TID.md` | 참고만 | verified (초록만) |
| `kurbanova2023_peek_ebeam` (PDF 없음) | Kurbanova et al. (2023). PEEK electron-beam study. Polymers, 10.3390/polym15061340 | 선량 모델(TID). PEEK 안정성 참고 | `notes/02_부품_TID.md` | 읽는 중 | verified |
| `iter_pdd_2_09_remote_handling` (PDF 없음) | ITER Plant Design Description 2.9 Remote Handling (ITER G A0 FDR 1 R1.0, 2001-07-13) | 원자력 원격조작, 선량 모델(TID). 내방사선성 근거 서술 | `notes/02_부품_TID.md` | 읽는 중 | verified (페이지 표기 기준) |
| `blumberg1968_ornl_tm0910_maintenance` (PDF 없음) | Blumberg, Hise (1968). MSRE Design and Operations Report, Part X: Maintenance Equipment and Procedures. ORNL-TM-0910 | 원자력 원격조작. 교체 철학, 차폐체, 장비 | `notes/03_원격유지보수_선박경사.md` | 읽는 중 | verified (표제, 저자, 날짜). 시리즈 표기 partial |
| `blumberg_ornl_tm1859_msbr_maintenance` (PDF 없음) | Blumberg. Maintenance Development for Molten-Salt Breeder Reactors. ORNL-TM-1859 | 원자력 원격조작. MSBR 보수가 MSRE 경험에 기반 | `notes/03_원격유지보수_선박경사.md` | 읽는 중 | partial (날짜 미확인) |
| `haubenreich1970_ornl_tm2974_postop` (PDF 없음) | Haubenreich, Richardson (1970). Plans for Post-Operation Examination of the Molten-Salt Reactor Experiment. ORNL-TM-2974 | 원자력 원격조작. 숯 베드 절단과 운반 계획 | `notes/03_원격유지보수_선박경사.md` | 읽는 중 | verified |
| `mcmillan2019_orssab_msre` (PDF 없음) | McMillan (2019). MSRE presentation, DOE ORSSAB, Nov 13, 2019 | 원자력 원격조작. 보조 숯 베드 오염 이력 | `notes/03_원격유지보수_선박경사.md` | 정리 완료 | verified |
| `cfr2024_46cfr58_01_40` (PDF 없음) | 46 CFR 58.01-40 Machinery inclination requirements (LII 텍스트) | 원자력 원격조작. 선박 경사 기준(프로젝트 선택 기준) | `notes/03_원격유지보수_선박경사.md` | 정리 완료 | verified (LII). eCFR 직접 열람 안 함 |
| `jang2025_kns_russian_register` (PDF 없음) | Jang (2025). A Study on the Revision of Korean Nuclear Regulation Guidelines under the Assuming the Introduction of nuclear ships: reference to Russian classification regulations. KNS 추계 | 원자력 원격조작. CFR보다 큰 대안 경사 포락선 | `notes/03_원격유지보수_선박경사.md` | 읽는 중 | verified (서지). 수치는 요약 기반 |
| `jung2022_kns_dynamic_motions` (PDF 없음) | Jung, Bang (2022). Preliminary Study on Single-phase Natural Circulation under Dynamic Motions in MARS-KS Code. KNS 추계 | 원자력 원격조작. 대표 해상 운동 값 | `notes/03_원격유지보수_선박경사.md` | 읽는 중 | verified |
| `zhang2018_floating_npp_safety` (PDF 없음) | Zhang, Buongiorno, Golay, Todreas (2018). Safety Analysis of a 300-MW(electric) Offshore Floating Nuclear Power Plant in Marine Environment. Nucl. Technol. | 원자력 원격조작. 부유식 원전 경사 사례 | `notes/03_원격유지보수_선박경사.md` | 참고만 | partial (권, 쪽 미확인) |
| `valiaveedu2025_nuclear_ship_handbook` (PDF 없음) | Valiaveedu, Edmonds, Izurieta (2025). Nuclear Ship Safety Handbook. MIT | 원자력 원격조작. 선박 원자로 안전 일반 | `notes/03_원격유지보수_선박경사.md` | 참고만 | verified (초록만) |
| `connell1975_marine_environment` (PDF 없음) | Connell (1975). Effect of Marine Environment on Nuclear Power Plant Design. IEEE Conf. on Engineering in the Ocean Environment | 원자력 원격조작. 선박 환경 설계 요인 열거 | `notes/03_원격유지보수_선박경사.md` | 참고만 | verified (기록만) |
| `jaea2023_mutsu_review` (PDF 없음) | JAEA-Review 2023-014. Operation Report on Review Results of the Nuclear Ship MUTSU | 원자력 원격조작. 선박 운동의 장비 영향 사례 | `notes/03_원격유지보수_선박경사.md` | 읽는 중 | verified (요약 수준) |
| `from_ship_motion_manipulator_planning` (PDF 없음) | From, Gravdahl, Abbeel. On the Influence of Ship Motion Prediction Accuracy on Motion Planning and Control of Robotic Manipulators on Seaborne Platforms (ICRA, 연도 미표기) | 경로계획, 동역학. 선상 매니퓰레이터 계획, 토크 저감 비용항 | `notes/03_원격유지보수_선박경사.md` | 읽는 중 | partial (연도, 매체 미표기) |
| `ans2020_51_10_afw` (PDF 없음) | ANSI/ANS-51.10-2020. Auxiliary Feedwater System for Pressurized Water Reactors | 원자력 원격조작. 해당 없음 확인용 | `notes/03_원격유지보수_선박경사.md` | 참고만 | verified |
| `ribeiro2011_iter_remote_handling` (PDF 없음) | Ribeiro, Damiani, Tesini, Kakudate, Siuko, Neri (2011). The remote handling systems for ITER. Fusion Eng. Des. 86(6-8), 471-477, 10.1016/j.fusengdes.2011.01.138 | 원자력 원격조작. 차폐와 조작 장치 분리 사례 | `notes/03_원격유지보수_선박경사.md` | 참고만 | verified (VTT 기록). 수치는 unverified |
| `okuzumi2024_fukushima_robotics_irid` (PDF 없음) | Okuzumi, Matsuzaki, Okada (2024). Development and Application of Robotics for Decommissioning of Fukushima Daiichi NPS by IRID. J. Robot. Mechatron. 36(1), 9-20, 10.20965/jrm.2024.p0009 | 원자력 원격조작. 후쿠시마 로봇 분류 | `notes/03_원격유지보수_선박경사.md` | 참고만 | verified |
| `pham2018_toppra` (PDF 없음) | Pham, Pham (2018). A New Approach to Time-Optimal Path Parameterization Based on Reachability Analysis. arXiv:1707.07239, IEEE Trans. Robot. 34(3), 645-659 | 동역학. 시간 배정(B0, B1) | `notes/04_궤적최적화_방법론.md` | 읽는 중 | partial (IEEE DOI 미확인) |
| `bobrow1985_time_optimal_control` (PDF 없음) | Bobrow, Dubowsky, Gibson. Time-Optimal Control of Robotic Manipulators Along Specified Paths. IJRR, 10.1177/027836498500400301 | 동역학. 고전 TOPP | `notes/04_궤적최적화_방법론.md` | 참고만 | partial (연도 1985는 DOI 인코딩 기준, 권호쪽 미확인) |
| `shin1985_minimum_time_control` (PDF 없음) | Shin, McKay (1985). Minimum-Time Control of Robotic Manipulators with Geometric Path Constraints. IEEE Trans. Autom. Control AC-30(6) | 동역학. 고전 TOPP | `notes/04_궤적최적화_방법론.md` | 읽는 중 | partial (쪽수 531-540 대 531-541 상충, DOI 미확인) |
| `debrouwere2013_convex_concave_topp` (PDF 없음) | Debrouwere et al. (2013). Time-optimal path following for robots with convex-concave constraints using sequential convex programming. IEEE Trans. Robot. 29(6), 1485-1495, 10.1109/TRO.2013.2277565 | 동역학. 볼록 TOPP의 한계 | `notes/04_궤적최적화_방법론.md` | 참고만 | verified |
| `kuffner2000_rrt_connect` (PDF 없음) | Kuffner, LaValle (2000). RRT-Connect: An Efficient Approach to Single-Query Path Planning. ICRA 2000, vol. 2, 995-1001 | 경로계획. 기하 경로 생성(B0) | `notes/04_궤적최적화_방법론.md` | 참고만 | verified (DOI 제외) |
| `karaman2011_rrtstar` (PDF 없음) | Karaman, Frazzoli. Sampling-based Algorithms for Optimal Motion Planning. arXiv:1105.1186, IJRR | 경로계획. 점근 최적 비교 대상 | `notes/04_궤적최적화_방법론.md` | 참고만 | verified (arXiv). IJRR 권쪽 unverified |
| `hart1968_astar` (PDF 없음) | Hart, Nilsson, Raphael (1968). A Formal Basis for the Heuristic Determination of Minimum Cost Paths. IEEE Trans. Syst. Sci. Cybern. 4(2), 100-107 | 경로계획. A* 인용(B1) | `notes/04_궤적최적화_방법론.md` | 참고만 | verified (DOI 제외) |
| `ratliff2009_chomp` (PDF 없음) | Ratliff, Zucker, Bagnell, Srinivasa (2009). CHOMP: Gradient Optimization Techniques for Efficient Motion Planning. ICRA, 489-494 | 경로계획. 기울기 기반 궤적 최적화 | `notes/04_궤적최적화_방법론.md` | 참고만 | verified (DOI 제외) |
| `kalakrishnan2011_stomp` (PDF 없음) | Kalakrishnan, Chitta, Theodorou, Pastor, Schaal (2011). STOMP: Stochastic Trajectory Optimization for Motion Planning. ICRA | 경로계획. 기울기 없는 비용 설계 | `notes/04_궤적최적화_방법론.md` | 참고만 | partial (쪽수, DOI 미확인) |
| `schulman2014_trajopt` (PDF 없음) | Schulman et al. (2014). Motion Planning with Sequential Convex Optimization and Convex Collision Checking. IJRR 33(9), 1251-1270, 10.1177/0278364914528132 | 경로계획. 순차 볼록 최적화 | `notes/04_궤적최적화_방법론.md` | 참고만 | verified |
| `deb2002_nsga2` (PDF 없음) | Deb, Pratap, Agarwal, Meyarivan (2002). A fast and elitist multiobjective genetic algorithm: NSGA-II. IEEE Trans. Evol. Comput. 6(2), 182-197, 10.1109/4235.996017 | 경로계획. 다목적 최적화(선량, 시간, 토크) | `notes/04_궤적최적화_방법론.md` | 참고만 | verified |
| `coumans_pybullet` (PDF 없음) | Coumans, Bai (2016~2021). PyBullet, a Python module for physics simulation for games, robotics and machine learning. http://pybullet.org | 동역학. 시뮬레이터 인용 | `notes/04_궤적최적화_방법론.md` | 참고만 | verified |
| `gaz2019_panda_identification` (PDF 없음) | Gaz, Cognetti, Oliva, Robuffo Giordano, De Luca (2019). Dynamic Identification of the Franka Emika Panda Robot With Retrieval of Feasible Parameters Using Penalty-Based Optimization. IEEE RA-L 4, 4147-4154, 10.1109/LRA.2019.2931248 | 동역학. 동역학 식별의 물리적 일관성 | `notes/04_궤적최적화_방법론.md` | 참고만 | verified |
| `pfeiffer1987_trajectory_planning` (PDF 없음) | Pfeiffer, Johanni (1987). A concept for manipulator trajectory planning. IEEE J. Robot. Autom. | 동역학. 후보 | `notes/04_궤적최적화_방법론.md` | 참고만 | unverified (기억만) |
| `verscheure2009_convex_time_optimal` (PDF 없음) | Verscheure, Demeulenaere, Swevers, De Schutter, Diehl (2009). Time-optimal path tracking for robots: a convex optimization approach. IEEE Trans. Autom. Control | 동역학. 후보 | `notes/04_궤적최적화_방법론.md` | 참고만 | unverified (기억만) |
| `nakamura1987_task_priority` (PDF 없음) | Nakamura, Hanafusa, Yoshikawa (1987). Task-priority based redundancy control of robot manipulators. IJRR | 동역학. 영공간 후보 | `notes/04_궤적최적화_방법론.md` | 참고만 | unverified (기억만) |
| `siciliano1991_multiple_tasks` (PDF 없음) | Siciliano, Slotine (1991). A general framework for managing multiple tasks in highly redundant robotic systems. ICAR | 동역학. 영공간 후보 | `notes/04_궤적최적화_방법론.md` | 참고만 | unverified (기억만) |
| `chiaverini1997_singularity_robust` (PDF 없음) | Chiaverini (1997). Singularity-robust task-priority redundancy resolution for real-time kinematic control of robot manipulators. IEEE Trans. Robot. Autom. | 동역학. 영공간 후보 | `notes/04_궤적최적화_방법론.md` | 참고만 | unverified (기억만) |
| `haimes1971_epsilon_constraint` (PDF 없음) | Haimes (1971). 엡실론 제약법의 1차 문헌(서지 전체 미확인) | 경로계획. 다목적 도구 후보 | `notes/04_궤적최적화_방법론.md` | 참고만 | unverified (기억만) |
| `robertson_ornl_tm0728_msre_design` (PDF 없음) | Robertson. MSRE Design and Operations Report, Part I: Description of Reactor Design. ORNL-TM-0728 (연도 미확인, 약 1965 추정) | 선량 모델. 베드 형상, 질량, 설계 기준 | `notes/05_MSR_오프가스.md` | 정리 완료 | verified (본문, OCR 노이즈) |
| `ornl_tm0732_safety_analysis` (PDF 없음) | MSRE Design and Operations Report, Part V: Reactor Safety Analysis Report. ORNL-TM-0732 | 선량 모델. 보유일수, 희석 가정, 선량률 경험식 | `notes/05_MSR_오프가스.md` | 읽는 중 | verified (본문). 저자는 OCR 불완전 |
| `ornl4037_msr_semiannual_1966` (PDF 없음) | MSR Program Semiannual Progress Report, period ending Aug 31, 1966. ORNL-4037 | 선량 모델, 원자력 원격조작. 로봇이 다룰 만한 크기의 베드 선례 | `notes/05_MSR_오프가스.md` | 정리 완료 | verified (해당 절) |
| `adams1958_ornl_cf584_14_hrt` (PDF 없음) | Adams, Browning (1958). ORNL/CF-584-14 | 선량 모델. HRT 베드 비교 | `notes/05_MSR_오프가스.md` | 참고만 | partial (요약만) |
| `mcfarlane2019_offgas_volatility` (PDF 없음) | McFarlane et al. (2019). Fission Product Volatility and Off-Gas Systems for Molten Salt Reactors. ORNL/TM-2019/1266, PNNL-28974 | 선량 모델. 현대 MSR 오프가스 배경 | `notes/05_MSR_오프가스.md` | 참고만 | verified (서지, 요약) |
| `mcfarlane2020_offgas_engineering` (PDF 없음) | McFarlane et al. (2020). Molten Salt Reactor Engineering Study for Off-Gas Management. ORNL/TM-2020/1602, PNNL-30159 | 선량 모델. MSBR 오프가스 개략 | `notes/05_MSR_오프가스.md` | 참고만 | verified (요약) |
| `andrews2021_msr_offgas_review` (PDF 없음) | Andrews et al. (2021). Review of molten salt reactor off-gas management considerations. Nucl. Eng. Des. 385, 10.1016/j.nucengdes.2021.111529 | 선량 모델. 리뷰 인용 | `notes/05_MSR_오프가스.md` | 참고만 | verified (서지만) |
| `andrews_inl_gain_offgas_roadmap` (PDF 없음) | Andrews, McFarlane, Thallapally. MSR Integrated Off Gas Roadmap. INL GAIN 슬라이드 (무기재) | 선량 모델. 단수명 Xe 핵종 반감기 | `notes/05_MSR_오프가스.md` | 참고만 | verified (슬라이드) |
| `nndc2014_kr85_decay_data` (PDF 없음) | NNDC NuDat, Kr-85 decay data (Nucl. Data Sheets 116, 1, 2014) | 선량 모델. 선원항(Kr-85) | `notes/05_MSR_오프가스.md` | 정리 완료 | verified |
| `hubbell1995_nistir5632` (PDF 없음) | Hubbell, Seltzer (1995). Tables of X-Ray Mass Attenuation Coefficients and Mass Energy-Absorption Coefficients 1 keV to 20 MeV. NISTIR 5632 | 선량 모델. 질량감쇠계수 | `notes/05_MSR_오프가스.md` | 참고만 | verified |
| `nist_xcom` (PDF 없음) | NIST XCOM Photon Cross Sections Database | 선량 모델. 감쇠계수 계산 도구 | `notes/05_MSR_오프가스.md` | 참고만 | partial (페이지 존재만) |
| `shultis_faw_handbook_ch` (PDF 없음) | Shultis, Faw. Radiation Shielding and Radiological Protection. Handbook of Nuclear Engineering (Cacuci 편), Springer | 선량 모델. 점커널 이론 | `notes/05_MSR_오프가스.md` | 읽는 중 | partial (선원 방정식 못 찾음) |
| `shultis_faw2000_radiation_shielding` (PDF 없음) | Shultis, Faw (2000). Radiation Shielding. ANS | 선량 모델. 선원 적분과 빌드업 | `notes/05_MSR_오프가스.md` | 참고만 | unverified (기억만) |
| `ans1991_6_4_3_buildup` (PDF 없음) | ANSI/ANS-6.4.3 (1991). Gamma-Ray Attenuation Coefficients and Buildup Factors for Engineering Materials | 선량 모델. 빌드업 계수 | `notes/05_MSR_오프가스.md` | 참고만 | unverified (지정 번호와 연도 미확인) |

총 74건. 서지 검증은 verified 55건, partial 11건, unverified 8건입니다.

상태는 `읽는 중` / `정리 완료` / `참고만` 중 하나로 적습니다.

### 이 표를 읽는 법

- **PDF 없음**: 이 표는 PDF를 직접 읽은 결과가 아니라, 2026-10-06에 웹 페이지, 초록, 저장소 사본을 열어 본 조사 기록(연구 원자료 노트 5개와 보고서)에서 옮긴 것입니다. 파일명은 PDF를 받으면 쓸 이름으로 정한 임시 이름입니다. 연도를 모르는 문헌은 연도를 넣지 않았습니다.
- **상태**: `정리 완료`는 본문이나 표를 읽고 수치의 쪽/표/절 위치까지 확보한 것, `읽는 중`은 일부 절만 읽었거나 키워드 스캔 또는 요약에 의존해 PDF 재확인이 필요한 것, `참고만`은 초록, 서지 기록, 요약 페이지만 본 것(또는 기억에서 나온 후보)입니다.
- **서지 검증**: `verified`는 저자, 제목, 매체, 연도 같은 핵심 서지를 해당 페이지에서 직접 확인한 것(괄호는 남은 미확인 항목), `partial`은 일부 항목이 비었거나 2차 인용인 것, `unverified`는 검색 결과나 기억만 있어 인용 전에 반드시 서지를 확인해야 하는 것입니다. 서지 검증과 본문 읽기 수준은 별개입니다. verified여도 초록만 본 것이 많습니다.
- 갈래별 노트의 소절 순서는 이 표와 같고, 확인이 남은 항목은 `notes/00_확인필요_목록.md`에 모았습니다.

## 분류

이 프로젝트에서 참고문헌은 대체로 네 갈래입니다. 표의 "쓰는 곳"에 적어 두면 나중에 찾기 쉽습니다.

- **선량 모델**: 선량률 계산, 차폐, TID와 부품 내성
- **경로계획**: RRT 계열, STOMP, 선량 가중 계획, 다목적 최적화
- **동역학**: 매니퓰레이터 역동역학, 시간 최적 경로 파라미터화
- **원자력 원격조작**: 핫셀 작업, 원격 유지보수 사례, 해양 원자로

## 주의

- 노트에 쓰는 수치는 **반드시 쪽 번호를 답니다.** 쪽을 댈 수 없으면 적지 않습니다
- 논문의 결론을 이 프로젝트의 결론처럼 쓰지 마세요. 조건이 다릅니다. 노트의 "우리와 다른 점" 절에 차이를 적어 둡니다
