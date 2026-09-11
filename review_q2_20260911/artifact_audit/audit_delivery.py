"""Independent read-only Q2 artifact audit. Writes only beside this script.

Uses standard-library OOXML parsing and NumPy; never imports delivery code.
Run with: python audit_delivery.py [repository-root]
"""
from __future__ import annotations
import csv
import hashlib
import json
import math
from pathlib import Path
import posixpath
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime, timezone
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
REPO = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else HERE.parents[1]
DELIVERY = REPO / "q2_final_delivery"
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
CHECKS = []

def check(name, passed, details=None):
    CHECKS.append({"name": name, "passed": bool(passed), "details": details})

def hashes(path):
    b = path.read_bytes()
    return {"bytes": len(b), "sha256": hashlib.sha256(b).hexdigest(),
            "git_blob_sha1": hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()}

def read_json(rel):
    return json.loads((DELIVERY / rel).read_text(encoding="utf-8"))

def colnum(name):
    v = 0
    for c in name:
        v = 26*v + ord(c)-64
    return v

def address(s):
    m = re.fullmatch(r"([A-Z]+)([1-9][0-9]*)", s)
    return int(m[2]), colnum(m[1])

def read_xlsx(path):
    with zipfile.ZipFile(path) as z:
        crc = z.testzip()
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            shared = ["".join(si.itertext()) for si in ET.fromstring(z.read("xl/sharedStrings.xml"))]
        styles = ET.fromstring(z.read("xl/styles.xml"))
        formats = {int(x.attrib["numFmtId"]): x.attrib["formatCode"]
                   for x in styles.findall("m:numFmts/m:numFmt", NS)}
        xfs = [int(x.attrib["numFmtId"]) for x in styles.findall("m:cellXfs/m:xf", NS)]
        rels = {x.attrib["Id"]: x.attrib["Target"]
                for x in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
        sheets = []
        for sheet in ET.fromstring(z.read("xl/workbook.xml")).findall("m:sheets/m:sheet", NS):
            target = rels[sheet.attrib["{" + NS["r"] + "}id"]]
            target = target.lstrip("/") if target.startswith("/") else posixpath.normpath("xl/"+target)
            tree = ET.fromstring(z.read(target))
            cells = {}
            for c in tree.findall("m:sheetData/m:row/m:c", NS):
                typ = c.attrib.get("t", "n")
                v = c.find("m:v", NS)
                value = None if v is None else v.text
                if typ == "s":
                    value = shared[int(value)]
                elif typ == "inlineStr":
                    value = "".join(c.find("m:is", NS).itertext())
                elif typ == "n" and value is not None:
                    value = float(value)
                elif typ == "b":
                    value = bool(int(value))
                style = int(c.attrib.get("s", "0"))
                cells[c.attrib["r"]] = {"value": value, "type": typ, "style": style,
                    "format": formats.get(xfs[style], "builtin:"+str(xfs[style])),
                    "formula": c.find("m:f", NS) is not None}
            dim = tree.find("m:dimension", NS)
            sheets.append({"name": sheet.attrib["name"], "dimension": dim.attrib.get("ref") if dim is not None else None,
                           "cells": cells, "xml_path": target})
        return {"crc_error": crc, "sheets": sheets}

def rounded(a):
    return np.array([float(format(float(x), ".4f")) for x in a.ravel()]).reshape(a.shape)

def maxdiff(a,b):
    return float(np.max(np.abs(a-b)))

def nonfinite_json(x, where=""):
    found=[]
    if isinstance(x, float) and not math.isfinite(x): found.append(where)
    elif isinstance(x, dict):
        for k,v in x.items(): found.extend(nonfinite_json(v, where+"/"+k))
    elif isinstance(x, list):
        for k,v in enumerate(x): found.extend(nonfinite_json(v, where+"/"+str(k)))
    return found

def main():
    original_inputs=[]
    for item in read_json("evidence/input_hashes.json"):
        actual=hashes(DELIVERY/item["local_path"])
        original=hashes(REPO/item["repo_path"])
        rec={"repository_path": item["repo_path"], "delivery_path": item["local_path"],
             "actual": actual, "original": original,
             "matches_original": actual==original,
             "matches_record": all(actual[k]==item[k] for k in actual),
             "record_remote_blob_matches_bytes": item["remote_blob_sha1"]==actual["git_blob_sha1"]}
        original_inputs.append(rec)
        check("input "+item["local_path"], all(rec[k] for k in ["matches_original","matches_record","record_remote_blob_matches_bytes"]))

    wb_in=read_xlsx(DELIVERY/"inputs/附件1.xlsx")
    d=wb_in["sheets"][0]["cells"]
    env=np.array([[d[f"{c}{i}"]["value"] for c in "ABC"] for i in range(2,243)])
    input_schema={"sheets":[x["name"] for x in wb_in["sheets"]], "dimension":wb_in["sheets"][0]["dimension"],
                  "headings":[d[c+"1"]["value"] for c in "ABC"], "records":len(env),
                  "first_3h_records":int(np.sum(env[:,0]<=10800)),
                  "time_range_s":[float(env[0,0]),float(env[-1,0])],
                  "steps_s":np.unique(np.diff(env[:,0])).tolist(),
                  "temperature_minmax":[float(env[:,1].min()),float(env[:,1].max())],
                  "environmental_moisture_minmax":[float(env[:,2].min()),float(env[:,2].max())],
                  "last_record":env[-1].tolist()}
    check("input rows and time", len(env)==241 and np.array_equal(env[:,0],np.arange(0,14401,60)) and np.all(np.isfinite(env)), input_schema)
    input_record=read_json("output/input_audit.json")
    check("input audit values", all(input_record[k]==input_schema[k] for k in ["first_3h_records","temperature_minmax","environmental_moisture_minmax"]) and input_record["count"]==241)
    template=read_xlsx(DELIVERY/"inputs/result2_template.xlsx")
    template_schema=[{"name":s["name"],"dimension":s["dimension"],"cells":{k:v["value"] for k,v in s["cells"].items() if v["value"] is not None}} for s in template["sheets"]]

    raw_file=DELIVERY/"output/q2_unrounded.npz"
    with np.load(raw_file,allow_pickle=False) as z:
        raw={k:z[k].copy() for k in z.files}
    raw_schema={k:{"shape":list(v.shape),"dtype":str(v.dtype),"nonfinite":int(np.sum(~np.isfinite(v)))} for k,v in raw.items()}
    check("NPZ all fields finite",all(v["nonfinite"]==0 for v in raw_schema.values()),raw_schema)
    check("NPZ time",np.array_equal(raw["time_s"],np.arange(10801)))
    check("NPZ radius",np.allclose(raw["radius_cm"],np.arange(21)/10,rtol=0,atol=5e-16))
    expected_env=np.column_stack([np.interp(raw["time_s"],env[:,0],env[:,j]) for j in [1,2]])
    check("NPZ environment from original piecewise linear input",maxdiff(raw["environment"],expected_env)<1e-12,{"max_abs":maxdiff(raw["environment"],expected_env)})

    workbook=read_xlsx(DELIVERY/"output/result2.xlsx")
    check("XLSX CRC",workbook["crc_error"] is None)
    check("XLSX sheet names preserve template",[s["name"] for s in workbook["sheets"]]==[s["name"] for s in template["sheets"]])
    fields=["temperature_degC","moisture_dry_basis"]
    workbook_summary=[]
    table_summary=[]
    paper=(DELIVERY/"output/第二问论文正文.md").read_text(encoding="utf-8")
    for s,key,table_name,section in zip(workbook["sheets"],fields,["temperature","moisture"],["### 表3","### 表4"]):
        cells=s["cells"]
        grid=np.full((10801,22),np.nan)
        result_cells=[]
        unexpected=[]
        for addr,c in cells.items():
            r,col=address(addr)
            if r>10801 or col>22: unexpected.append(addr);continue
            if isinstance(c["value"], (float,int)) and not isinstance(c["value"],bool):grid[r-1,col-1]=c["value"]
            if r>=2 and col>=2:result_cells.append(c)
        a=grid[1:,1:]
        expected=rounded(raw[key][1:])
        rs={"sheet":s["name"],"dimension_tag":s["dimension"],"actual_last_cell":"V10801",
            "nonempty_cells":sum(c["value"] is not None for c in cells.values()),
            "result_values":len(result_cells),"unexpected_cells":unexpected,
            "nonfinite_results":int(np.sum(~np.isfinite(a))),
            "non_numeric_results":sum(c["type"]!="n" for c in result_cells),
            "formula_count":sum(c["formula"] for c in cells.values()),
            "incorrect_decimal_formats":sum(c["format"]!="0.0000" for c in result_cells),
            "rounded_NPZ_mismatches":int(np.sum(a!=expected)),
            "max_rounding_error":maxdiff(a,raw[key][1:]),
            "A1":cells["A1"]["value"],"first_row":a[0].tolist(),"last_row":a[-1].tolist()}
        workbook_summary.append(rs)
        check("XLSX extent "+key,not unexpected and len(result_cells)==226800 and rs["nonempty_cells"]==237622)
        check("XLSX axis values "+key,np.array_equal(grid[1:,0],np.arange(1,10801)) and np.allclose(grid[0,1:],np.arange(21)/10,atol=5e-16,rtol=0))
        check("XLSX values and format "+key,all(rs[k]==0 for k in ["nonfinite_results","non_numeric_results","formula_count","incorrect_decimal_formats","rounded_NPZ_mismatches"]),rs)
        check("NPZ field shape and initial "+key,raw[key].shape==(10801,21) and np.all(raw[key][0]==(28. if key==fields[0] else 2.55)))
        csv_path=DELIVERY/("output/"+key+"_unrounded.csv")
        csv_raw=np.loadtxt(csv_path,delimiter=",",skiprows=1)
        check("full CSV "+key,csv_raw.shape==(10801,22) and np.array_equal(csv_raw[:,0],raw["time_s"]) and np.array_equal(csv_raw[:,1:],raw[key]),{"shape":list(csv_raw.shape),"max_abs":maxdiff(csv_raw[:,1:],raw[key]),"header":csv_path.read_text(encoding="utf-8").splitlines()[0]})
        table_path=DELIVERY/("output/table_"+table_name+".csv")
        table_lines=list(csv.reader(table_path.open(encoding="utf-8-sig",newline="")))
        table=np.array(table_lines[1:],dtype=float)
        target=rounded(raw[key][np.ix_(np.arange(1800,10801,1800),np.arange(0,21,5))])
        table_four_digits=all(re.fullmatch(r"-?\d+\.\d{4}",v) for row in table_lines[1:] for v in row[1:])
        check("paper CSV "+key,table.shape==(6,6) and np.array_equal(table[:,0],np.arange(.5,3.1,.5)) and np.array_equal(table[:,1:],target) and table_four_digits)
        segment=paper.split(section,1)[1].split("### ",1)[0]
        rows=[line for line in segment.splitlines() if re.match(r"^\|\s*\d+\.\d\s*\|",line)]
        paper_tokens=[[x.strip() for x in row.strip("|").split("|")] for row in rows]
        paper_values=np.array(paper_tokens,dtype=float)
        paper_four_digits=all(re.fullmatch(r"-?\d+\.\d{4}",v) for row in paper_tokens for v in row[1:])
        check("paper Markdown "+key,paper_values.shape==(6,6) and np.array_equal(paper_values,table) and paper_four_digits,{"rows":len(rows),"values":int(paper_values[:,1:].size),"tokens":paper_tokens})
        table_summary.append({"field":key,"hours":table[:,0].tolist(),"values":table[:,1:].tolist()})

    summary=read_json("output/delivery_summary.json")
    validation=read_json("output/validation/validation.json")
    T=raw[fields[0]];C=raw[fields[1]]
    endpoints={"T_center":float(T[-1,0]),"T_surface":float(T[-1,-1]),"C_center":float(C[-1,0]),"C_surface":float(C[-1,-1]),
               "mean_T":float(raw["average_temperature_degC"][-1]),"mean_C":float(raw["average_moisture_dry_basis"][-1]),
               "effective_water_reduction_percent":float(100*(1-raw["average_moisture_dry_basis"][-1]/2.55))}
    check("summary endpoint and average values",summary["values_3h"]==endpoints,{"recomputed":endpoints})
    fieldchecks={"T_min":float(T.min()),"T_max":float(T.max()),"C_min":float(C.min()),"C_max":float(C.max()),
                 "C_min_space_difference":float(np.diff(C,axis=1).min()),"C_max_unexpected_radial_increase":float(np.diff(C,axis=1).max()),
                 "T_max_above_current_ambient":float((T-raw["environment"][:,0,None]).max()),
                 "initial_T_error":float(abs(T[0]-28).max()),"initial_C_error":float(abs(C[0]-2.55).max())}
    check("summary physical field checks",summary["field_checks"]==fieldchecks,fieldchecks)
    common=[k for k in summary if k in validation]
    check("summary matches validation shared fields",all(summary[k]==validation[k] for k in common),common)
    check("counts across metadata",summary["total_values"]==453600 and validation["dimensions"]==[10800,21,2] and validation["table_values"]==60)
    excel_record=read_json("output/excel_audit.json")
    check("recorded Excel audit counts",excel_record["all_passed"] and excel_record["total_result_values"]==453600 and excel_record["paper_values_checked"]==60)
    check("recorded Excel audit hash",excel_record["xlsx_hash"]==hashes(DELIVERY/"output/result2.xlsx"),excel_record["xlsx_hash"])

    manifest=read_json("evidence/delivery_manifest.json")
    mismatched=[]; missing=[];present=[]
    paths=[]
    for x in manifest["files"]:
        paths.append(x["path"])
        p=DELIVERY/x["path"]
        if not p.is_file():missing.append(x);continue
        actual=hashes(p)
        if actual["bytes"]!=x["bytes"] or actual["sha256"]!=x["sha256"]: mismatched.append({"record":x,"actual":actual})
        else:present.append(x["path"])
    actual_files=[str(p.relative_to(DELIVERY)).replace("\\","/") for p in DELIVERY.rglob("*") if p.is_file()]
    unlisted=sorted(set(actual_files)-set(paths))
    manifest_summary={"listed":len(paths),"duplicate_paths":len(paths)-len(set(paths)),"present_and_matched":len(present),
                      "mismatched":mismatched,"missing":missing,"unlisted":unlisted,
                      "split_arrays_declared":manifest.get("validation_npz_in_separate_archive"),
                      "missing_bytes":sum(x["bytes"] for x in missing),
                      "all_missing_are_validation_npz":all(x["path"].startswith("output/validation/") and x["path"].endswith(".npz") for x in missing)}
    check("manifest available bytes and hashes",not mismatched and len(paths)==len(set(paths)),manifest_summary)
    check("manifest absent files limited to declared array split",manifest_summary["all_missing_are_validation_npz"] and manifest.get("validation_npz_in_separate_archive") is True)
    figs=read_json("output/figures_manifest.json")
    check("figure manifest files",len(figs["figures"])==10 and all((DELIVERY/f"output/figures/{x}.{ext}").is_file() for x in figs["figures"] for ext in ["png","svg"]))
    paper_images=re.findall(r"!\[[^\]]*\]\(([^)]+)\)",paper)
    check("paper image references",len(paper_images)==10 and all((DELIVERY/"output"/x).is_file() for x in paper_images),paper_images)
    check("paper no unresolved generation tokens",re.search(r"@@[A-Z_0-9]+@@",paper) is None)
    invalid_json=[]
    for p in DELIVERY.rglob("*.json"):
        invalid_json.extend(str(p.relative_to(DELIVERY))+k for k in nonfinite_json(json.loads(p.read_text(encoding="utf-8"))))
    check("JSON no NaN/Infinity",not invalid_json,invalid_json)

    access=read_json("evidence/source_access.json")
    commit=access["observed_commit"]
    git_checks=[]
    for item in access["text_reads"]:
        if item.get("git_blob_sha1") is None:
            git_checks.append({"path":item["path"],"status":"no recorded blob hash; partial read explicitly disclosed"});continue
        p=subprocess.run(["git","rev-parse",f"{commit}:{item['path']}"],cwd=REPO,capture_output=True,text=True,encoding="utf-8")
        blob=p.stdout.strip()
        git_checks.append({"path":item["path"],"recorded_blob":item["git_blob_sha1"],"local_commit_blob":blob,"match":p.returncode==0 and blob==item["git_blob_sha1"]})
    check("GitHub source read blob records match pinned local Git objects",all(x.get("match",True) for x in git_checks),git_checks)
    original_git_checks=[]
    for item in original_inputs:
        p=subprocess.run(["git","rev-parse",f"{commit}:{item['repository_path']}"],cwd=REPO,capture_output=True,text=True,encoding="utf-8")
        original_git_checks.append({"path":item["repository_path"],"blob":p.stdout.strip(),"match":p.returncode==0 and p.stdout.strip()==item["actual"]["git_blob_sha1"]})
    check("original input bytes match pinned Git blobs",all(x["match"] for x in original_git_checks),original_git_checks)
    reproduction=read_json("output/reproduction_audit.json")
    report={"audit_utc":datetime.now(timezone.utc).isoformat(),"scope":"Independently executed artifact audit; no PDE solves, no delivery imports, no writes to delivery. Historical source-access and solver-reproduction events remain Pro-supplied records; local hashes and consistency were independently checked.",
            "source_hash":hashes(Path(__file__)),"delivery_root":str(DELIVERY),
            "all_artifact_checks_passed":all(x["passed"] for x in CHECKS),"checks":CHECKS,
            "inputs":original_inputs,"input_schema":input_schema,"template_schema":template_schema,
            "raw_hash":hashes(raw_file),"workbook":workbook_summary,"paper_tables":table_summary,
            "values_3h":endpoints,"manifest":manifest_summary,"source_access_git_checks":git_checks,
            "pro_recorded_reproduction":reproduction,
            "limits":[f"{len(missing)} per-grid/reference/sensitivity/2D NPZ files are listed but absent from this directory; README and manifest explicitly disclose separate archive. Independent recomputation of those validation statistics requires that archive or fresh solver runs.",
                      "This audit verifies workbook/formal-array/CSV/paper consistency, not the physical validity of the model or actual historical GitHub tool activity."]}
    out=HERE/"artifact_audit.json"
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps({"all_artifact_checks_passed":report["all_artifact_checks_passed"],"checks":len(CHECKS),"failed":[x for x in CHECKS if not x["passed"]],"manifest":{k:v for k,v in manifest_summary.items() if k not in ["missing"]},"missing_array_files":len(missing),"output":str(out)},ensure_ascii=False,indent=2))

if __name__=="__main__": main()
