"""Xe 포집 이중베드: 선원항, 베드 크기, 모듈 차폐·질량 (config/xe_bed.json).

10/6 회의 결정(Xe 단일 타겟, 이중베드 유지)을 E 파트 계산에 넣기 위한 모듈이다.
값의 근거는 config/xe_bed.json에 적혀 있다. 여기서는 식만 구현한다.

단위: 시간 s(입력 편의상 d, h도 받음), 길이 m, 질량 kg, 방사능 Bq, 선량률 Gy/h.

물리 모델 요약
- 베드 재고 (MARINA spec 식): A_i = F·Y_i·ε·exp(-λ_i t_d)·(1 - exp(-λ_i T_on)), 교체 시점 A_i·exp(-λ_i t_c)
- 선원 세기 (Si 흡수선량률, 1 m, 점선원): S = Σ A·y·E·(μen/ρ)_Si / (4π) × 3600
  (공기 감쇠, 베드 자체차폐, 용기 감쇠 없음 → 상한)
- 지연(파과) 시간: t = f_dyn·K(T)·m / Q_act (Underhill 2003 식 2, 희박 Henry 영역)
- 차폐 투과: exp(-μ(E)·x) × buildup (기본 1, 좁은 빔)
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from . import config as _config

MEV_J = 1.602176634e-13
DAY = 86400.0


def load(path=None) -> dict:
    return _config.load_json(path or _config.CONFIG / "xe_bed.json")


# --------------------------------------------------------------------------- 선원항
def fission_rate(cfg: dict) -> float:
    st = cfg["source_term"]
    return st["P_th_MW"] * 1e6 / (st["E_f_MeV"] * MEV_J)


def bed_activity(cfg: dict, T_on_s: float, t_c_s: float = 0.0) -> dict[str, float]:
    """교체 시점 베드 재고 [Bq] (핵종별). T_on: 베드 운전시간, t_c: 격리 후 냉각시간."""
    st = cfg["source_term"]
    F = fission_rate(cfg)
    out = {}
    for n in st["nuclides"]:
        lam = math.log(2) / n["T_half_s"]
        R = F * n["yield_pct"] / 100 * st["eps"] * math.exp(-lam * st["t_d_h"] * 3600)
        out[n["id"]] = R * (1 - math.exp(-lam * T_on_s)) * math.exp(-lam * t_c_s)
    return out


def online_bed_activity(cfg: dict, t_online_s: float) -> dict[str, float]:
    """교체 중 운전을 이어가는 베드의 재고. 전환 후 t_online 동안 쌓인 양 (냉각 없음)."""
    return bed_activity(cfg, t_online_s, 0.0)


def _interp_loglog(E, Es, mus):
    return float(np.exp(np.interp(np.log(E), np.log(Es), np.log(mus))))


def mu_en_si(cfg: dict, E_MeV: float) -> float:
    a = cfg["attenuation_nist"]
    return _interp_loglog(E_MeV, a["energy_MeV"], a["Si_mu_en"])


def mu_mass(cfg: dict, material: str, E_MeV: float) -> float:
    """질량감쇠계수 μ/ρ [cm²/g]. K 흡수끝 양쪽을 따로 보간한다."""
    a = cfg["attenuation_nist"]
    Es = list(a["energy_MeV"])
    mus = list(a[f"{material}_mu"])
    edge = a[f"{material}_K_edge_MeV"]
    below = [(e, m) for e, m in zip(Es, mus) if e < edge] + [(edge, a[f"{material}_mu_below_edge"])]
    above = [(edge, a[f"{material}_mu_above_edge"])] + [(e, m) for e, m in zip(Es, mus) if e > edge]
    # 표의 흡수끝 바로 아래 칸(Pb 0.08 MeV 등)이 끝값보다 작은 에너지인지 확인
    seg = below if E_MeV < edge else above
    e_arr, m_arr = zip(*seg)
    return _interp_loglog(E_MeV, e_arr, m_arr)


def lines_of(cfg: dict) -> dict[str, list]:
    return {n["id"]: n["lines"] for n in cfg["source_term"]["nuclides"]}


def strength_si(cfg: dict, activity: dict[str, float], material: str | None = None,
                x_m: float = 0.0, buildup: float | None = None) -> float:
    """1 m 거리 Si 흡수선량률 [Gy/h]. material/x_m을 주면 차폐 투과를 곱한다."""
    B = cfg["module"]["buildup_factor"] if buildup is None else buildup
    rho = cfg["module"]["shield_materials"][material]["density_g_cm3"] if material else 0.0
    L = lines_of(cfg)
    s = 0.0
    for nid, A in activity.items():
        for E_keV, y in L[nid]:
            E = E_keV / 1000
            T = 1.0
            if material and x_m > 0:
                T = min(1.0, B * math.exp(-mu_mass(cfg, material, E) * rho * x_m * 100))
            s += A * y * E * MEV_J * mu_en_si(cfg, E) * 0.1 / (4 * math.pi) * 3600 * T
    return s


def strength_by_line(cfg: dict, activity: dict[str, float]) -> list[tuple[float, float]]:
    """(E [MeV], 1 m Si 선량률 기여 [Gy/h]) 목록. 차폐 두께를 바꿔가며 빠르게 계산할 때 쓴다."""
    L = lines_of(cfg)
    out = []
    for nid, A in activity.items():
        for E_keV, y in L[nid]:
            E = E_keV / 1000
            out.append((E, A * y * E * MEV_J * mu_en_si(cfg, E) * 0.1 / (4 * math.pi) * 3600))
    return out


def transmitted(cfg: dict, by_line, material: str, x_m: float) -> float:
    B = cfg["module"]["buildup_factor"]
    rho = cfg["module"]["shield_materials"][material]["density_g_cm3"]
    return sum(s * min(1.0, B * math.exp(-mu_mass(cfg, material, E) * rho * x_m * 100)) for E, s in by_line)


# --------------------------------------------------------------------------- 베드 크기
def K_xe(cfg: dict, T_C: float) -> float:
    """Henry 상수 [cm³/g, 기상 실부피 기준]. KAERI 25 °C 값에 Ackley-Browning 온도비를 곱한다."""
    sb = cfg["sorbent"]
    TR = lambda c: (c + 273.15) * 1.8  # noqa: E731
    return sb["K_ref_cm3_per_g"] * math.exp(5880 / TR(T_C) - 5880 / TR(sb["K_ref_T_C"]))


def q_actual_cm3_per_s(cfg: dict, T_C: float, P_bar: float) -> float:
    Q = cfg["sorbent"]["Q_He_STP_L_min"] * 1000 / 60
    return Q * (T_C + 273.15) / 273.15 * (1.01325 / P_bar)


def breakthrough_time_s(cfg: dict, m_kg: float, T_C: float = 25.0, P_bar: float = 1.0) -> float:
    sb = cfg["sorbent"]
    return sb["dynamic_fraction"] * K_xe(cfg, T_C) * m_kg * 1000 / q_actual_cm3_per_s(cfg, T_C, P_bar)


def sorbent_mass_kg(cfg: dict, T_on_s: float, T_C: float = 25.0, P_bar: float = 1.0) -> float:
    sb = cfg["sorbent"]
    return T_on_s * q_actual_cm3_per_s(cfg, T_C, P_bar) / (sb["dynamic_fraction"] * K_xe(cfg, T_C)) / 1000


@dataclass
class Module:
    m_sorbent: float
    D: float          # 흡착제 기둥 직경 [m]
    H: float          # 높이 [m]
    m_vessel: float
    x_shield: float   # 차폐 두께 [m]
    material: str
    m_shield: float

    @property
    def mass(self) -> float:
        return self.m_sorbent + self.m_vessel + self.m_shield


def build_module(cfg: dict, m_sorbent: float, material: str = "W", x_shield: float = 0.0) -> Module:
    md = cfg["module"]
    rho = cfg["sorbent"]["packing_density_g_cm3"] * 1000
    V = m_sorbent / rho
    a = md["aspect_H_over_D"]
    D = (4 * V / (math.pi * a)) ** (1 / 3)
    H = a * D
    tw, rv = md["vessel_wall_m"], md["vessel_density_kg_m3"]
    R = D / 2
    m_v = rv * (math.pi * ((R + tw) ** 2 - R ** 2) * H + 2 * math.pi * (R + tw) ** 2 * tw)
    Ro = R + tw
    rs = md["shield_materials"][material]["density_g_cm3"] * 1000
    m_s = rs * (math.pi * ((Ro + x_shield) ** 2 - Ro ** 2) * (H + 2 * tw) + 2 * math.pi * (Ro + x_shield) ** 2 * x_shield)
    return Module(m_sorbent, D, H, m_v, x_shield, material, m_s)


def solve_thickness(f, target: float, x_max: float = 0.2) -> float | None:
    """f(x)가 단조 감소할 때 f(x) <= target 인 최소 x. x_max 안에서 못 찾으면 None."""
    if f(0.0) <= target:
        return 0.0
    if f(x_max) > target:
        return None
    lo, hi = 0.0, x_max
    for _ in range(60):
        mid = (lo + hi) / 2
        if f(mid) <= target:
            hi = mid
        else:
            lo = mid
    return hi
