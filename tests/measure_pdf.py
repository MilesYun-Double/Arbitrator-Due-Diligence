"""One reproducible fixture timing run; not a performance service or SLA framework."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from pdf_source import PDF_ROOT, collect_pdf
from static_source import scoped_path
from pdf_fixture import SECOND


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    root = scoped_path(parser.parse_args().output, ROOT)
    root.mkdir(parents=True, exist_ok=False)
    source = PDF_ROOT / 'digital.pdf'
    results = []
    for index in range(3):
        output = root / f'cli-{index + 1}'
        command = [sys.executable, '-E', '-S', str(ROOT / 'scripts/pdf_source.py'), str(source),
                   '--output', str(output), '--evidence-id', f'E-COLD-{index + 1}',
                   '--title', '合成PDF', '--publisher', 'ADD tests', '--claim', '第二页合成声明',
                   '--excerpt', SECOND, '--page', '2']
        start = perf_counter()
        run = subprocess.run(command, capture_output=True, encoding='utf-8', errors='replace')
        elapsed = (perf_counter() - start) * 1000
        if run.returncode:
            raise RuntimeError(run.stdout + run.stderr)
        timing = json.loads((output / 'timing.json').read_text(encoding='utf-8'))
        results.append(dict(mode='fresh CLI (-E -S)', run=index + 1,
                            external_wall_ms=elapsed, **timing))
    # No warm-up is hidden: run 1 imports pypdf in this parent; runs 2/3 reuse it.
    for index in range(3):
        output = root / f'in-process-{index + 1}'
        collect_pdf(str(source), output, evidence_id=f'E-PROCESS-{index + 1}', title='合成PDF',
                    publisher='ADD tests', claim='第二页合成声明', excerpt=SECOND, page=2)
        timing = json.loads((output / 'timing.json').read_text(encoding='utf-8'))
        results.append(dict(mode='same process (first import included in run 1)', run=index + 1, **timing))
    report = dict(measurement='synthetic digital PDF only; not an arbitrator-task latency prediction',
                  command='python -E -S tests/measure_pdf.py --output <new project directory>',
                  python=platform.python_version(), platform=platform.platform(), machine=platform.machine(),
                  input='tests/fixtures/pdf_sources/digital.pdf', input_bytes=source.stat().st_size,
                  input_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  cache_note='No application result cache. Fresh processes do not clear OS filesystem caches.',
                  results=results)
    (root / 'baseline.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(root / 'baseline.json')


if __name__ == '__main__':
    main()
