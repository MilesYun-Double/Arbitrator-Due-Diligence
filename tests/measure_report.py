"""Reproduce one fresh CLI and two same-process report timings, without hidden warmup."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from report import INPUT_ROOT, generate
from static_source import scoped_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    root = scoped_path(parser.parse_args().output, ROOT)
    root.mkdir(parents=True, exist_ok=False)
    inputs = [str(INPUT_ROOT / 'evidence.json'), str(INPUT_ROOT / 'task.json')]
    command = [sys.executable, '-E', '-S', str(ROOT / 'scripts/report.py'), *inputs, '--output', str(root / 'cli')]
    start = perf_counter()
    run = subprocess.run(command, capture_output=True, text=True)
    wall = (perf_counter() - start) * 1000
    if run.returncode: raise RuntimeError(run.stdout + run.stderr)
    timing = json.loads((root / 'cli/timing.json').read_text(encoding='utf-8'))
    results = [dict(mode='fresh CLI (-E -S)', external_wall_ms=wall, **timing)]
    for i in range(2):
        results.append(dict(mode=f'same process {i + 1} (no hidden warmup)',
                            **generate(*inputs, root / f'process-{i + 1}')))
    baseline = dict(command='python -E -S tests/measure_report.py --output <new directory>',
                    note='Synthetic 6-Evidence sample only; no OS cache flush, no SLA', results=results)
    (root / 'baseline.json').write_text(json.dumps(baseline, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(root / 'baseline.json')


if __name__ == '__main__': main()
