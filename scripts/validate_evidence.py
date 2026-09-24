#!/usr/bin/env python3
"""Deterministic, zero-dependency validator for ADD Evidence Objects."""
import hashlib, json, re, sys
from datetime import datetime, date
from pathlib import Path

HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")
EID = re.compile(r"^E-[A-Za-z0-9][A-Za-z0-9._-]*$")

def _date(v):
    try: date.fromisoformat(v); return True
    except Exception: return False

def _dt(v):
    try: datetime.fromisoformat(v.replace("Z", "+00:00")); return True
    except Exception: return False

def validate_evidence(obj, *, existing_ids=None, base_dir=None):
    errors=[]; existing_ids=existing_ids or set()
    def req(path, cond, msg):
        if not cond: errors.append(f"{path}: {msg}")
    req("$", isinstance(obj, dict), "must be an object")
    if not isinstance(obj, dict): return errors
    required=["evidence_id","subject","evidence_type","claim","source","retrieval","identity_resolution","quality","supports","limitations","uncertainty","snapshot","human_review"]
    for k in required: req(k, k in obj, "required")
    eid=obj.get("evidence_id")
    req("evidence_id", isinstance(eid,str) and bool(EID.fullmatch(eid)), "must match E-<id>")
    req("evidence_id", eid not in existing_ids, "must be unique")
    req("claim", isinstance(obj.get("claim"),str) and bool(obj.get("claim").strip()), "must be non-empty")
    s=obj.get("subject",{}); req("subject", isinstance(s,dict) and isinstance(s.get("candidate_name"),str) and bool(s.get("candidate_name").strip()), "candidate_name required")
    ets={"source_supported_fact","public_viewpoint","relationship_fact","derived_interpretation","unresolved_lead","unknown_insufficient_coverage"}
    req("evidence_type", obj.get("evidence_type") in ets, "invalid enum")
    src=obj.get("source",{}); req("source", isinstance(src,dict), "must be object")
    if isinstance(src,dict):
        for k in ("title","publisher","source_type"): req(f"source.{k}", isinstance(src.get(k),str) and bool(src.get(k).strip()), "required")
        if not src.get("url") and not src.get("local_path"): errors.append("source: url or local_path required")
        if src.get("published_date") is not None: req("source.published_date", isinstance(src["published_date"],str) and _date(src["published_date"]), "invalid ISO date")
        if src.get("event_date") is not None: req("source.event_date", isinstance(src["event_date"],str) and _date(src["event_date"]), "invalid ISO date")
    ret=obj.get("retrieval",{}); req("retrieval.retrieved_at", isinstance(ret,dict) and isinstance(ret.get("retrieved_at"),str) and _dt(ret["retrieved_at"]), "invalid ISO datetime")
    ex=obj.get("excerpt"); loc=obj.get("excerpt_locator")
    if ex is not None: req("excerpt", isinstance(ex,str) and bool(ex.strip()), "must be non-empty when supplied")
    if ex and not loc: errors.append("excerpt_locator: required when excerpt is supplied")
    if obj.get("evidence_type") in {"source_supported_fact","public_viewpoint","relationship_fact"} and not ex: errors.append("excerpt: required for source-backed evidence")
    allowed_id={"resolved","partially_resolved","unresolved_same_name","not_applicable"}; req("identity_resolution", obj.get("identity_resolution") in allowed_id, "invalid enum")
    q=obj.get("quality",{}); req("quality", isinstance(q,dict) and q.get("source_quality") in {"A","B","C","unknown"} and q.get("provenance_status") in {"primary","secondary","snippet_only","user_supplied","unknown"}, "invalid or missing quality")
    sp=obj.get("supports",{}); req("supports", isinstance(sp,dict) and sp.get("relevance") in {"direct","contextual","lead_only","none","unknown"} and isinstance(sp.get("supports_statement"),str) and bool(sp.get("supports_statement").strip()), "invalid supports")
    req("limitations", isinstance(obj.get("limitations"),list) and all(isinstance(x,str) for x in obj.get("limitations",[])), "must be string array")
    req("uncertainty", obj.get("uncertainty") in {"none_stated","limited","material","unknown"}, "invalid enum")
    hr={"not_started","in_review","reviewed","reviewed_with_reservation"}; req("human_review", obj.get("human_review") in hr, "invalid enum")
    snap=obj.get("snapshot",{}); req("snapshot", isinstance(snap,dict) and snap.get("level") in {"L0","L1","L2","L3","L4"} and snap.get("status") in {"not_saved","saved","unavailable","user_provided"}, "invalid snapshot")
    if isinstance(snap,dict):
        path=snap.get("path"); sha=snap.get("sha256")
        if snap.get("status") in {"saved","user_provided"}: req("snapshot.path", isinstance(path,str) and bool(path), "required for saved snapshot")
        if sha is not None: req("snapshot.sha256", isinstance(sha,str) and bool(HEX64.fullmatch(sha)), "must be 64 hex characters")
        if path and base_dir and Path(path).is_file() and sha: req("snapshot.sha256", hashlib.sha256(Path(path).read_bytes()).hexdigest().lower()==sha.lower(), "does not match snapshot file")
        if path and base_dir and snap.get("status")=="saved": req("snapshot.path", Path(path).is_file(), "snapshot file does not exist")
    return errors

def validate_file(path):
    data=json.loads(Path(path).read_text(encoding="utf-8")); items=data if isinstance(data,list) else [data]; errors=[]; ids=set()
    for i,item in enumerate(items):
        es=validate_evidence(item,existing_ids=ids,base_dir=Path(path).parent)
        errors.extend([f"item[{i}]: {e}" for e in es]);
        if isinstance(item,dict) and isinstance(item.get("evidence_id"),str): ids.add(item["evidence_id"])
    return errors

if __name__ == "__main__":
    if len(sys.argv)!=2: print("usage: validate_evidence.py FILE", file=sys.stderr); sys.exit(2)
    errs=validate_file(sys.argv[1])
    if errs:
        print("INVALID"); print("\n".join(f"- {e}" for e in errs)); sys.exit(1)
    print("VALID")
