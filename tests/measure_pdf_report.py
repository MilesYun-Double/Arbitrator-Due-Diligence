"""Fresh CLI and same-process PDF timings, with explicit fresh runtime unpacking."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from time import perf_counter
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from pdf_report import generate_pdf
from static_source import scoped_path


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True)
    root=scoped_path(p.parse_args().output,ROOT);root.mkdir(parents=True,exist_ok=False)
    model=ROOT/'tests/fixtures/pdf_reports/model.json'
    runtime=root/'.tmp-runtime'
    command=[sys.executable,'-B','-E','-S',str(ROOT/'scripts/pdf_report.py'),str(model),'--output',str(root/'cli'),'--runtime',str(runtime)]
    start=perf_counter();run=subprocess.run(command,capture_output=True,text=True);wall=(perf_counter()-start)*1000
    if run.returncode:raise RuntimeError(run.stdout+run.stderr)
    t=json.loads((root/'cli/timing.json').read_text(encoding='utf-8'))
    results=[dict(mode='fresh CLI, new runtime',external_wall_ms=wall,**t)]
    for i in range(2):
        results.append(dict(mode=f'same process {i+1}, explicitly reused unpacked runtime',**generate_pdf(model,root/f'process-{i+1}',runtime)))
    for name in ('report.json','report.md','report.html','report.pdf'):
        if (root/'cli'/name).read_bytes()!=(root/'process-1'/name).read_bytes() or (root/'cli'/name).read_bytes()!=(root/'process-2'/name).read_bytes():
            raise ValueError('repeated report output differs')
    (root/'baseline.json').write_text(json.dumps({'results':results,'deterministic_artifacts':True,'note':'No hidden warmup. Fresh CLI unpacks wheels. OS cache not flushed.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(root/'baseline.json')


if __name__=='__main__':main()
