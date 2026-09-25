import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from pdf_fixture import CHINESE, SECOND, ENGLISH, make_pdf
import pdf_source as pdf
from validate_evidence import validate_file


class PDFSourceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='.tmp-pdf-', dir=ROOT)
        self.addCleanup(self.tmp.cleanup)
        self.output = Path(self.tmp.name) / 'result'

    def collect(self, **kwargs):
        options = dict(source=str(pdf.PDF_ROOT / 'digital.pdf'), output=self.output,
                       evidence_id='E-PDF-001', title='合成PDF', publisher='测试夹具',
                       claim='第二页包含合成声明。', excerpt=SECOND, page=2)
        options.update(kwargs)
        path = pdf.collect_pdf(**options)
        self.assertEqual(validate_file(path), [])
        return json.loads(path.read_text(encoding='utf-8'))

    def test_chinese_pages_excerpt_hash(self):
        obj = self.collect()
        self.assertEqual(obj['excerpt'], SECOND)
        self.assertIn('PDF page 2', obj['excerpt_locator'])
        raw = Path(obj['snapshot']['path']).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), obj['snapshot']['sha256'])
        self.assertEqual(raw, make_pdf())
        pages = json.loads((self.output / 'pages.json').read_text(encoding='utf-8'))
        self.assertIn(CHINESE, pages[0]['text'])
        self.assertIn(ENGLISH, pages[1]['text'])
        notes = json.loads(obj['snapshot']['notes'])
        self.assertEqual(notes['pages_sha256'], hashlib.sha256(Path(notes['pages_path']).read_bytes()).hexdigest())
        text = pages[1]['text']
        offset = text.index(SECOND)
        self.assertIn(hashlib.sha256(text.encode('utf-8')).hexdigest(), obj['excerpt_locator'])
        self.assertIn(f'characters [{offset}, {offset + len(SECOND)})', obj['excerpt_locator'])
        self.assertEqual(text[offset:offset + len(SECOND)], obj['excerpt'])
        self.assertEqual(pages[2]['status'], 'no_text_extracted')
        self.assertTrue(any('3' in x and '不表示' in x for x in obj['limitations']))
        self.assertEqual(obj['human_review'], 'not_started')

    def test_empty_target_page_is_unknown(self):
        obj = self.collect(page=3)
        self.assertEqual(obj['evidence_type'], 'unknown_insufficient_coverage')
        self.assertIsNone(obj['excerpt'])
        self.assertEqual(obj['snapshot']['status'], 'saved')

    def test_excerpt_on_wrong_page_and_missing_excerpt(self):
        for index, ex in enumerate((CHINESE, '不存在的摘录')):
            with self.subTest(excerpt=ex):
                self.output = Path(self.tmp.name) / str(index)
                obj = self.collect(excerpt=ex)
                self.assertEqual(obj['evidence_type'], 'unknown_insufficient_coverage')
                self.assertIsNone(obj['excerpt_locator'])

    def test_out_of_range_page(self):
        obj = self.collect(page=10)
        self.assertEqual(obj['evidence_type'], 'unknown_insufficient_coverage')

    def test_corrupt_and_unsupported_pdf(self):
        with tempfile.TemporaryDirectory(dir=pdf.PDF_ROOT) as folder:
            for index, data in enumerate((b'not a pdf', b'%PDF-1.4\ncorrupt')):
                path = Path(folder) / f'{index}.pdf'
                path.write_bytes(data)
                self.output = Path(self.tmp.name) / str(index)
                obj = self.collect(source=str(path))
                self.assertEqual(obj['evidence_type'], 'unknown_insufficient_coverage')
                self.assertIsNone(obj['excerpt'])
                self.assertTrue(obj['limitations'])
                self.assertEqual(obj['snapshot']['status'], 'unavailable')
                self.assertIsNone(obj['snapshot']['path'])
                self.assertFalse((self.output / 'pages.json').exists())
                timing = json.loads((self.output / 'timing.json').read_text())
                self.assertGreaterEqual(timing['total_ms'], 0)

    def test_all_blank_pdf(self):
        with tempfile.TemporaryDirectory(dir=pdf.PDF_ROOT) as folder:
            path = Path(folder) / 'blank.pdf'
            path.write_bytes(make_pdf(['']))
            obj = self.collect(source=str(path), page=1)
            self.assertEqual(obj['evidence_type'], 'unknown_insufficient_coverage')
            self.assertIn('不表示', obj['claim'])

    def test_reject_roots_and_reports(self):
        for path in (ROOT / 'reports/private.pdf', ROOT / 'AGENTS.md', pdf.PDF_ROOT / '../outside.pdf'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.collect(source=str(path))
        self.assertFalse(self.output.exists())

    def test_existing_output_not_overwritten(self):
        self.output.mkdir()
        with self.assertRaises(FileExistsError):
            self.collect()

    def test_real_timings(self):
        self.collect()
        timing = json.loads((self.output / 'timing.json').read_text(encoding='utf-8'))
        self.assertEqual(timing['page_count'], 3)
        self.assertEqual(timing['input_bytes'], (pdf.PDF_ROOT / 'digital.pdf').stat().st_size)
        for key in ('bundle_load_ms', 'pdf_open_parse_ms', 'extraction_ms',
                    'snapshot_evidence_ms', 'validation_ms', 'total_ms'):
            self.assertGreaterEqual(timing[key], 0)
        self.assertEqual(len(timing['page_extraction_ms']), 3)
        self.assertTrue(all(x >= 0 for x in timing['page_extraction_ms']))
        self.assertGreaterEqual(timing['total_ms'], timing['extraction_ms'])

    def test_site_packages_disabled_cli(self):
        result = subprocess.run([sys.executable, '-E', '-S', str(ROOT / 'scripts/pdf_source.py'),
                                 str(pdf.PDF_ROOT / 'digital.pdf'), '--output', str(self.output),
                                 '--evidence-id', 'E-CLI-001', '--title', 'Synthetic', '--publisher', 'ADD',
                                 '--claim', 'Test statement', '--excerpt', SECOND, '--page', '2'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(validate_file(self.output / 'evidence.json'), [])
        timing = json.loads((self.output / 'timing.json').read_text())
        self.assertFalse(timing['pypdf_already_loaded'])
        self.assertEqual(timing['pypdf_version'], '6.19.0')

    def test_wheel_hash_mismatch_blocks_loading(self):
        with patch.object(pdf, 'WHEEL_HASH', '0' * 64), self.assertRaises(RuntimeError):
            self.collect()
        self.assertFalse(self.output.exists())

    def test_encrypted_input_is_rejected(self):
        module = pdf.load_pypdf()
        # Only an encrypted failure fixture, not a product PDF renderer.
        with tempfile.TemporaryDirectory(dir=pdf.PDF_ROOT) as folder:
            path = Path(folder) / 'encrypted.pdf'
            writer = module.PdfWriter()
            writer.add_blank_page(width=200, height=200)
            writer.encrypt('synthetic-secret')
            writer.write(path)
            obj = self.collect(source=str(path), page=1)
            self.assertEqual(obj['evidence_type'], 'unknown_insufficient_coverage')
            self.assertTrue(any('encrypted PDF unsupported' in x for x in obj['limitations']))

    def test_page_extraction_exception_is_a_gap(self):
        module = pdf.load_pypdf()
        with patch.object(module._page.PageObject, 'extract_text', side_effect=ValueError('synthetic page error')):
            obj = self.collect()
        self.assertEqual(obj['evidence_type'], 'unknown_insufficient_coverage')
        self.assertIsNone(obj['excerpt'])
        pages = json.loads((self.output / 'pages.json').read_text(encoding='utf-8'))
        self.assertTrue(all(x['status'] == 'extraction_error' and x['text'] is None for x in pages))


if __name__ == '__main__':
    unittest.main()
