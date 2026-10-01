"""환경 점검: 필요한 패키지와 버전, PyBullet 데이터, TOPP-RA 사용 가능 여부.

실행: python scripts/00_check_env.py
"""
import importlib
import platform
import sys

REQUIRED = ["numpy", "scipy", "matplotlib", "pybullet", "pybullet_data", "openpyxl"]
OPTIONAL = ["toppra"]


def ver(mod):
    m = importlib.import_module(mod)
    return getattr(m, "__version__", "설치됨")


def main():
    print(f"Python {sys.version.split()[0]} ({platform.machine()}, {platform.system()})")
    ok = True
    for m in REQUIRED:
        try:
            print(f"  [ok] {m:14s} {ver(m)}")
        except Exception as e:  # noqa: BLE001
            ok = False
            print(f"  [없음] {m:12s} -> 설치 필요 ({e.__class__.__name__})")
    for m in OPTIONAL:
        try:
            importlib.import_module(m)
            print(f"  [ok] {m:14s} 설치됨")
        except Exception:  # noqa: BLE001
            print(f"  [선택] {m:12s} 없음 -> 시간 매개변수화는 대체 방식(quintic)으로 동작, 토크 제약은 사후 점검만")
    if ok:
        import os

        import pybullet as p
        import pybullet_data

        cid = p.connect(p.DIRECT)
        urdf = os.path.join(pybullet_data.getDataPath(), "kuka_iiwa", "model.urdf")
        rid = p.loadURDF(urdf, useFixedBase=True)
        print(f"  [ok] KUKA iiwa URDF 로드 (관절 {p.getNumJoints(rid)}개)")
        p.disconnect(cid)
        print("\n환경 준비 완료. 다음: python scripts/01_make_virtual_grids.py")
    else:
        print("\n빠진 패키지를 설치한 뒤 다시 실행하세요 (SETUP.md 3단계).")
        sys.exit(1)


if __name__ == "__main__":
    main()
