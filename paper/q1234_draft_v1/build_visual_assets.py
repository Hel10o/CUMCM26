"""Build the six revised figures, exclusively from frozen repository evidence."""
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
for group in ('process','geometry','validation'):
    subprocess.run([sys.executable,'-X','utf8',str(HERE/'visual_revision'/f'{group}.py')],check=True,cwd=HERE)
