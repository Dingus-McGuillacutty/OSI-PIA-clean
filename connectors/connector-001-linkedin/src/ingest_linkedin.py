#!/usr/bin/env python3
"""Connector 001: LinkedIn archive -> normalized PIA evidence records."""
from pathlib import Path
import argparse, csv, hashlib, json, re
from datetime import datetime

def read_csv_flexible(path):
    lines = Path(path).read_text(encoding="utf-8-sig", errors="replace").splitlines()
    start = 0
    for i, line in enumerate(lines):
        if "," in line:
            fields = next(csv.reader([line]))
            if len(fields) >= 2 and "Notes:" not in fields:
                start = i
                if i == 0 or any(x in fields for x in ("First Name","Name","Title","Company Name","School Name")):
                    break
    return list(csv.DictReader(lines[start:]))

def clean(value):
    return re.sub(r"\s+", " ", (value or "").strip())

def evidence_id(participant_id, source_file, row_number, evidence_type):
    raw = f"{participant_id}|{source_file}|{row_number}|{evidence_type}"
    return "ev-" + hashlib.sha256(raw.encode()).hexdigest()[:16]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--participant-id", required=True)
    args = ap.parse_args()

    inp, out = Path(args.input), Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    evidence = []

    mapping = {
        "Profile.csv": ("profile", "Headline", "Summary"),
        "Positions.csv": ("position", "Title", "Description"),
        "Education.csv": ("education", "Degree Name", "Notes"),
        "Certifications.csv": ("certification", "Name", "Authority"),
        "Projects.csv": ("project", "Title", "Description"),
        "Publications.csv": ("publication", "Name", "Description"),
        "Skills.csv": ("skill", "Name", ""),
        "Honors.csv": ("honor", "Title", "Description"),
        "Learning.csv": ("learning", "Content Title", "Content Description"),
        "Endorsement_Received_Info.csv": ("endorsement", "Skill Name", "Endorsement Status"),
    }

    for filename, (etype, title_key, desc_key) in mapping.items():
        p = inp / filename
        if not p.exists():
            continue
        for n, row in enumerate(read_csv_flexible(p), start=2):
            evidence.append({
                "evidence_id": evidence_id(args.participant_id, filename, n, etype),
                "participant_id": args.participant_id,
                "evidence_type": etype,
                "source_file": filename,
                "source_row": n,
                "title": clean(row.get(title_key)),
                "description": clean(row.get(desc_key)) if desc_key else "",
                "source_payload_json": json.dumps(row, ensure_ascii=False),
                "confidence": "source_asserted",
                "sensitivity": "private",
                "derivation_method": "direct_normalization"
            })

    fields = list(evidence[0]) if evidence else [
        "evidence_id","participant_id","evidence_type","source_file","source_row",
        "title","description","source_payload_json","confidence","sensitivity","derivation_method"
    ]
    with (out / "evidence_records.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(evidence)

if __name__ == "__main__":
    main()
