from copy import deepcopy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch
import uuid

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from static_source import task_run_root, scoped_path, collect
from pdf_source import collect_pdf
import report
import pdf_report
from package_synthetic_smoke import package


class RunBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.root=ROOT/('.tmp-add-run-test-'+uuid.uuid4().hex)
        task_run_root(self.root,create=True)
    def tearDown(self):
        assert self.root.parent==ROOT and self.root.name.startswith('.tmp-add-run-test-')
        shutil.rmtree(self.root)
    def test_task_root_and_no_overwrite(self):
        self.assertEqual(task_run_root(self.root),self.root)
        with self.assertRaises(FileExistsError):task_run_root(self.root,create=True)
    def test_root_outside_reports_and_missing_contract_rejected(self):
        for root in (ROOT.parent/'.tmp-add-run-outside',ROOT/'reports/.tmp-add-run-no',ROOT/'tests',ROOT/'.tmp-add-run-absent'):
            with self.assertRaises((ValueError,OSError)):task_run_root(root)
    def test_module_inputs_and_outputs_stay_in_run(self):
        source=self.root/'source.txt';source.write_text('synthetic',encoding='utf-8')
        kwargs=dict(evidence_id='E-RUN-1',title='Synthetic',publisher='ADD',claim='synthetic',run_root=self.root)
        for path in (ROOT/'tests/fixtures/static_sources/source.txt',ROOT/'reports/secret.txt'):
            with self.assertRaises(ValueError):collect(str(path),self.root/'out',**kwargs)
        with self.assertRaises(ValueError):collect(str(source),ROOT/'.tmp-outside-run',**kwargs)
        with self.assertRaises(ValueError):collect('https://example.invalid',self.root/'out',**kwargs)
        with self.assertRaises(ValueError):collect_pdf(ROOT/'tests/fixtures/pdf_sources/digital.pdf',self.root/'pdf',excerpt='a',page=1,**kwargs)
        with self.assertRaises(ValueError):report.generate(ROOT/'tests/fixtures/report_sources/evidence.json',self.root/'task.json',self.root/'report',run_root=self.root)
        with self.assertRaises(ValueError):pdf_report.generate_pdf(ROOT/'tests/fixtures/pdf_reports/model.json',self.root/'pdf',self.root/'.tmp-runtime',run_root=self.root)
    def test_snapshot_outside_run_rejected_before_read(self):
        source=self.root/'source.txt';source.write_text('synthetic',encoding='utf-8')
        path=collect(str(source),self.root/'collected',evidence_id='E-RUN-1',title='Synthetic',publisher='ADD',claim='synthetic',run_root=self.root)
        item=json.loads(path.read_text(encoding='utf-8'))
        report.validate_inputs([item],self.root,run_root=self.root)
        item['snapshot']['path']=str(ROOT/'reports/secret.pdf')
        with self.assertRaises(ValueError):report.validate_inputs([item],self.root,run_root=self.root)
    def test_reparse_guard_applies_to_run(self):
        original=Path.lstat
        def fake(path):
            result=original(path)
            if path==self.root:
                class Reparse:
                    st_mode=result.st_mode
                    st_file_attributes=1024
                    st_nlink=1
                return Reparse()
            return result
        with patch.object(Path,'lstat',fake),self.assertRaisesRegex(ValueError,'reparse'):
            task_run_root(self.root)


class SyntheticPackageTests(unittest.TestCase):
    def test_real_collectors_relocated_chain_and_pillow_failure(self):
        with tempfile.TemporaryDirectory(prefix='.tmp-chain-test-',dir=ROOT) as folder:
            result=package(Path(folder)/'package')
            baseline,absent=result['results']
            self.assertEqual(baseline['chain']['result'],'PASS')
            self.assertEqual(result['pillow'],'REQUIRED')
            self.assertFalse(absent['chain']['pil_loaded'])
            self.assertTrue(absent['chain']['pil_import_attempts'])
            self.assertEqual(baseline['chain']['evidence_count'],3)
            self.assertTrue(baseline['chain']['content_consistent'])
            for row in result['results']:
                self.assertTrue(row['chain']['site_disabled'])
                self.assertGreater(row['zip_bytes'],0)
                self.assertGreater(row['uncompressed_package_bytes'],0)
                self.assertGreater(row['fresh_process_wall_ms'],0)
                self.assertTrue(all(value>=0 for value in row['chain']['timing'].values()))
                for origin in row['chain']['loaded_product_modules'].values():
                    self.assertNotIn('site-packages',origin)
                    self.assertTrue(Path(origin).is_relative_to(Path(folder)))
            root=Path(folder)/'package/baseline/.tmp-add-run-smoke'
            items=json.loads((root/'evidence.json').read_text(encoding='utf-8'))
            for item,name in zip(items,('html-source','text-source','pdf-source')):
                self.assertEqual(item,json.loads((root/name/'evidence.json').read_text(encoding='utf-8')))


if __name__=='__main__':unittest.main()
