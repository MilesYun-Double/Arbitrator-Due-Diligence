"""Relocate the full synthetic capability chain; test normal and no-Pillow closure."""
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
from package_pdf_smoke import check_distribution


def package(output):
    output=scoped_path(output,ROOT);output.mkdir(parents=True,exist_ok=False)
    names=['LICENSE','scripts/static_source.py','scripts/pdf_source.py','scripts/validate_evidence.py',
           'scripts/report.py','scripts/pdf_report.py','scripts/pdf_bundle.py',
           'schemas/evidence.schema.json','references/snapshot-policy.md','references/bundled-baseline.md',
           'tests/synthetic_chain.py','tests/fixtures/static_sources/page.html',
           'tests/fixtures/static_sources/source.txt','tests/fixtures/pdf_sources/digital.pdf',
           'vendor/pypdf-6.19.0-py3-none-any.whl','vendor/pypdf-LICENSE.txt','vendor/README.md']
    names+=['vendor/pdf/'+n for n in [*WHEELS,'LXGWWenKai-Regular.ttf','LXGWWenKai-OFL.txt',
            'reportlab-LICENSE.txt','pillow-LICENSE.txt','charset_normalizer-LICENSE.txt',
            'bitstream-vera-LICENSE.txt','README.md','upstream.json','derivation.json']]
    results=[]
    for absent in (False,True):
        selected=[n for n in names if not (absent and (Path(n).name.startswith('pillow-')))]
        label='without-pillow' if absent else 'baseline'
        archive=output/(label+'.zip')
        with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED) as z:
            for n in selected:z.write(scoped_path(ROOT/n,ROOT),n)
        closure=check_distribution(archive.read_bytes())
        relocated=output/label;relocated.mkdir()
        with zipfile.ZipFile(archive) as z:
            for member in z.infolist():
                scoped_path(relocated/member.filename,relocated)
                z.extract(member,relocated)
        command=[sys.executable,'-B','-E','-S','tests/synthetic_chain.py','--run-root','.tmp-add-run-smoke']
        if absent:command+=['--without-pillow']
        start=perf_counter();proc=subprocess.run(command,cwd=relocated,capture_output=True,text=True)
        elapsed=(perf_counter()-start)*1000
        result=json.loads((relocated/'.tmp-add-run-smoke/chain-result.json').read_text(encoding='utf-8'))
        if absent:
            if proc.returncode!=3 or result['pil_loaded'] or set(result['pil_import_attempts'])!={'PIL'} or 'from PIL import Image' not in result.get('traceback',''):
                raise ValueError('unexpected no-Pillow experiment; inspect raw evidence')
        elif proc.returncode or result['result']!='PASS':raise ValueError(proc.stdout+proc.stderr+str(result))
        record=dict(mode=label,zip_bytes=archive.stat().st_size,zip_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),uncompressed_package_bytes=sum((ROOT/n).stat().st_size for n in selected),files=selected,closure_check=closure,command=command[1:],fresh_process_wall_ms=elapsed,exit_code=proc.returncode,chain=result)
        results.append(record)
    summary=dict(pillow='REQUIRED',finding='PLATFORM_DEPENDENCY_CONFIRMED',results=results)
    (output/'package-result.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return summary


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True)
    package(p.parse_args().output)
