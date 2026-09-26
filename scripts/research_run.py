"""Explicit task scope, not OS authorization; never infer permission from location."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re

from static_source import PROJECT, _checked_path, scoped_path, task_run_root
from validate_evidence import validate_evidence

MARKER = 'research-run.json'
SCOPE = 'ADD authorized research run'
MAX_INPUT_BYTES = 10 * 1024 * 1024


def _root(value):
    root = Path(os.path.abspath(value))
    if root.parent != PROJECT / 'reports' or root.name.startswith('.'):
        raise ValueError('real root must be a direct reports child')
    return _checked_path(value, PROJECT, reports_root=root)


def input_path(value, *, current_run=None):
    """Exact declared file only, inside project fixtures or legacy reports.

    Active sibling research runs are never staging sources. No directory scans.
    """
    path = Path(os.path.abspath(value))
    reports = PROJECT / 'reports'
    if current_run is not None and path.is_relative_to(current_run / 'incoming'):
        path = _checked_path(value, current_run, reports_root=current_run)
    elif path.is_relative_to(reports):
        path = _checked_path(value, reports, reports_root=reports)
        for parent in path.parents:
            if parent == reports:
                break
            if (parent / MARKER).exists():
                raise ValueError('cannot stage from a research run')
    else:
        path = scoped_path(value, PROJECT / 'tests' / 'fixtures')
    if path.suffix.lower() not in ('.pdf', '.txt', '.html', '.htm'):
        raise ValueError('unsupported staged input type')
    return path


def _declarations(items, root):
    if not isinstance(items, list):
        raise ValueError('authorized_inputs must be an explicit list')
    seen = set()
    for item in items:
        if (not isinstance(item, dict) or set(item) != {'path', 'sha256', 'url'}
                or not isinstance(item['path'], str) or not Path(item['path']).is_absolute()
                or not isinstance(item['sha256'], str) or not re.fullmatch('[0-9a-f]{64}', item['sha256'])
                or (item['url'] is not None and not isinstance(item['url'], str))):
            raise ValueError('input requires absolute path, lowercase SHA-256 and URL or null')
        source = input_path(item['path'], current_run=root)
        if str(source) in seen:
            raise ValueError('duplicate authorized input')
        seen.add(str(source))


def real_run_root(value, *, create=False, authorized_inputs=None):
    root = _root(value)
    marker = _checked_path(root / MARKER, root, reports_root=root)
    if create:
        _declarations(authorized_inputs, root)
        authorized_inputs = [dict(item, path=str(input_path(item['path'], current_run=root)))
                             for item in authorized_inputs]
        root.parent.mkdir(exist_ok=True)
        root.mkdir(exist_ok=False)
        contract = dict(scope=SCOPE, version=1, authorized_inputs=authorized_inputs)
        with marker.open('x', encoding='utf-8') as stream:
            json.dump(contract, stream, ensure_ascii=False, indent=2)
    else:
        contract = json.loads(marker.read_text(encoding='utf-8'))
        if (not isinstance(contract, dict) or set(contract) != {'scope', 'version', 'authorized_inputs'}
                or contract['scope'] != SCOPE or type(contract['version']) is not int or contract['version'] != 1):
            raise ValueError('invalid real research contract')
        _declarations(contract['authorized_inputs'], root)
    return root


def resolve_run(value):
    path = Path(os.path.abspath(value))
    return real_run_root(value) if path.is_relative_to(PROJECT / 'reports') else task_run_root(value)


def is_real(root):
    return root is not None and root.parent == PROJECT / 'reports'


def run_path(value, root):
    if is_real(root):
        root = real_run_root(root)
        return _checked_path(value, root, reports_root=root)
    return scoped_path(value, root)


def stage_input(root, source, expected_sha256):
    root = real_run_root(root)
    source = input_path(source, current_run=root)
    contract = json.loads((root / MARKER).read_text(encoding='utf-8'))
    matches = [x for x in contract['authorized_inputs']
               if Path(x['path']) == source and x['sha256'] == expected_sha256]
    if len(matches) != 1:
        raise ValueError('input path/hash not explicitly authorized by this run')
    with source.open('rb') as stream:
        raw = stream.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise ValueError('staging exceeds 10 MiB')
    actual = hashlib.sha256(raw).hexdigest()
    if actual != expected_sha256:
        raise ValueError('staging SHA-256 mismatch')
    folder = run_path(root / 'inputs' / (actual + '-' + source.name), root)
    folder.mkdir(parents=True, exist_ok=False)
    target = folder / source.name
    with target.open('xb') as stream:
        stream.write(raw)
    record = dict(original_path=str(source), original_url=matches[0]['url'],
                  expected_sha256=expected_sha256, actual_sha256=actual,
                  copied_at=datetime.now(timezone.utc).isoformat(), staged_path=str(target),
                  note='Byte identity only; staging does not establish source authenticity.')
    (folder / 'staging.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    return target


def staged_input(value, root):
    path = run_path(value, root)
    if not path.is_relative_to(root / 'inputs'):
        raise ValueError('local collector input must be staged')
    record_path = run_path(path.parent / 'staging.json', root)
    record = json.loads(record_path.read_text(encoding='utf-8'))
    if record.get('staged_path') != str(path) or record.get('expected_sha256') != record.get('actual_sha256'):
        raise ValueError('invalid staging record')
    contract = json.loads((root / MARKER).read_text(encoding='utf-8'))
    declared = dict(path=record.get('original_path'), sha256=record.get('expected_sha256'), url=record.get('original_url'))
    if declared not in contract['authorized_inputs']:
        raise ValueError('staging record not authorized by run contract')
    original = Path(declared['path'])
    expected_path = root / 'inputs' / (declared['sha256'] + '-' + original.name) / original.name
    if path != expected_path:
        raise ValueError('staged location does not match declaration')
    with path.open('rb') as stream:
        raw = stream.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES or hashlib.sha256(raw).hexdigest() != record['actual_sha256']:
        raise ValueError('staged content changed')
    return path


def real_metadata(path, root, evidence_id, excerpt, local=None, url=None):
    value = json.loads(run_path(path, root).read_text(encoding='utf-8'))
    keys = {'subject', 'evidence_type', 'claim', 'source', 'identity_resolution', 'quality',
            'supports', 'context', 'limitations', 'uncertainty', 'human_review'}
    if not isinstance(value, dict) or set(value) != keys:
        raise ValueError('explicit real Evidence metadata fields required')
    obj = deepcopy(value)
    if not isinstance(obj['source'], dict) or 'local_path' in obj['source']:
        raise ValueError('source.local_path is collector-owned')
    obj['source']['local_path'] = str(local) if local else None
    if url is not None and obj['source'].get('url') != url:
        raise ValueError('metadata source URL must match requested URL')
    obj.update(evidence_id=evidence_id, retrieval={'retrieved_at': datetime.now(timezone.utc).isoformat()},
               excerpt=excerpt, excerpt_locator='pending collector verification' if excerpt else None,
               snapshot={'level': 'L0', 'status': 'not_saved'})
    errors = validate_evidence(obj)
    if errors:
        raise ValueError('; '.join(errors))
    return obj


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='action', required=True)
    create = subs.add_parser('create'); create.add_argument('root'); create.add_argument('--authorization', required=True)
    stage = subs.add_parser('stage'); stage.add_argument('root'); stage.add_argument('source'); stage.add_argument('--sha256', required=True)
    args = parser.parse_args()
    try:
        if args.action == 'create':
            # Control input itself remains within the ordinary non-research path policy.
            declaration = json.loads(scoped_path(args.authorization, PROJECT).read_text(encoding='utf-8'))
            print(real_run_root(args.root, create=True, authorized_inputs=declaration))
        else:
            print(stage_input(args.root, args.source, args.sha256))
        return 0
    except (OSError, ValueError) as exc:
        print(f'ERROR: {exc}'); return 2


if __name__ == '__main__':
    raise SystemExit(main())
