from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import pdf_report as pdf
from report import blocks, render_html, render_markdown


class PDFReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=json.loads((ROOT/'tests/fixtures/pdf_reports/model.json').read_text(encoding='utf-8'))
        cls.runtime=ROOT/'.tmp-issue9-test-runtime'
        pdf.load_dependencies(cls.runtime)

    def test_same_model_content_and_layout(self):
        before=deepcopy(self.model)
        raw,meta=pdf.render_pdf(self.model, self.runtime)
        checked=pdf.readback(raw,self.model)
        self.assertGreater(checked['page_count'],1)
        self.assertEqual(self.model,before)
        self.assertGreater(meta['font_bytes'],0)
        self.assertTrue(checked['content_consistent'])
        self.assertTrue(checked['embedded_fonts'])
        self.assertEqual(checked['page_labels'],list(range(1,checked['page_count']+1)))
        self.assertIn('unresolved',render_html(self.model))
        self.assertIn('unknown',render_markdown(self.model))

    def test_no_network_or_source_access(self):
        model=deepcopy(self.model)
        model['evidence'][0]['claim']='<img src="https://example.invalid/remote"> <script>alert(1)</script>'
        model['evidence'][0]['source']['url']='javascript://alert(1)'
        with patch('socket.socket',side_effect=AssertionError('network')):
            raw,_=pdf.render_pdf(model,self.runtime)
        checked=pdf.readback(raw,model)
        self.assertTrue(checked['content_consistent'])
        self.assertEqual(checked['uri_links'],[])

    def test_missing_glyph_fails(self):
        model=deepcopy(self.model);model['task']['title']+='\U0010ffff'
        with self.assertRaisesRegex(ValueError,'missing glyph'):
            pdf.render_pdf(model,self.runtime)

    def test_missing_font_fails(self):
        with patch.object(pdf,'FONT_PATH',ROOT/'vendor/pdf/missing.ttf'), self.assertRaises((ValueError,OSError)):
            pdf.render_pdf(self.model,self.runtime)

    def test_font_hash_fails(self):
        with patch.object(pdf,'FONT_HASH','0'*64),self.assertRaisesRegex(ValueError,'hash'):
            pdf.render_pdf(self.model,self.runtime)

    def test_bundle_hash_fails(self):
        with patch.dict(pdf.WHEELS,{next(iter(pdf.WHEELS)):'0'*64}),self.assertRaisesRegex(ValueError,'hash'):
            pdf.load_dependencies(self.runtime)

    def test_missing_dependency_fails(self):
        with patch.dict(pdf.WHEELS,{'missing.whl':'0'*64}),self.assertRaises(OSError):
            pdf.load_dependencies(self.runtime)

    def test_runtime_unknown_file_is_not_executed_or_overwritten(self):
        extra=self.runtime/'unexpected.py'
        extra.write_text('raise AssertionError("must not execute")',encoding='utf-8')
        try:
            with self.assertRaisesRegex(ValueError,'unexpected runtime'):
                pdf.load_dependencies(self.runtime)
            self.assertIn('must not execute',extra.read_text())
        finally:
            extra.unlink()  # Only the exact file created by this test.

    def test_personal_hooks_are_disabled(self):
        from reportlab import rl_config
        self.assertEqual(rl_config.TTFSearchPath,[])
        self.assertEqual(rl_config.T1SearchPath,[])
        self.assertFalse(hasattr(sys.modules['reportlab_mods'],'__file__'))

    def test_saved_model_tampering_rejected(self):
        model=deepcopy(self.model);model['sections'][0]['evidence_ids']=[]
        with self.assertRaisesRegex(ValueError,'canonical'):
            pdf.check_model(model)

    def test_model_external_snapshot_not_read(self):
        model=deepcopy(self.model)
        model['evidence'][0]['snapshot'].update(path=str(ROOT/'reports/private.pdf'),status='saved')
        with patch.object(Path,'read_bytes',side_effect=AssertionError('source read')):
            pdf.check_model(model)

    def test_output_and_timing(self):
        with tempfile.TemporaryDirectory(prefix='.tmp-pdf-report-',dir=ROOT) as folder:
            output=Path(folder)/'out'
            t=pdf.generate_pdf(ROOT/'tests/fixtures/pdf_reports/model.json',output,self.runtime)
            for key in ('dependency_load_ms','pdf_render_ms','pdf_write_ms','readback_ms','formats_total_ms','total_ms'):
                self.assertGreaterEqual(t[key],0)
            self.assertEqual(t['pdf_bytes'],(output/'report.pdf').stat().st_size)
            self.assertEqual((output/'report.md').read_text(encoding='utf-8'),render_markdown(self.model))
            self.assertEqual((output/'report.html').read_text(encoding='utf-8'),render_html(self.model))
            with self.assertRaises(FileExistsError):
                pdf.generate_pdf(ROOT/'tests/fixtures/pdf_reports/model.json',output,self.runtime)

    def test_outside_model_rejected(self):
        with self.assertRaises(ValueError):
            pdf.generate_pdf(ROOT/'reports/model.json',ROOT/'.tmp-no-report',self.runtime)


if __name__=='__main__':unittest.main()
