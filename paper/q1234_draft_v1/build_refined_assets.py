"""Redraw four refined figures and the model workflow; no numerical solves."""
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
for group in ('process', 'geometry', 'workflow'):
    subprocess.run([sys.executable, '-X', 'utf8', str(HERE / 'visual_refinement' / f'{group}.py')], check=True, cwd=HERE)
