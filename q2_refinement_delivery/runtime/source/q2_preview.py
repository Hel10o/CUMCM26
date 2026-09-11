"""Render an audited A1:H7 excerpt without loading a large workbook into the renderer.
Read actual OOXML values and reproduce the exporter's unchanged formats with
artifact_tool. This is a compact layout preview, not native Excel application testing.
"""
import argparse
from artifact_tool import Workbook
from q2_core import read_workbook_values

def main():
    p=argparse.ArgumentParser();p.add_argument("--xlsx",required=True);p.add_argument("--out",required=True);a=p.parse_args()
    values=read_workbook_values(a.xlsx)["温度"]["values"]
    w=Workbook.create();s=w.worksheets.add("温度")
    s.get_range("A1:H7").values=[[values[f"{col}{row}"] for col in "ABCDEFGH"] for row in range(1,8)]
    s.get_range("A1").format.column_width=23
    s.get_range("B1:H1").format.column_width=11
    s.get_range("B1:H1").set_number_format("0.0")
    s.get_range("B2:H7").set_number_format("0.0000")
    w.render({"sheet_name":"温度","range":"A1:H7","scale":2}).save(a.out)
    print("Audited compact excerpt preview:",a.out)

if __name__=="__main__":main()
