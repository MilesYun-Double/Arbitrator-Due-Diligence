import json, tempfile, unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from validate_evidence import validate_evidence

BASE=json.loads((Path(__file__).parents[1]/"examples/evidence.valid.json").read_text(encoding="utf-8"))
class EvidenceValidatorTests(unittest.TestCase):
    def test_valid(self): self.assertEqual(validate_evidence(BASE), [])
    def test_missing_source_traceability(self):
        x=json.loads(json.dumps(BASE)); x["source"]["url"]=None; self.assertTrue(validate_evidence(x))
    def test_duplicate_id(self): self.assertTrue(validate_evidence(BASE, existing_ids={BASE["evidence_id"]}))
    def test_unknown_dates_allowed(self):
        x=json.loads(json.dumps(BASE)); x["source"]["published_date"]=None; x["source"]["event_date"]=None; self.assertEqual(validate_evidence(x), [])
    def test_unresolved_same_name(self):
        x=json.loads(json.dumps(BASE)); x["identity_resolution"]="unresolved_same_name"; x["evidence_type"]="unresolved_lead"; x["supports"]={"relevance":"lead_only","supports_statement":"仅为待核查线索。"}; self.assertEqual(validate_evidence(x), [])
    def test_search_snippet_is_lead(self):
        x=json.loads(json.dumps(BASE)); x["source"]["source_type"]="search_snippet"; x["quality"]={"source_quality":"C","provenance_status":"snippet_only"}; x["evidence_type"]="unresolved_lead"; x["supports"]={"relevance":"lead_only","supports_statement":"仅用于定位原文。"}; self.assertEqual(validate_evidence(x), [])
    def test_secondary_source(self):
        x=json.loads(json.dumps(BASE)); x["source"]["source_type"]="secondary_or_aggregator"; x["quality"]={"source_quality":"C","provenance_status":"secondary"}; self.assertEqual(validate_evidence(x), [])
    def test_excerpt_requires_locator(self):
        x=json.loads(json.dumps(BASE)); x["excerpt_locator"]=None; self.assertTrue(validate_evidence(x))
    def test_missing_snapshot(self):
        x=json.loads(json.dumps(BASE)); x["snapshot"]={"level":"L2","status":"saved","path":"missing.html"}; self.assertTrue(validate_evidence(x,base_dir=Path('.')))
    def test_bad_hash(self):
        x=json.loads(json.dumps(BASE)); x["snapshot"]["sha256"]="bad"; self.assertTrue(validate_evidence(x))
    def test_human_review_pending(self):
        x=json.loads(json.dumps(BASE)); x["human_review"]="not_started"; self.assertEqual(validate_evidence(x), [])
    def test_not_found_is_unknown(self):
        x=json.loads(json.dumps(BASE)); x["evidence_type"]="unknown_insufficient_coverage"; x["claim"]="本次检索未发现符合条件的公开来源。"; x["excerpt"]=None; x["excerpt_locator"]=None; x["supports"]={"relevance":"unknown","supports_statement":"仅表示本次覆盖范围内未发现，不表示不存在。"}; x["uncertainty"]="material"; self.assertEqual(validate_evidence(x), [])
if __name__=='__main__': unittest.main()
