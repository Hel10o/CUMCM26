"""Redraw only the workflow with wider vertical spacing; no solver execution."""
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
subprocess.run([sys.executable, '-X', 'utf8', str(HERE / 'workflow_spacing/workflow.py')], cwd=HERE, check=True)
