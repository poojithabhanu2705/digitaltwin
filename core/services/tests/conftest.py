import sys
from pathlib import Path

current = Path(__file__).resolve()
while current.parent != current:
    if (current / "pytest.ini").exists() or (current / "manage.py").exists():
        break
    current = current.parent

ROOT_DIR = current
for p in [ROOT_DIR / "core" / "services", ROOT_DIR / "core" / "repositories", ROOT_DIR]:
    p_str = str(p)
    if p_str not in sys.path:
        sys.path.insert(0, p_str)

def pytest_configure(config):
    for p in [ROOT_DIR / "core" / "services", ROOT_DIR / "core" / "repositories", ROOT_DIR]:
        p_str = str(p)
        if p_str not in sys.path:
            sys.path.insert(0, p_str)

