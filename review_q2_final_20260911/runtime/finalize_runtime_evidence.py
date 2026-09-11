"""Package text-only runtime review and smoke-test the independent installer."""
import difflib, hashlib, json, subprocess, sys, tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
PROJECT=HERE.parents[1]

def main():
    original=PROJECT/'q2_refinement_delivery/runtime/source/q2_run_guard.py'
    fixed=HERE/'overlay/source/q2_run_guard.py'
    diff=''.join(difflib.unified_diff(original.read_text(encoding='utf-8').splitlines(True),fixed.read_text(encoding='utf-8').splitlines(True),
        fromfile='runtime/source/q2_run_guard.py (original Pro)',tofile='runtime/source/q2_run_guard.py (reviewed overlay)'))
    (HERE/'q2_run_guard.patch').write_text(diff,encoding='utf-8')
    with tempfile.TemporaryDirectory(prefix='q2_verified_installer_') as td:
        target=Path(td)/'verified_runtime'
        command=[sys.executable,'-X','utf8','-B',str(HERE/'install_verified_runtime.py'),'--destination',str(target)]
        install=subprocess.run(command,capture_output=True,text=True,encoding='utf-8')
        assert install.returncode==0,install.stderr
        help_run=subprocess.run([sys.executable,'-X','utf8','-B',str(target/'run_all.py'),'--help'],capture_output=True,text=True,encoding='utf-8')
        assert help_run.returncode==0,help_run.stderr
        duplicate=subprocess.run(command,capture_output=True,text=True,encoding='utf-8')
        assert duplicate.returncode!=0 and 'Existing destination refused' in duplicate.stderr
        proof=json.loads((target/'VERIFIED_RUNTIME_PROVENANCE.json').read_text(encoding='utf-8'))
        proof.update(installer_exit_code=install.returncode,cli_help_exit_code=help_run.returncode,existing_destination_refused=True,
            scientific_modules_unchanged=len(proof['unchanged_scientific_source']),scope='Temporary independent installation and --help only; no numerical solve started.')
        (HERE/'installer_smoke.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf-8')
        (HERE/'installer_smoke.log').write_text(install.stdout+'\nCLI HELP:\n'+help_run.stdout+'\nEXPECTED DUPLICATE REFUSAL:\n'+duplicate.stderr,encoding='utf-8')
    print('Installer and existing-destination protection smoke checks passed; patch generated.')

if __name__=='__main__':main()
