#!/usr/bin/env python3
"""Deterministic, zero-dependency structural/runtime validator for ADD Evidence Objects."""
import hashlib, json, re, sys
from datetime import datetime, date
from pathlib import Path

HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")
EID = re.compile(r"^E-[A-Za-z0-9][A-Za-z0-9._-]*$")
URI = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*://[^\s]+$")
DATE_FIELDS = ("published_date", "event_date")

def _date(v):
    try: date.fromisoformat(v); return True
    except Exception: return False

def _dt(v):
    try: datetime.fromisoformat(v.replace("Z", "+00:00")); return True
    except Exception: return False

def _type(v, kind):
    if kind == "string": return isinstance(v, str)
    if kind == "object": return isinstance(v, dict)
    if kind == "array": return isinstance(v, list)
    if kind == "null": return v is None
    return False

def _object(errors, path, value, allowed, required):
    if not isinstance(value, dict):
        errors.append(f"{path}: must be object"); return False
    for key in required:
        if key not in value: errors.append(f"{path}.{key}: required")
    for key in value:
        if key not in allowed: errors.append(f"{path}.{key}: unknown field")
    return True

def _nullable_string(errors, path, value, nonempty=False):
    if value is not None and (not isinstance(value, str) or (nonempty and not value.strip())):
        errors.append(f"{path}: must be {'non-empty ' if nonempty else ''}string or null")

