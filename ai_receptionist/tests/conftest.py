import sys
from pathlib import Path

# Ensure the ai_receptionist package root is importable regardless of CWD
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
