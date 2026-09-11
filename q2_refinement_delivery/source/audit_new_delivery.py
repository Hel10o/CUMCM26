"""Read-only provenance, artifact structure and postprocessing reproduction checks.
Does not repeat the accepted full-field PDE validation or edit result2.xlsx.
"""
import argparse,csv,hashlib,json,subprocess,sys,os,tempfile,zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
ROOT=Path(__file__).resolve().parents[1]

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def workbook_summary(p):
 ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
 with zipfile.ZipFile(p) as z:
  assert z.testzip() is None;ss=[]
  if 'xl/sharedStrings.xml' in z.namelist():
   for x in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',ns):ss.append(''.join(t.text or '' for t in x.iter('{'+ns['s']+'}t')))
  wb=ET.fromstring(z.read('xl/workbook.xml'));rels={x.attrib['Id']:x.attrib['Target'] for x in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))};out={}
  for sheet in wb.find('s:sheets',ns):
   target=rels[sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']]
   target=target.lstrip('/') if target.startswith('/') else 'xl/'+target
   sh=ET.fromstring(z.read(target));rows=sh.findall('s:sheetData/s:row',ns);selected={}
   for row in rows:
    if int(row.attrib['r']) not in (1,2,3,4,5,10801):continue
    for c in row.findall('s:c',ns):
     v=c.find('s:v',ns);typ=c.attrib.get('t');value=None
     if typ=='s':value=ss[int(v.text)]
     elif typ=='inlineStr':value=''.join(t.text or '' for t in c.findall('.//s:t',ns))
     elif v is not None:
      try:value=float(v.text)
      except ValueError:value=v.text
     selected[c.attrib['r']]=value
   out[sheet.attrib['name']]={'xml_rows':len(rows),'selected_cells':selected}
  return out

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--handoff',type=Path);a=p.parse_args()
 original_checks=None;workbooks={}
 if a.handoff:
  snap=json.loads((ROOT/'evidence/before_upload_hashes.json').read_text());changed=[]
  for rel,info in snap.items():
   f=a.handoff/rel
   if not f.is_file() or sha(f)!=info['sha256']:changed.append(rel)
  assert not changed
  original_checks={'registered_files':len(snap),'all_hashes_unchanged':True,'changed':changed}
  template=a.handoff/'q2_final_delivery/inputs/result2_template.xlsx'
  accepted=a.handoff/'q2_final_delivery/output/result2.xlsx'
  workbooks={'template':workbook_summary(template),'accepted_result2':workbook_summary(accepted),'accepted_result2_sha256':sha(accepted),'scope':'Structure and selected endpoints only; reuse local 2026-09-11 full 453600-value audit.'}
  assert set(workbooks['accepted_result2'])=={'温度','水分浓度'}
  for sheet in workbooks['accepted_result2'].values():assert sheet['xml_rows']==10801
 with tempfile.TemporaryDirectory(prefix='q2_postprocessing_') as td:
  cmd=[sys.executable,str(ROOT/'source/q2_mechanism.py'),'--out',td,'--no-figures']
  e={**os.environ,'OPENBLAS_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1','CUA_DD_PYTHON_TOOL_WARM_SPREADSHEET_RUNTIME':'0'}
  r=subprocess.run(cmd,capture_output=True,text=True,env=e);assert r.returncode==0,r.stderr
  c=np.load(ROOT/'data/mechanism_unrounded.npz');d=np.load(Path(td)/'data/mechanism_unrounded.npz')
  assert c.files==d.files;differences={}
  for k in c.files:
   assert np.array_equal(c[k],d[k],equal_nan=True),k
   differences[k]=0.
  csvs=['mechanism_timeseries.csv','mechanism_table.csv','interval_60s_contributions.csv','parameter_sensitivity_3h.csv','parameter_sensitivity_timeseries.csv','boundary_identifiability_diagnostic.csv','environment_original.csv']
  assert all(sha(ROOT/'data'/n)==sha(Path(td)/'data'/n) for n in csvs)
 # Copied scientific source hashes are checked against the actual remote identities.
 source=json.loads((ROOT/'evidence/source_identity.json').read_text());scientific=[]
 for x in source['checked_file_identities']:
  if x['remote_path'].startswith('q2_final_delivery/source/'):
   f=ROOT/'runtime/source'/Path(x['remote_path']).name
   assert sha(f)==x['sha256'];scientific.append(f.name)
 manifest=json.loads((ROOT/'figures/manifest.json').read_text())
 assert all((ROOT/'figures'/x).is_file() for x in manifest['files']) and manifest['pairs']==10
 report={'accepted_originals':original_checks,'postprocessor_fresh_directory_exitcode':r.returncode,
         'postprocessor_all_npz_arrays_identical':True,'postprocessor_csv_byte_identity':True,
         'scientific_sources_sha256_unchanged':scientific,'figure_pairs_exist':10,
         'scope':'No full 3h production rerun; mathematical baseline unchanged; no overwritten accepted outputs.',
         'workbooks':workbooks}
 dest=ROOT/'evidence/new_delivery_audit.json';dest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print('NEW DELIVERY AUDIT PASSED; originals unchanged:',original_checks)
if __name__=='__main__':main()
