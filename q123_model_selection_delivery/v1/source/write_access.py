from pathlib import Path
import json,hashlib,datetime,shutil
P=Path(__file__).resolve().parents[1];BASE='1feb7686a371179bc6f545217e229f388a9bc379';TASK='f5c06bb276062b52b61c092f16c436c9d971f4f9'
entries=[]
def add(path,sha,scope,commit=BASE):
 entries.append(dict(path=path,commit=commit,url=f'https://github.com/Hel10o/libai/blob/{commit}/{path}',method='GitHub.fetch_file connector',status='read_succeeded',git_blob_sha1_returned=sha,read_scope=scope,local_full_binary_sha256=None))
add('README.md','311c62dc8a119e1d63a550df2c029761e55038f8','full root README in overlapping line ranges; later first 8 lines rechecked for blob identity',TASK)
add('q123_model_selection_handoff/前三问二维与潜热影响评估及最终建模路线_Pro任务书.md','379212b98749d742a4420d53316f3fc3c75c2931','complete, lines1-65,65-130,130-end and overlapping earlier calls',TASK)
add('readable/README.md','c0c6ddfa5a08b8f9961be6f6924eae154e54cbd4','complete')
add('readable/QUALITY.md','29c9a22207711787316803dd7e7b078e0829c44f','complete')
add('readable/problem/fulltext.md','e97b7dabbd704ac4dfde3092467601546fe48c99','all four pages in overlapping chunks; equations crosschecked against actual source constants; PDF page images not downloaded')
add('q1_complete_delivery/q1_delivery/input/environment_extracted.csv','d55880786a62ff55933c045998a6a7de033b83c5','all 242 lines including header; locally reconstructed exact bytes and verified Git blob SHA1')
b=(P/'inputs/environment_extracted.csv').read_bytes();blob=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest();assert blob=='d55880786a62ff55933c045998a6a7de033b83c5'
entries[-1].update(local_path='inputs/environment_extracted.csv',local_full_binary_sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),local_git_blob_match=True)
add('q1_complete_delivery/q1_delivery/source/q1_solver.py','02adff297ad8256bac1c32afc155a34b8af3ecbd','lines1-155: parameters, OOXML/environment reader, radial FV and nonlinear water boundary')
add('q2_final_delivery/source/q2_core.py','1da48e84d908cbf4994e83bf79b4f07e17365813','lines1-150: properties, environment, radial fluxes/storage/boundary')
add('q2_final_delivery/source/q2_axisymmetric.py','3213312ba5fabd3dddd8e0a240cfc531737d91f1','complete returned source through solve_axisymmetric outputs')
add('review_q123_physics_20260911/q1_heat_scale.json','f2d1895d64353101135e556b7712900b130efb92','complete JSON')
add('q3_refinement_delivery/output/end_event.json','4dc7af9f4f93e0cdaec1d0a88a08979cb4b1f7ca','complete JSON')
add('q3_refinement_delivery/validation/geometry/historical_geometry_comparison.json','1e4d556136397ac6f7422cb39294c39c6fffc6a5','complete four-case historical JSON')
add('review_q123_physics_20260911/前三问现状与物理闭合审核.md',None,'read sections1-3.2; requested1-145 response truncated during moving-material discussion; NOT marked complete')
add('review_q3_20260911/model/model_review.md',None,'read sections1-4.2; requested1-100 response truncated near execution-time discussion; NOT marked complete')
add('readable/papers/adrover-2020/README.md','4e51f4d6c81c3a7eab909da0c42567570aacd674','complete')
for name,page,sha in [('adrover-2020','005','30ec0d21494dcec840d264fab4356915fc518062'),('adrover-2020','006','815843170be14962fc3da8e2b22e32afe769d2ed'),('da-silva-2014','003','cd59594ff06306c67fa8f315fc9639a8e4802e23'),('da-silva-2014','004','e8adb1c7bd58fcbc71966d293f0ed2c9e93953d8'),('da-silva-2014','005','a37c98eb5efe068f6c98395763da007c9ebbc0bc'),('chupawa-2022','003','afff0e7591f8677f367e30ad5dfc061e213b1190')]:
 add(f'readable/papers/{name}/pages/{page}.md',sha,'complete original-page extracted text; not a PDF-image visual audit')
fail=json.loads((P/'validation/access_initial.json').read_text())
web=[dict(url=u,status='primary HTML read',scope=s) for u,s in [('https://www.mdpi.com/2304-8158/9/11/1577','original paper nonisothermal model and appendix structure'),('https://www.sciencedirect.com/science/article/pii/S0260877414002118','original paper abstract; full methodological text read in repository pages'),('https://www.fao.org/4/X0490E/x0490e0k.htm','Annex3 equation3-1 latent heat'),('https://www.fao.org/4/X0490E/x0490e07.htm','equation11 saturated vapor pressure'),('https://handbook.ashrae.org/Handbooks/F17/IP/f17_ch01/f17_ch01_ip.aspx','humidity ratio and psychrometric definitions'),('https://handbook.ashrae.org/Handbooks/F21/SI/F21_Ch06/F21_Ch06_si.aspx','gas concentration transfer and Lewis relation, equations26 and39-46')]]
data=dict(repository='Hel10o/libai',baseline_commit=BASE,task_commit=TASK,main_resolution='Initial GitHub connector commits/main response resolved f5c06bb276062b52b61c092f16c436c9d971f4f9; subsequent task and README reads pinned to this commit.',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),offline_input_zip_received=False,offline_manifest_verified=False,entries=entries,web_reads=web,failed_access=[dict(method='container Python requests',raw_error=fail,record='validation/access_initial.json'),dict(method='container curl --resolve direct IP',record='validation/curl_direct.log',exit_code=7),dict(method='GitHub.fetch_file encoding=base64 for original XLSX',status='partial payloads obtained; local complete XLSX reconstruction not achieved; not used as numerical input',raw_partial_payloads='validation/access_failed_source_raw/',note='No invented HTTP failure code: connector text retrieval worked, binary transfer/reconstruction did not complete.')],uncompleted=['Independent original XLSX binary parsing','Frozen Q1/Q2/Q3 NPZ full-byte download and elementwise review','Original PDF page-image visual equation verification','Full reading of every old implementation, audit and paper file listed by task; actual partial ranges recorded rather than claimed complete','Experimental identification of water activity, partial enthalpies and material/gas resistances','Shrinking-domain Q4 or external airflow CFD','All official result1/2/3 workbooks and manuscript final layout, outside current primary scope'],evidence_separation='New PDE results, inherited JSON evidence, synthetic software probes, rejected/failed runs and unexecuted work are separately labelled. No old scalar partial-package calculation used as new physical evidence.')
(P/'source_access.json').write_text(json.dumps(data,indent=2,ensure_ascii=False))
raw=P/'validation/access_failed_source_raw';raw.mkdir(exist_ok=True)
for src in Path('/mnt/data/model_selection_work').glob('*'):
 if src.suffix in ['.b64','.txt']:shutil.copy2(src,raw/src.name)
print('verified input blob:',blob)
