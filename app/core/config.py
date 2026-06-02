from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
REPORTS_DIR = PROJECT_ROOT / "reports"
BASELINES_DIR = PROJECT_ROOT / "baselines"
SAMPLES_DIR = PROJECT_ROOT / "samples"
DEFAULT_DB_PATH = DATA_DIR / "toolkit.sqlite3"


def ensure_runtime_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

