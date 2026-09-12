#!/usr/bin/env python3
"""Verify a delivery manifest without writing any input or result file."""
from pathlib import Path
import hashlib, json, sys
root=Path(__file__).resolve().parents[1]
items=json.loads((root/'MANIFEST.json').read_text(encoding='utf-8'))['files']
failed=[]
for item in items:
    p=root/item['path']
    if not p.is_file(): failed.append(item['path']+': missing'); continue
    b=p.read_bytes()
    if len(b)!=item['bytes'] or hashlib.sha256(b).hexdigest()!=item['sha256']:
        failed.append(item['path']+': hash mismatch')
print(json.dumps({'checked':len(items),'passed':not failed,'failures':failed},ensure_ascii=False))
sys.exit(1 if failed else 0)
