#!/usr/bin/env python3
"""Local digital PDF extraction with page evidence and explicit timing (no OCR)."""
import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import platform
import sys
from time import perf_counter

from static_source import PROJECT, scoped_path, task_run_root
from validate_evidence import validate_evidence, validate_file

PDF_ROOT = PROJECT / 'tests' / 'fixtures' / 'pdf_sources'
WHEEL = PROJECT / 'vendor' / 'pypdf-6.19.0-py3-none-any.whl'
WHEEL_HASH = '7e5d6e730e7dae87d560a2cee218b852f6498c8be61966f3cd02ead971e48d14'
MAX_BYTES = 10 * 1024 * 1024
MAX_PAGES = 100


def load_pypdf():
    """Load the fixed shipped wheel, never install or fall back to a global copy."""
    if sys.version_info < (3, 11):
        raise RuntimeError('PDF capability requires host Python >=3.11; no automatic installation')
    wheel = scoped_path(WHEEL, PROJECT)
    if hashlib.sha256(wheel.read_bytes()).hexdigest() != WHEEL_HASH:
        raise RuntimeError('bundled pypdf hash mismatch')
    if str(wheel) not in sys.path:
        sys.path.insert(0, str(wheel))
    import pypdf
    normalized = str(pypdf.__file__).replace('\\', '/')
    if pypdf.__version__ != '6.19.0' or not normalized.startswith(str(wheel).replace('\\', '/') + '/'):
        raise RuntimeError('a different pypdf is already loaded; start a fresh process')
    return pypdf


