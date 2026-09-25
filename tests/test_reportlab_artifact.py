import base64
import csv
import hashlib
import io
import json
from pathlib import Path
import sys
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from derive_reportlab import derive, UPSTREAM_SHA256, ARTIFACT_NAME, EXCLUDED, RECORD
from pdf_bundle import WHEELS
from package_pdf_smoke import check_distribution


class ReportLabArtifactTests(unittest.TestCase):
    def test_pinned_derivation_and_record(self):
        m=json.loads((ROOT/'vendor/pdf/derivation.json').read_text())
        raw=(ROOT/'vendor/pdf'/ARTIFACT_NAME).read_bytes()
        self.assertEqual(m['upstream']['sha256'],UPSTREAM_SHA256)
        self.assertEqual(m['sha256'],WHEELS[ARTIFACT_NAME])
        self.assertEqual(hashlib.sha256(raw).hexdigest(),m['sha256'])
        self.assertEqual(len(raw),m['bytes'])
        self.assertEqual(set(EXCLUDED),{x['path'] for x in m['derivation']['excluded_files']})
        check_distribution(raw)
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            rows=list(csv.reader(io.StringIO(z.read(RECORD).decode())))
            self.assertEqual(set(z.namelist()),{row[0] for row in rows})
            for name,digest,size in rows:
                if name==RECORD:continue
                data=z.read(name)
                self.assertEqual(int(size),len(data))
                self.assertEqual(digest,'sha256='+base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b'=').decode())
            self.assertEqual(z.read('reportlab-4.4.10.dist-info/licenses/LICENSE'),(ROOT/'vendor/pdf/reportlab-LICENSE.txt').read_bytes())

    def test_wrong_derivation_input_rejected(self):
        with self.assertRaisesRegex(ValueError,'upstream.*hash'):
            derive(b'not the fixed upstream wheel')

    def test_package_check_rejects_original_wheel(self):
        raw=io.BytesIO()
        with zipfile.ZipFile(raw,'w') as z:
            z.writestr('vendor/pdf/reportlab-4.4.10-py3-none-any.whl',b'anything')
        with self.assertRaisesRegex(ValueError,'forbidden'):
            check_distribution(raw.getvalue())

    def test_package_check_rejects_nested_component(self):
        inner=io.BytesIO()
        with zipfile.ZipFile(inner,'w') as z:z.writestr('fonts/DarkGardenMK.pfb',b'font')
        outer=io.BytesIO()
        with zipfile.ZipFile(outer,'w') as z:z.writestr('runtime.zip',inner.getvalue())
        with self.assertRaisesRegex(ValueError,'forbidden'):
            check_distribution(outer.getvalue())

    def test_package_check_rejects_renamed_license(self):
        raw=io.BytesIO()
        with zipfile.ZipFile(raw,'w') as z:
            z.writestr('renamed.txt',b'Michal  Kosmulski\nGNU General Public License')
        with self.assertRaisesRegex(ValueError,'license'):
            check_distribution(raw.getvalue())


if __name__=='__main__':unittest.main()
