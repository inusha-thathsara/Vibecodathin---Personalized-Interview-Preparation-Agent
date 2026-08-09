import sys
from pathlib import Path

# Add root directory to python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app
