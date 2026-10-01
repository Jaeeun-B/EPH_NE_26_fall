"""스크립트에서 저장소 루트의 datraj 패키지를 불러오기 위한 경로 설정."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
