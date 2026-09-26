"""Real scope plumbing with entirely synthetic identities and documents."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import research_run as rr
import static_source as static
import pdf_source as pdf
import report
from pdf_fixture import make_pdf


def metadata():
    return dict(subject=dict(candidate_name='测试人物甲 / TEST, Alpha', candidate_id='test-18',
                             institution='合成机构', identity_notes='合成内容，不是人物研究'),
                evidence_type='source_supported_fact', claim='合成资料记载测试文字。',
                source=dict(title='合成公开材料', publisher='测试发布者', source_type='institutional_profile',
                            url=None, published_date='2026-01-02', event_date=None),
                identity_resolution='partially_resolved',
                quality=dict(source_quality='B', provenance_status='primary', quality_notes='测试输入'),
                supports=dict(relevance='contextual', supports_statement='仅测试调用者明确的关联'),
                context='测试文字上下文', limitations=['仅验证 plumbing，不作真人结论'],
                uncertainty='limited', human_review='not_started')


class RealRunTests(unittest.TestCase):
    def setUp(self):
        self.fixture = tempfile.TemporaryDirectory(dir=ROOT / 'tests/fixtures', prefix='real-input-')
        self.addCleanup(self.fixture.cleanup)
        self.source = Path(self.fixture.name) / 'source.txt'
        self.source.write_text('合成测试文字', encoding='utf-8')
        self.root = ROOT / 'reports' / ('test-real-' + uuid.uuid4().hex)
        self.addCleanup(lambda: shutil.rmtree(self.root) if self.root.exists() else None)

    def create(self, source=None, sha=None):
        source = source or self.source
        digest = sha or hashlib.sha256(source.read_bytes()).hexdigest()
        rr.real_run_root(self.root, create=True, authorized_inputs=[dict(path=str(source), sha256=digest, url=None)])
        return rr.stage_input(self.root, source, digest)

    def meta(self, value=None):
        path = self.root / 'metadata.json'
        path.write_text(json.dumps(value or metadata(), ensure_ascii=False), encoding='utf-8')
        return path

    def collect(self, staged, **kwargs):
        return static.collect(str(staged), self.root / 'static', evidence_id='E-REAL-1',
                              excerpt='合成测试文字', run_root=self.root, metadata_path=self.meta(), **kwargs)

    def test_staging_identity_and_provenance(self):
        staged = self.create()
        self.assertEqual(staged.read_bytes(), self.source.read_bytes())
        record = json.loads((staged.parent / 'staging.json').read_text(encoding='utf-8'))
        self.assertEqual(record['original_path'], str(self.source))
        self.assertEqual(record['actual_sha256'], record['expected_sha256'])
        self.assertTrue(record['copied_at'])
        with self.assertRaises(FileExistsError): rr.stage_input(self.root, self.source, record['actual_sha256'])
        with self.assertRaises(FileExistsError): rr.real_run_root(self.root, create=True, authorized_inputs=[])
        evidence = json.loads(self.collect(staged).read_text(encoding='utf-8'))
        for key in ('subject', 'identity_resolution', 'quality', 'supports', 'context', 'limitations', 'uncertainty', 'human_review', 'evidence_type', 'claim'):
            self.assertEqual(evidence[key], metadata()[key])
        for key, value in metadata()['source'].items(): self.assertEqual(evidence['source'][key], value)
        with self.assertRaises(FileExistsError): self.collect(staged)

    def test_bad_hash_and_undeclared_source(self):
        rr.real_run_root(self.root, create=True, authorized_inputs=[dict(path=str(self.source),sha256='0'*64,url=None)])
        with self.assertRaisesRegex(ValueError, 'mismatch'): rr.stage_input(self.root,self.source,'0'*64)
        with self.assertRaisesRegex(ValueError, 'not explicitly'): rr.stage_input(self.root,self.source,'1'*64)
        with self.assertRaises(ValueError): rr.input_path(ROOT / 'AGENTS.md')
        with self.assertRaises(ValueError): rr.input_path(ROOT / 'reports/secrets/input.txt')

    def test_marker_scope_and_sibling(self):
        self.create()
        with self.assertRaises(ValueError): rr.real_run_root(ROOT / '.tmp-wrong',create=True,authorized_inputs=[])
        with self.assertRaises(ValueError): static.scoped_path(self.root / 'metadata.json', ROOT)
        with self.assertRaises(ValueError): rr.run_path(self.root.parent / 'sibling/x.txt',self.root)
        with self.assertRaises(ValueError): rr.run_path(self.root / 'inputs/../x.txt',self.root)
        with self.assertRaises(ValueError): rr.input_path(self.root / 'x.txt')
        marker = self.root / rr.MARKER
        marker.write_text(json.dumps(static.RUN_CONTRACT),encoding='utf-8')
        with self.assertRaises(ValueError): rr.real_run_root(self.root)
        marker.unlink()
        with self.assertRaises(OSError): rr.real_run_root(self.root)

    def test_changed_and_unstaged_inputs(self):
        staged = self.create()
        staged.write_text('changed',encoding='utf-8')
        with self.assertRaises(ValueError): self.collect(staged)
        direct = self.root / 'direct.txt';direct.write_text('合成测试文字',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'must be staged'): self.collect(direct)

    def test_declared_incoming_and_forged_staging(self):
        incoming=self.root/'incoming/new.txt';raw=b'new locally saved source'
        digest=hashlib.sha256(raw).hexdigest()
        rr.real_run_root(self.root,create=True,authorized_inputs=[dict(path=str(incoming),sha256=digest,url=None)])
        incoming.parent.mkdir();incoming.write_bytes(raw)
        staged=rr.stage_input(self.root,incoming,digest)
        self.assertEqual(rr.staged_input(staged,self.root),staged)
        record_path=staged.parent/'staging.json'
        record=json.loads(record_path.read_text(encoding='utf-8'))
        record['original_path']=str(self.source)
        record_path.write_text(json.dumps(record),encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'not authorized'): rr.staged_input(staged,self.root)

    def test_metadata_required_invalid_and_failure_no_invented_evidence(self):
        staged = self.create()
        with self.assertRaises(ValueError): static.collect(str(staged),self.root/'out',evidence_id='E-1',run_root=self.root)
        value=metadata();value['identity_resolution']='invented'
        with self.assertRaisesRegex(ValueError,'identity_resolution'):
            static.collect(str(staged),self.root/'out',evidence_id='E-1',excerpt='合成测试文字',run_root=self.root,metadata_path=self.meta(value))
        with self.assertRaisesRegex(ValueError,'not reclassified'):
            static.collect(str(staged),self.root/'out',evidence_id='E-1',excerpt='absent',run_root=self.root,metadata_path=self.meta())
        self.assertFalse((self.root/'out').exists())

    def test_real_url_uses_existing_safe_fetch(self):
        rr.real_run_root(self.root,create=True,authorized_inputs=[])
        value=metadata();value['source']['url']='https://example.com/profile'
        def fetch(url, info):
            info.update(content_type='text/plain',http_status=200,final_url=url)
            return '合成测试文字'.encode()
        with patch.object(static,'_fetch',side_effect=fetch) as called:
            path=static.collect(value['source']['url'],self.root/'url',evidence_id='E-URL',excerpt='合成测试文字',run_root=self.root,metadata_path=self.meta(value))
        called.assert_called_once()
        self.assertEqual(json.loads(path.read_text(encoding='utf-8'))['source']['url'],value['source']['url'])

    def test_pdf_151_page_selective_and_ceiling(self):
        source=Path(self.fixture.name)/'large.pdf';source.write_bytes(make_pdf(['合成测试文字']*151))
        staged=self.create(source)
        path=pdf.collect_pdf(staged,self.root/'pdf',evidence_id='E-PDF',excerpt='合成测试文字',page=107,run_root=self.root,metadata_path=self.meta())
        obj=json.loads(path.read_text(encoding='utf-8'))
        self.assertEqual(obj['identity_resolution'],'partially_resolved')
        self.assertEqual(obj['supports'],metadata()['supports'])
        pages=json.loads((path.parent/'pages.json').read_text(encoding='utf-8'))
        self.assertEqual(pages['page_count'],151);self.assertEqual(pages['extracted_pages'],[107])
        self.assertEqual(len(pages['pages']),1);self.assertEqual(pages['pages'][0]['page'],107)
        with patch.object(pdf,'REAL_MAX_PAGES',150), self.assertRaisesRegex(ValueError,'1..150'):
            pdf.collect_pdf(staged,self.root/'too-many',evidence_id='E-PDF',excerpt='合成测试文字',page=107,run_root=self.root,metadata_path=self.meta())
        with patch.object(pdf,'MAX_BYTES',10), self.assertRaisesRegex(ValueError,'10 MiB'):
            pdf.collect_pdf(staged,self.root/'too-big',evidence_id='E-PDF',excerpt='合成测试文字',page=107,run_root=self.root,metadata_path=self.meta())

    def test_real_pdf_corrupt_encrypted_and_301_pages(self):
        import io
        writer=pdf.load_pypdf().PdfWriter()
        writer.add_blank_page(width=100,height=100);writer.encrypt('test-only')
        stream=io.BytesIO();writer.write(stream)
        cases=[(b'%PDF-1.4\ncorrupt','corrupt'),(stream.getvalue(),'encrypted'),
               (make_pdf(['合成测试文字']*301),'ceiling')]
        for raw,name in cases:
            with self.subTest(name=name):
                source=Path(self.fixture.name)/(name+'.pdf');source.write_bytes(raw)
                root=self.root.with_name(self.root.name+'-'+name)
                self.addCleanup(lambda root=root:shutil.rmtree(root) if root.exists() else None)
                digest=hashlib.sha256(raw).hexdigest()
                rr.real_run_root(root,create=True,authorized_inputs=[dict(path=str(source),sha256=digest,url=None)])
                staged=rr.stage_input(root,source,digest)
                meta=root/'metadata.json';meta.write_text(json.dumps(metadata()),encoding='utf-8')
                with self.assertRaisesRegex(ValueError,'not reclassified'):
                    pdf.collect_pdf(staged,root/'out',evidence_id='E-PDF',excerpt='合成测试文字',page=1,run_root=root,metadata_path=meta)
                self.assertFalse((root/'out').exists())

    def test_cross_run_collector_report_and_pdf_inputs_rejected(self):
        staged=self.create()
        other=self.root.with_name(self.root.name+'-sibling')
        self.addCleanup(lambda:shutil.rmtree(other) if other.exists() else None)
        rr.real_run_root(other,create=True,authorized_inputs=[])
        with self.assertRaises(ValueError): rr.stage_input(other,staged,hashlib.sha256(staged.read_bytes()).hexdigest())
        with self.assertRaises(ValueError):
            pdf.collect_pdf(staged,other/'out',evidence_id='E-PDF',excerpt='x',page=1,run_root=other,metadata_path=self.meta())
        with self.assertRaises(ValueError):
            report.generate(self.root/'evidence.json',other/'task.json',other/'out',run_root=other)
        import pdf_report
        with self.assertRaises(ValueError):
            pdf_report.generate_pdf(self.root/'report.json',other/'out',other/'.tmp-runtime',run_root=other)

    def test_snapshot_sibling_rejected_before_validator(self):
        staged=self.create();obj=json.loads(self.collect(staged).read_text(encoding='utf-8'))
        obj['snapshot']['path']=str(self.root.parent/'other/private.pdf')
        with patch.object(report,'validate_evidence') as validator, self.assertRaises(ValueError):
            report.validate_inputs([obj],self.root,run_root=self.root)
        validator.assert_not_called()

    def test_hardlink_refused(self):
        self.create();link=self.root/'link.txt';os.link(self.source,link)
        self.addCleanup(lambda:link.unlink() if link.exists() else None)
        with self.assertRaisesRegex(ValueError,'hard-linked'): rr.run_path(link,self.root)

    def test_junction_or_symlink_refused(self):
        self.create();link=self.root/'linked'
        if os.name=='nt':
            result=subprocess.run(['cmd','/c','mklink','/J',str(link),self.fixture.name],capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.addCleanup(lambda:os.rmdir(link) if link.exists() else None)
        else:
            link.symlink_to(self.fixture.name,target_is_directory=True)
            self.addCleanup(lambda:link.unlink() if link.is_symlink() else None)
        with self.assertRaisesRegex(ValueError,'links/reparse'): rr.run_path(link/'source.txt',self.root)

    def test_full_real_mode_cli_smoke(self):
        result=subprocess.run([sys.executable,'-B','-E','-S',str(ROOT/'tests/real_chain.py'),
                               '--run-root',str(self.root)],capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr.decode('utf-8',errors='replace'))
        smoke=json.loads((self.root/'smoke-result.json').read_text(encoding='utf-8'))
        self.assertEqual(smoke['result'],'PASS')
        self.assertTrue(smoke['pdf']['content_consistent'])


if __name__=='__main__': unittest.main()
