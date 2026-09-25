import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import static_source as source
from validate_evidence import validate_file


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/redirect':
            self.send_response(302)
            self.send_header('Location', '/page')
            self.end_headers()
            return
        code = 404 if self.path == '/missing' else 200
        data = (b'User-agent: *\nDisallow: /blocked\n' if self.path == '/robots.txt'
                else (ROOT / 'tests/fixtures/static_sources/page.html').read_bytes())
        self.send_response(code)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


class StaticSourceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='.tmp-source-', dir=ROOT)
        self.addCleanup(self.tmp.cleanup)
        self.output = Path(self.tmp.name) / 'run'

    def run_source(self, value, **kwargs):
        options = dict(evidence_id='E-TEST-001', title='合成来源', publisher='合成发布者',
                       claim='来源记载合成机构成立于2020年。', excerpt='合成机构成立于2020年。',
                       evidence_type='source_supported_fact', level='L2')
        options.update(kwargs)
        return source.collect(value, self.output, **options)

    def valid(self, path):
        self.assertEqual(validate_file(path), [])
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/validate_evidence.py'), str(path)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads(path.read_text(encoding='utf-8'))

    def test_local_html_and_text(self):
        for name in ('page.html', 'source.txt'):
            with self.subTest(name=name):
                self.output = Path(self.tmp.name) / name
                path = self.run_source(str(source.TEST_ROOT / name))
                obj = self.valid(path)
                raw = Path(obj['snapshot']['path'])
                self.assertEqual(raw.read_bytes(), (source.TEST_ROOT / name).read_bytes())
                self.assertEqual(obj['snapshot']['sha256'], hashlib.sha256(raw.read_bytes()).hexdigest())
                self.assertIn('characters', obj['excerpt_locator'])
                text = (path.parent / 'readable.txt').read_text(encoding='utf-8')
                self.assertNotIn('throw new Error', text)
                self.assertEqual(obj['human_review'], 'not_started')
                self.assertEqual(obj['quality']['source_quality'], 'unknown')

    def server(self):
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        return f'http://127.0.0.1:{server.server_port}'

    def test_url_redirect_snapshot_evidence(self):
        url = self.server()
        # Only synthetic transport tests bypass public-address validation; no production switch.
        with patch.object(source, '_check_public_url'):
            path = self.run_source(url + '/redirect')
        obj = self.valid(path)
        ret = json.loads(obj['retrieval']['retrieval_notes'])
        self.assertEqual(ret['requested_url'], url + '/redirect')
        self.assertEqual(ret['final_url'], url + '/page')
        self.assertIn('text/html', ret['content_type'])
        self.assertTrue(obj['retrieval']['retrieved_at'])
        self.assertEqual(obj['snapshot']['status'], 'saved')

    def test_http_failure_and_robots_denial(self):
        url = self.server()
        for target in ('missing', 'blocked'):
            with self.subTest(target=target):
                self.output = Path(self.tmp.name) / target
                with patch.object(source, '_check_public_url'):
                    path = self.run_source(url + '/' + target)
                obj = self.valid(path)
                self.assertEqual(obj['evidence_type'], 'unknown_insufficient_coverage')
                self.assertEqual(obj['snapshot']['status'], 'unavailable')
                self.assertIsNone(obj['snapshot']['path'])
                self.assertIsNone(obj['excerpt'])
                self.assertEqual(list(path.parent.iterdir()), [path])
                self.assertIn('不表示', obj['claim'])

    def test_network_failure(self):
        from urllib.error import URLError
        with patch.object(source, '_fetch', side_effect=URLError('synthetic unavailable')):
            obj = self.valid(self.run_source('https://example.invalid/source'))
        self.assertIn('synthetic unavailable', ' '.join(obj['limitations']))

    def test_local_boundaries_before_read(self):
        for path in (ROOT / 'AGENTS.md', ROOT / 'reports/private.txt',
                     source.TEST_ROOT / '../outside.txt', source.TEST_ROOT / 'reports/no.txt'):
            with self.subTest(path=str(path)), self.assertRaises(ValueError):
                self.run_source(str(path))
        self.assertFalse(self.output.exists())

    def test_public_url_guard(self):
        for url in ('file:///etc/passwd', 'http://user:pass@example.com', 'http://127.0.0.1/a',
                    'http://[::1]/a'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                source._check_public_url(url)

    def test_redirect_guard(self):
        from urllib.request import Request
        with self.assertRaises(ValueError):
            source.SafeRedirect().redirect_request(Request('https://example.com'), None, 302,
                                                  'Found', {}, 'http://127.0.0.1/private')

    def test_l0_l1_and_lead(self):
        for level in ('L0', 'L1'):
            with self.subTest(level=level):
                self.output = Path(self.tmp.name) / level
                obj = self.valid(self.run_source(str(source.TEST_ROOT / 'page.html'), level=level,
                                                evidence_type='unresolved_lead'))
                self.assertEqual(obj['snapshot']['level'], level)
                self.assertIsNone(obj['snapshot']['path'])
                self.assertEqual(list(self.output.iterdir()), [self.output / 'evidence.json'])
                self.assertEqual(obj['excerpt'] is None, level == 'L0')

    def test_excerpt_mismatch_does_not_assert_fact(self):
        obj = self.valid(self.run_source(str(source.TEST_ROOT / 'source.txt'), excerpt='不存在的原文'))
        self.assertEqual(obj['evidence_type'], 'unknown_insufficient_coverage')
        self.assertIsNone(obj['excerpt'])

    def test_no_overwrite(self):
        self.output.mkdir()
        with self.assertRaises(FileExistsError):
            self.run_source(str(source.TEST_ROOT / 'source.txt'))

    def test_unsupported_type_and_encoding(self):
        for media, raw in (('application/pdf', b'%PDF'), ('text/plain; charset=utf-8', b'\xff')):
            with self.subTest(media=media), self.assertRaises(ValueError):
                source.readable(raw, media)

    def test_size_limit(self):
        import io
        with self.assertRaises(ValueError):
            source._bounded_read(io.BytesIO(b'x' * (source.MAX_BYTES + 1)))

    def test_link_and_output_boundaries(self):
        # Hard links need no Windows symlink privilege and exercise pre-read rejection.
        import os
        with tempfile.TemporaryDirectory(dir=source.TEST_ROOT) as folder:
            link = Path(folder) / 'linked.txt'
            os.link(source.TEST_ROOT / 'source.txt', link)
            try:
                with self.assertRaises(ValueError):
                    self.run_source(str(link))
            finally:
                link.unlink()
        self.output = ROOT / 'reports' / 'must-not-write'
        with self.assertRaises(ValueError):
            self.run_source(str(source.TEST_ROOT / 'source.txt'))

    def test_credential_url_is_rejected_without_artifact(self):
        with self.assertRaises(ValueError):
            self.run_source('https://user:password@example.com/test')
        self.assertFalse(self.output.exists())

    def test_locator_and_derived_hash_are_reproducible(self):
        path = self.run_source(str(source.TEST_ROOT / 'page.html'))
        obj = self.valid(path)
        notes = json.loads(obj['snapshot']['notes'])
        raw = Path(notes['readable_path']).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), notes['readable_sha256'])
        text = raw.decode('utf-8')
        offset = text.index(obj['excerpt'])
        self.assertIn(f'[{offset}, {offset + len(obj["excerpt"])})', obj['excerpt_locator'])

    def test_unknown_coverage_success_is_not_upgraded(self):
        obj = self.valid(self.run_source(str(source.TEST_ROOT / 'source.txt'),
                                        evidence_type='unknown_insufficient_coverage'))
        self.assertEqual(obj['evidence_type'], 'unknown_insufficient_coverage')

    def test_ads_and_windows_aliases_are_rejected(self):
        for name in ('.tmp-file:secret.txt', 'reports./private.txt', '.env.txt'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                source.scoped_path(source.TEST_ROOT / name, source.TEST_ROOT)

    def test_reparse_point_rejected(self):
        from types import SimpleNamespace
        import stat
        info = SimpleNamespace(st_mode=stat.S_IFDIR, st_file_attributes=0x400)
        with patch.object(Path, 'lstat', return_value=info), self.assertRaises(ValueError):
            source.scoped_path(source.TEST_ROOT / 'page.html', source.TEST_ROOT)


if __name__ == '__main__':
    unittest.main()