def validate_evidence(obj, *, existing_ids=None, base_dir=None):
    errors=[]; existing_ids=existing_ids or set()
    root_allowed={"evidence_id","subject","evidence_type","claim","source","retrieval","excerpt","excerpt_locator","context","identity_resolution","quality","supports","limitations","uncertainty","snapshot","human_review"}
    root_required={"evidence_id","subject","evidence_type","claim","source","retrieval","identity_resolution","quality","supports","limitations","uncertainty","snapshot","human_review"}
    if not isinstance(obj, dict): return ["$: must be object"]
    _object(errors,"$",obj,root_allowed,root_required)
    eid=obj.get("evidence_id")
    if not (isinstance(eid,str) and EID.fullmatch(eid)): errors.append("evidence_id: invalid format")
    if eid in existing_ids: errors.append("evidence_id: must be unique")
    if not (isinstance(obj.get("claim"),str) and obj["claim"].strip()): errors.append("claim: must be non-empty string")
    s=obj.get("subject")
    if _object(errors,"subject",s,{"candidate_name","candidate_id","institution","identity_notes"},{"candidate_name"}):
        if not (isinstance(s.get("candidate_name"),str) and s["candidate_name"].strip()): errors.append("subject.candidate_name: must be non-empty string")
        for k in ("candidate_id","institution","identity_notes"): _nullable_string(errors,f"subject.{k}",s.get(k))
    ets={"source_supported_fact","public_viewpoint","relationship_fact","derived_interpretation","unresolved_lead","unknown_insufficient_coverage"}
    if obj.get("evidence_type") not in ets: errors.append("evidence_type: invalid enum")
    src=obj.get("source")
    if _object(errors,"source",src,{"title","publisher","url","local_path","source_type","published_date","event_date"},{"title","publisher","source_type"}):
        for k in ("title","publisher"):
            if not (isinstance(src.get(k),str) and src[k].strip()): errors.append(f"source.{k}: must be non-empty string")
        stypes={"official_roster","official_profile","official_rule","government_or_court","original_publication","publisher_page","conference_or_event","institutional_profile","formal_media","secondary_or_aggregator","search_snippet","user_provided_file","other"}
        if src.get("source_type") not in stypes: errors.append("source.source_type: invalid enum")
        for k in ("url","local_path"): _nullable_string(errors,f"source.{k}",src.get(k))
        if not src.get("url") and not src.get("local_path"): errors.append("source: url or local_path required")
        if src.get("url") is not None and isinstance(src.get("url"),str) and not URI.fullmatch(src["url"]): errors.append("source.url: invalid URI")
        for k in DATE_FIELDS:
            v=src.get(k)
            if v is not None and (not isinstance(v,str) or not _date(v)): errors.append(f"source.{k}: invalid ISO date")
    ret=obj.get("retrieval")
    if _object(errors,"retrieval",ret,{"retrieved_at","retrieval_notes"},{"retrieved_at"}):
        if not (isinstance(ret.get("retrieved_at"),str) and _dt(ret["retrieved_at"])): errors.append("retrieval.retrieved_at: invalid ISO datetime")
        _nullable_string(errors,"retrieval.retrieval_notes",ret.get("retrieval_notes"))
    ex=obj.get("excerpt"); loc=obj.get("excerpt_locator"); ctx=obj.get("context")
    _nullable_string(errors,"excerpt",ex); _nullable_string(errors,"excerpt_locator",loc); _nullable_string(errors,"context",ctx)
    if ex and not (isinstance(loc,str) and loc.strip()): errors.append("excerpt_locator: required non-empty string when excerpt is supplied")
    if obj.get("evidence_type") in {"source_supported_fact","public_viewpoint","relationship_fact"} and not (isinstance(ex,str) and ex.strip()): errors.append("excerpt: required for source-backed evidence")
    if obj.get("identity_resolution") not in {"resolved","partially_resolved","unresolved_same_name","not_applicable"}: errors.append("identity_resolution: invalid enum")
    q=obj.get("quality")
    if _object(errors,"quality",q,{"source_quality","provenance_status","quality_notes"},{"source_quality","provenance_status"}):
        if q.get("source_quality") not in {"A","B","C","unknown"}: errors.append("quality.source_quality: invalid enum")
        if q.get("provenance_status") not in {"primary","secondary","snippet_only","user_supplied","unknown"}: errors.append("quality.provenance_status: invalid enum")
        _nullable_string(errors,"quality.quality_notes",q.get("quality_notes"))
    sp=obj.get("supports")
    if _object(errors,"supports",sp,{"relevance","supports_statement"},{"relevance","supports_statement"}):
        if sp.get("relevance") not in {"direct","contextual","lead_only","none","unknown"}: errors.append("supports.relevance: invalid enum")
        if not (isinstance(sp.get("supports_statement"),str) and sp["supports_statement"].strip()): errors.append("supports.supports_statement: must be non-empty string")
    lim=obj.get("limitations")
    if not (isinstance(lim,list) and all(isinstance(x,str) for x in lim)): errors.append("limitations: must be string array")
    if obj.get("uncertainty") not in {"none_stated","limited","material","unknown"}: errors.append("uncertainty: invalid enum")
    snap=obj.get("snapshot")
    if _object(errors,"snapshot",snap,{"level","status","path","sha256","media_type","notes"},{"level","status"}):
        if snap.get("level") not in {"L0","L1","L2","L3","L4"}: errors.append("snapshot.level: invalid enum")
        if snap.get("status") not in {"not_saved","saved","unavailable","user_provided"}: errors.append("snapshot.status: invalid enum")
        for k in ("path","sha256","media_type","notes"): _nullable_string(errors,f"snapshot.{k}",snap.get(k))
        path=snap.get("path"); sha=snap.get("sha256")
        if snap.get("status") in {"saved","user_provided"} and not (isinstance(path,str) and path): errors.append("snapshot.path: required for saved snapshot")
        if sha is not None and (not isinstance(sha,str) or not HEX64.fullmatch(sha)): errors.append("snapshot.sha256: must be 64 hex characters or null")
        if path and base_dir and Path(path).is_file() and sha and hashlib.sha256(Path(path).read_bytes()).hexdigest().lower()!=sha.lower(): errors.append("snapshot.sha256: does not match snapshot file")
        if path and base_dir and snap.get("status")=="saved" and not Path(path).is_file(): errors.append("snapshot.path: snapshot file does not exist")
    if obj.get("human_review") not in {"not_started","in_review","reviewed","reviewed_with_reservation"}: errors.append("human_review: invalid enum")
    return errors

def validate_file(path):
    data=json.loads(Path(path).read_text(encoding="utf-8")); items=data if isinstance(data,list) else [data]; errors=[]; ids=set()
    for i,item in enumerate(items):
        es=validate_evidence(item,existing_ids=ids,base_dir=Path(path).parent); errors.extend([f"item[{i}]: {e}" for e in es])
        if isinstance(item,dict) and isinstance(item.get("evidence_id"),str): ids.add(item["evidence_id"])
    return errors

if __name__ == "__main__":
    if len(sys.argv)!=2: print("usage: validate_evidence.py FILE", file=sys.stderr); sys.exit(2)
    errs=validate_file(sys.argv[1])
    if errs: print("INVALID"); print("\n".join(f"- {e}" for e in errs)); sys.exit(1)
    print("VALID")
