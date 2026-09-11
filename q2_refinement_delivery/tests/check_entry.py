"""Scoped, reproducible CLI integration: tests stage only, then reuse/protection.
This does NOT run the full ten-stage second-question computation.
"""
import os,sys,subprocess,json,tempfile,shutil
from pathlib import Path

def main():
 b=Path(__file__).resolve().parents[1];r=b/'tests/results';r.mkdir(exist_ok=True)
 e={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','CUA_DD_PYTHON_TOOL_WARM_SPREADSHEET_RUNTIME':'0'}
 with tempfile.TemporaryDirectory(prefix='q2_entry_') as td:
  w=Path(td)/'managed_work'
  cmd=[sys.executable,str(b/'runtime/run_all.py'),'--out',str(w),'--stage','tests','--excel-engine','portable']
  first=subprocess.run(cmd,capture_output=True,text=True,env=e)
  (r/'entry_first.log').write_text(first.stdout+'\nSTDERR:\n'+first.stderr)
  assert first.returncode==0 and 'DONE tests' in first.stdout and 'COMPLETE: False' in first.stdout
  first_state=json.loads((w/'run_state.json').read_text())
  resume=subprocess.run(cmd+['--resume'],capture_output=True,text=True,env=e)
  assert resume.returncode==0 and 'REUSE VERIFIED tests' in resume.stdout and 'START tests' not in resume.stdout
  without=subprocess.run(cmd,capture_output=True,text=True,env=e)
  assert without.returncode!=0 and 'Nonempty output' in without.stderr
  protected=subprocess.run([sys.executable,str(b/'runtime/run_all.py'),'--out',str(b/'reused/q2_final_delivery/output'),'--stage','tests'],capture_output=True,text=True,env=e)
  assert protected.returncode!=0 and 'Protected' in protected.stderr
  (r/'entry_resume.log').write_text(resume.stdout+'\nSTDERR:\n'+resume.stderr)
  (r/'entry_refused.log').write_text(without.stderr+'\nPROTECTED:\n'+protected.stderr)
  shutil.copy2(w/'validation/unit_tests.json',r/'entry_unit_tests.json')
  shutil.copy2(w/'validation/geometry_unit_tests.json',r/'entry_geometry_unit_tests.json')
  state=json.loads((w/'run_state.json').read_text())
  report={'scope':'Actual patched CLI ran tests stage (not whole ten-stage pipeline), then legitimate resume and unsafe-output refusal.',
   'first_run_exitcode':first.returncode,'first_run_tests_stage_passed':state['stages']['tests']['passed'], 'complete_ten_stage_run':False,
   'resume_exitcode':resume.returncode,'resume_skipped_only_valid_stage':True,'nonempty_without_resume_rejected':True,
   'accepted_output_location_rejected':True,'unit_test_log_is_this_review':True,'tests_stage_elapsed_s':first_state['stages']['tests']['elapsed_s']}
  (r/'entry_integration.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
  print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
