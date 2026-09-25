from copy import deepcopy
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import report


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.values = []
        self.tags = []
        self.rows = []
        self.current = None
    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))
        if tag == 'dd': self.current = ''
    def handle_data(self, data):
        self.values.append(data)
        if self.current is not None: self.current += data
    def handle_endtag(self, tag):
        if tag == 'dd':
            self.rows.append(self.current)
            self.current = None


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.evidence = json.loads((report.INPUT_ROOT / 'evidence.json').read_text(encoding='utf-8'))
        self.task = json.loads((report.INPUT_ROOT / 'task.json').read_text(encoding='utf-8'))

    def model(self):
        report.validate_inputs(self.evidence, report.INPUT_ROOT)
        return report.build_model(self.evidence, self.task)

    def test_multiple_evidence_and_states_preserved(self):
        model = self.model()
        self.assertEqual(model['evidence'], self.evidence)
        self.assertEqual(len(model['evidence']), 6)
        self.assertTrue({'public_viewpoint', 'relationship_fact', 'unresolved_lead',
                         'unknown_insufficient_coverage', 'derived_interpretation'} <=
                        {e['evidence_type'] for e in model['evidence']})
        self.evidence[0]['claim'] = 'changed after construction'
        self.assertNotEqual(model['evidence'][0]['claim'], self.evidence[0]['claim'])

    def test_shared_content_consistency(self):
        model = self.model()
        md, html = report.render_markdown(model), report.render_html(model)
        parsed = Text(); parsed.feed(html)
        text = ''.join(parsed.values)
        for e in self.evidence:
            for value in (e['evidence_id'], e['claim'], e['evidence_type'], e['human_review'],
                          e['source']['title'], e['source']['url'], *e['limitations']):
                self.assertIn(report.md_text(value), md)
                self.assertIn(value, text)
        self.assertEqual({e['evidence_id'] for e in self.evidence},
                         {a['id'][9:] for t, a in parsed.tags if a.get('id', '').startswith('evidence-')})
        self.assertIn('来源索引', md)
        self.assertIn('覆盖与限制', text)
        expected_rows = [v for _, _, _, rows in report.blocks(model) for _, v in rows]
        self.assertEqual(parsed.rows, expected_rows)
        # All rows, including complete source-index and limitation rows, appear
        # in exactly the same order in Markdown (not merely a subset of IDs).
        md_rows = [line.split('**：', 1)[1] for line in md.splitlines() if line.startswith('- **')]
        expected_md = []
        for _, _, _, rows in report.blocks(model):
            for label, value in rows:
                display = report.md_text(value)
                if label.endswith('.url') and report.safe_url(value):
                    display = f'[{display}]({report.quote(value, safe=":/?#[]@!$&*,;=%")})'
                expected_md.append(display)
        self.assertEqual(md_rows, expected_md)

    def test_disabled_module_and_no_false_conflict(self):
        model = self.model()
        self.assertEqual(model['sections'][-1]['status'], '未执行')
        for result in (report.render_markdown(model), report.render_html(model)):
            self.assertIn('未进行针对具体案件主体的关系比对', result)
            self.assertNotIn('本案无冲突', result)

    def test_disabled_assignments_and_missing_ids_rejected(self):
        for change in ('disabled', 'missing', 'extra'):
            task = deepcopy(self.task)
            if change == 'disabled': task['assignments']['E-REPORT-1'] = 'conflicts'
            if change == 'missing': del task['assignments']['E-REPORT-1']
            if change == 'extra': task['assignments']['E-ABSENT'] = 'identity'
            with self.subTest(change=change), self.assertRaises(ValueError):
                report.build_model(self.evidence, task)

    def test_invalid_and_duplicate_evidence_rejected(self):
        for items in ([*self.evidence, self.evidence[0]], [{}], []):
            with self.subTest(items=len(items)), self.assertRaises(ValueError):
                report.validate_inputs(items, report.INPUT_ROOT)

    def test_html_and_markdown_injection(self):
        attack = '<script>alert(1)</script><img src=x onerror=alert(2)> & "quote"\n# injected'
        self.evidence[0]['claim'] = attack
        self.evidence[0]['source']['url'] = 'javascript://alert(1)'
        model = self.model()
        html = report.render_html(model)
        parsed = Text(); parsed.feed(html)
        self.assertIn(attack, ''.join(parsed.values))
        self.assertFalse(any(t in ('script', 'img', 'iframe', 'link') for t, _ in parsed.tags))
        self.assertFalse(any(a.get('href', '').startswith('javascript:') for _, a in parsed.tags))
        self.assertNotIn('<script>', report.render_markdown(model))
        self.assertNotIn('\n# injected', report.render_markdown(model))

    def test_deterministic_no_mutation_no_io(self):
        model = self.model()
        before = deepcopy(model)
        with patch('socket.socket', side_effect=AssertionError('network')), patch('builtins.open', side_effect=AssertionError('IO')):
            self.assertEqual(report.render_markdown(model), report.render_markdown(model))
            self.assertEqual(report.render_html(model), report.render_html(model))
        self.assertEqual(model, before)
        self.assertEqual(report.build_model(self.evidence, self.task), model)

    def test_snapshot_outside_root_rejected_before_validator_read(self):
        self.evidence[0]['snapshot'].update(path=str(ROOT / 'reports' / 'private.pdf'), status='saved')
        with self.assertRaises(ValueError):
            report.validate_inputs(self.evidence, report.INPUT_ROOT)

    def test_task_metadata_checked(self):
        self.task['enabled_modules']['viewpoints'] = 'false'
        with self.assertRaises(ValueError): self.model()

    def test_enabled_conflicts_and_empty_modules(self):
        self.task['enabled_modules']['conflicts'] = True
        self.task['assignments']['E-REPORT-3'] = 'conflicts'
        model = self.model()
        self.assertEqual(model['sections'][-1]['evidence_ids'], ['E-REPORT-3'])
        self.assertEqual(model['sections'][-2]['status'], '未提供证据 / unknown')
        self.assertNotIn('未进行针对具体案件主体的关系比对', report.render_html(model))

    def test_metadata_and_url_attribute_escaping(self):
        self.task['title'] = '<img src=x onerror=alert(1)> title'
        self.evidence[0]['source']['url'] = 'https://example.invalid/"onmouseover="alert(1)'
        parsed = Text(); parsed.feed(report.render_html(self.model()))
        self.assertFalse(any(t == 'img' or 'onmouseover' in attrs for t, attrs in parsed.tags))
        self.assertTrue(all(not attrs.get('href', '').startswith(('file:', 'javascript:')) for _, attrs in parsed.tags))

    def test_invalid_pipeline_creates_no_report(self):
        with tempfile.TemporaryDirectory(dir=report.INPUT_ROOT) as source_dir, tempfile.TemporaryDirectory(prefix='.tmp-report-', dir=ROOT) as out_dir:
            source = Path(source_dir) / 'invalid.json'
            source.write_text('[{}]', encoding='utf-8')
            output = Path(out_dir) / 'out'
            with self.assertRaises(ValueError):
                report.generate(source, report.INPUT_ROOT / 'task.json', output)
            self.assertFalse(output.exists())

    def test_pipeline_outputs_timing_and_no_overwrite(self):
        with tempfile.TemporaryDirectory(prefix='.tmp-report-', dir=ROOT) as folder:
            output = Path(folder) / 'out'
            timing = report.generate(report.INPUT_ROOT / 'evidence.json', report.INPUT_ROOT / 'task.json', output)
            model = json.loads((output / 'report.json').read_text(encoding='utf-8'))
            self.assertEqual((output / 'report.md').read_text(encoding='utf-8'), report.render_markdown(model))
            self.assertEqual((output / 'report.html').read_text(encoding='utf-8'), report.render_html(model))
            self.assertEqual(timing['evidence_count'], 6)
            for key in ('validation_ms', 'model_ms', 'markdown_ms', 'html_ms', 'total_ms'):
                self.assertGreaterEqual(timing[key], 0)
            for name, size in timing['output_bytes'].items():
                self.assertEqual((output / name).stat().st_size, size)
            with self.assertRaises(FileExistsError):
                report.generate(report.INPUT_ROOT / 'evidence.json', report.INPUT_ROOT / 'task.json', output)


if __name__ == '__main__': unittest.main()
