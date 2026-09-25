"""Build and execute a minimal relocated PDF capability ZIP, not a full Skill release."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from time import perf_counter
import zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from static_source import scoped_path
from pdf_bundle import WHEELS


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
    root=scoped_path(parser.parse_args().output,ROOT);root.mkdir(parents=True,exist_ok=False)
    names=['LICENSE','scripts/report.py','scripts/static_source.py','scripts/validate_evidence.py',
           'scripts/pdf_source.py','scripts/pdf_bundle.py','scripts/pdf_report.py',
           'references/pdf-renderer.md','tests/fixtures/pdf_reports/model.json',
           'vendor/pypdf-6.19.0-py3-none-any.whl','vendor/pypdf-LICENSE.txt','vendor/README.md']
    names += ['vendor/pdf/'+n for n in [*WHEELS,'LXGWWenKai-Regular.ttf','LXGWWenKai-OFL.txt',
              'reportlab-LICENSE.txt','pillow-LICENSE.txt','charset_normalizer-LICENSE.txt',
              'bitstream-vera-LICENSE.txt','README.md','upstream.json']]
    archive=root/'pdf-capability-candidate.zip'
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED) as z:
        for name in names:z.write(scoped_path(ROOT/name,ROOT),name)
    relocated=root/'relocated';relocated.mkdir()
    with zipfile.ZipFile(archive) as z:
        for info in z.infolist():
            scoped_path(relocated/info.filename,relocated)
            z.extract(info,relocated)
    command=[sys.executable,'-B','-E','-S','scripts/pdf_report.py','tests/fixtures/pdf_reports/model.json',
             '--output','.tmp-result','--runtime','.tmp-runtime']
    start=perf_counter();run=subprocess.run(command,cwd=relocated,capture_output=True,text=True);wall=(perf_counter()-start)*1000
    if run.returncode:raise RuntimeError(run.stdout+run.stderr)
    t=json.loads((relocated/'.tmp-result/timing.json').read_text(encoding='utf-8'))
    result=dict(zip_bytes=archive.stat().st_size,zip_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
                uncompressed_package_bytes=sum((ROOT/n).stat().st_size for n in names),file_count=len(names),
                files=names,command=command[1:],external_wall_ms=wall,timing=t,
                result='PASS: relocated package CLI with site-packages disabled; not a full Skill ZIP')
    (root/'packaging.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(root/'packaging.json')


if __name__=='__main__':main()