def _json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def collect_pdf(source, output, *, evidence_id, title, publisher, claim, excerpt, page, run_root=None):
    started = perf_counter()
    allowed = task_run_root(run_root) if run_root is not None else None
    source = scoped_path(source, allowed or PDF_ROOT)
    output = scoped_path(output, allowed or PROJECT)
    if source.suffix.lower() != '.pdf':
        raise ValueError('only an explicitly authorized test PDF is accepted')
    if output.exists():
        raise FileExistsError('output must be a new directory')
    if not isinstance(page, int) or isinstance(page, bool) or page < 1:
        raise ValueError('page must be a positive one-based PDF page index')
    if not all(isinstance(x, str) and x.strip() for x in (title, publisher, claim, excerpt)):
        raise ValueError('title, publisher, claim and excerpt must be nonempty caller metadata')
    preparation_started = perf_counter()
    obj = dict(evidence_id=evidence_id,
               subject={'candidate_name': '合成PDF测试来源（非人物）'},
               evidence_type='unresolved_lead', claim=claim,
               source=dict(title=title, publisher=publisher, url=None, local_path=str(source),
                           source_type='user_provided_file', published_date=None, event_date=None),
               retrieval={'retrieved_at': datetime.now(timezone.utc).isoformat()},
               excerpt=None, excerpt_locator=None, context='调用者提供陈述；仅验证页内摘录存在。',
               identity_resolution='not_applicable',
               quality={'source_quality': 'unknown', 'provenance_status': 'user_supplied'},
               supports={'relevance': 'unknown', 'supports_statement': '语义支持关系待人工复核。'},
               limitations=['仅数字原生PDF文本提取；未执行OCR、身份或来源真实性判断。'],
               uncertainty='unknown', human_review='not_started',
               snapshot=dict(level='L0', status='unavailable', path=None, sha256=None,
                             media_type='application/pdf', notes='尚未取得可解析PDF。'))
    preparation_ms = (perf_counter() - preparation_started) * 1000
    check = perf_counter()
    errors = validate_evidence(obj)
    preflight_ms = (perf_counter() - check) * 1000
    if errors:
        raise ValueError('; '.join(errors))
    timing = dict(clock='time.perf_counter', python=platform.python_version(),
                  platform=platform.platform(), machine=platform.machine(),
                  pypdf_version='6.19.0', pypdf_already_loaded='pypdf' in sys.modules,
                  input_bytes=None, page_count=None, page_extraction_ms=[],
                  extraction_ms=0.0, preflight_validation_ms=preflight_ms)
    stage = perf_counter()
    pypdf = load_pypdf()
    timing['bundle_load_ms'] = (perf_counter() - stage) * 1000
    raw = None
    pages = []
    parse_ok = False
    failure = None
    stage = perf_counter()
    try:
        with source.open('rb') as stream:
            raw = stream.read(MAX_BYTES + 1)
        timing['input_bytes'] = len(raw)
        if len(raw) > MAX_BYTES:
            raw = None
            raise ValueError('PDF exceeds 10 MiB limit; input not fully read')
        if not raw.startswith(b'%PDF-'):
            raise ValueError('unsupported input: missing PDF header')
        reader = pypdf.PdfReader(io.BytesIO(raw), strict=True)
        if reader.is_encrypted:
            raise ValueError('encrypted PDF unsupported; no decryption attempted by ADD')
        timing['page_count'] = len(reader.pages)
        if not 1 <= timing['page_count'] <= MAX_PAGES:
            raise ValueError('PDF page count must be 1..100')
        pdf_pages = list(reader.pages)
        parse_ok = True
    except Exception as exc:
        failure = f'{type(exc).__name__}: {exc}'
    finally:
        timing['pdf_open_parse_ms'] = (perf_counter() - stage) * 1000
    if parse_ok:
        stage = perf_counter()
        for number, pdf_page in enumerate(pdf_pages, 1):
            page_started = perf_counter()
            entry = {'page': number, 'text': None, 'status': 'extraction_error'}
            try:
                text = pdf_page.extract_text() or ''
                if '\ufffd' in text or '\x00' in text:
                    raise ValueError('unreliable Unicode mapping')
                entry.update(text=text, status='text_extracted' if text.strip() else 'no_text_extracted')
            except Exception as exc:
                entry['error'] = f'{type(exc).__name__}: {exc}'
            timing['page_extraction_ms'].append((perf_counter() - page_started) * 1000)
            pages.append(entry)
        timing['extraction_ms'] = (perf_counter() - stage) * 1000
    stage = perf_counter()
    if raw is not None:
        input_hash = hashlib.sha256(raw).hexdigest()
    else:
        input_hash = None
    obj['retrieval']['retrieval_notes'] = json.dumps(
        {'input_sha256': input_hash, 'pypdf_version': '6.19.0', 'requested_page': page}, ensure_ascii=False)
    if parse_ok:
        for entry in pages:
            if entry['status'] != 'text_extracted':
                obj['limitations'].append(
                    f"PDF page {entry['page']}: {entry['status']}；不表示该页没有内容。"
                    + entry.get('error', ''))
        target = pages[page - 1] if page <= len(pages) else None
        if target and target['status'] == 'text_extracted' and excerpt in target['text']:
            offset = target['text'].index(excerpt)
            text_hash = hashlib.sha256(target['text'].encode('utf-8')).hexdigest()
            obj.update(evidence_type='source_supported_fact', excerpt=excerpt,
                       excerpt_locator=f'PDF page {page} (one-based); text SHA256={text_hash}; '
                                       f'characters [{offset}, {offset + len(excerpt)}) (zero-based Unicode)')
        else:
            failure = 'requested page unavailable, has no reliable extracted text, or excerpt absent on that page'
    if failure:
        obj.update(evidence_type='unknown_insufficient_coverage', uncertainty='material',
                   claim='本次未取得所请求PDF摘录的可靠证据，不表示相关内容不存在。',
                   context=f'原始待核验陈述：{claim}')
        obj['limitations'].append(failure)
        obj['snapshot']['notes'] = failure
    output.mkdir(parents=True, exist_ok=False)
    if parse_ok:
        (output / 'source.pdf').write_bytes(raw)
        page_bytes = _json_bytes(pages)
        (output / 'pages.json').write_bytes(page_bytes)
        obj['snapshot'].update(level='L3', status='saved', path=str(output / 'source.pdf'), sha256=input_hash,
                               notes=json.dumps({'pages_path': str(output / 'pages.json'),
                                                 'pages_sha256': hashlib.sha256(page_bytes).hexdigest()},
                                                ensure_ascii=False))
    path = output / 'evidence.json'
    path.write_bytes(_json_bytes(obj))
    timing['snapshot_evidence_ms'] = preparation_ms + (perf_counter() - stage) * 1000
    stage = perf_counter()
    errors = validate_file(path)
    timing['validation_ms'] = (perf_counter() - stage) * 1000
    timing['total_ms'] = (perf_counter() - started) * 1000
    timing['result'] = 'INVALID' if errors else obj['evidence_type']
    timing['total_boundary'] = 'collect_pdf entry through final Validator; excludes timing sidecar write and interpreter startup'
    (output / 'timing.json').write_bytes(_json_bytes(timing))
    if errors:
        raise ValueError('; '.join(errors))
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source')
    parser.add_argument('--output', required=True)
    for name in ('evidence-id', 'title', 'publisher', 'claim', 'excerpt'):
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--page', type=int, required=True)
    parser.add_argument('--run-root')
    try:
        path = collect_pdf(**vars(parser.parse_args()))
        obj = json.loads(path.read_text(encoding='utf-8'))
        print(f"VALID {obj['evidence_type']}: {path}")
        print(f'Timing: {path.parent / "timing.json"}')
        return 0 if obj['evidence_type'] == 'source_supported_fact' else 3
    except (OSError, ValueError, RuntimeError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
