"""Fresh-process real-contract smoke; only fabricated identities and source text."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from pdf_fixture import make_pdf
from test_research_run import metadata


def run(root):
    if not sys.flags.no_site:
        raise ValueError('use fresh Python -B -E -S')
    start = perf_counter()
    calls = []
    def cli(script, *args):
        command = [sys.executable, '-B', '-E', '-S', str(ROOT / 'scripts' / script), *map(str, args)]
        tick = perf_counter()
        result = subprocess.run(command, capture_output=True)
        calls.append(dict(command=command, exit_code=result.returncode, wall_ms=(perf_counter()-tick)*1000,
                          stdout=result.stdout.decode('utf-8', errors='replace'), stderr=result.stderr.decode('utf-8', errors='replace')))
        if result.returncode:
            raise RuntimeError(calls[-1])
    root = Path(root).absolute()
    with tempfile.TemporaryDirectory(dir=ROOT/'tests/fixtures', prefix='real-smoke-') as fixture:
        fixture = Path(fixture)
        raw = {'sample.html': '<p>合成测试文字</p>'.encode(),
               'sample.pdf': make_pdf(['合成测试文字'] * 151)}
        declarations = []
        for name, data in raw.items():
            path = fixture/name; path.write_bytes(data)
            declarations.append(dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), url=None))
        authorization=fixture/'authorization.json'
        authorization.write_text(json.dumps(declarations),encoding='utf-8')
        cli('research_run.py','create',root,'--authorization',authorization)
        try:
            (root/'metadata.json').write_text(json.dumps(metadata(),ensure_ascii=False),encoding='utf-8')
            for declaration in declarations:
                cli('research_run.py','stage',root,declaration['path'],'--sha256',declaration['sha256'])
            paths={Path(x['path']).suffix: root/'inputs'/(x['sha256']+'-'+Path(x['path']).name)/Path(x['path']).name for x in declarations}
            common=['--run-root',root,'--metadata',root/'metadata.json','--excerpt','合成测试文字']
            cli('static_source.py',paths['.html'],'--output',root/'static','--evidence-id','E-REAL-HTML',*common)
            cli('pdf_source.py',paths['.pdf'],'--output',root/'pdf','--evidence-id','E-REAL-PDF','--page','107',*common)
            evidence=[json.loads((root/name/'evidence.json').read_text(encoding='utf-8')) for name in ('static','pdf')]
            (root/'evidence.json').write_text(json.dumps(evidence,ensure_ascii=False),encoding='utf-8')
            cli('validate_evidence.py',root/'evidence.json')
            task=dict(title='真实运行合同：合成身份链路测试',scope='仅验证 real-mode plumbing，不研究任何真人。',
                      enabled_modules={key:key not in ('viewpoints','conflicts') for key in ('identity','background','publications','viewpoints','relationships','conflicts')},
                      assignments={'E-REAL-HTML':'background','E-REAL-PDF':'publications'})
            (root/'task.json').write_text(json.dumps(task,ensure_ascii=False),encoding='utf-8')
            cli('report.py',root/'evidence.json',root/'task.json','--output',root/'canonical','--run-root',root)
            cli('pdf_report.py',root/'canonical/report.json','--output',root/'rendered','--runtime',root/'.tmp-runtime','--run-root',root)
            for name in ('report.json','report.md','report.html'):
                assert (root/'canonical'/name).read_bytes()==(root/'rendered'/name).read_bytes(),name
            model=json.loads((root/'rendered/report.json').read_text(encoding='utf-8'))
            assert model['evidence']==evidence
            timing=json.loads((root/'rendered/timing.json').read_text(encoding='utf-8'))
            assert timing['content_consistent'] and timing['embedded_fonts']
            result=dict(result='PASS',evidence_count=len(evidence),pdf=timing,calls=calls,
                        total_wall_ms=(perf_counter()-start)*1000,synthetic_identity_only=True)
            (root/'smoke-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
            return result
        except Exception:
            (root/'smoke-failure.json').write_text(json.dumps(calls,ensure_ascii=False,indent=2),encoding='utf-8')
            raise


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run-root',required=True)
    result=run(parser.parse_args().run_root)
    print(json.dumps({key:result[key] for key in ('result','evidence_count','total_wall_ms')}))
