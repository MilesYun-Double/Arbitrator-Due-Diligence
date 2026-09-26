#!/usr/bin/env python3
"""Bounded static-source capture; semantic claims remain the caller's responsibility."""
import argparse
from datetime import datetime, timezone
from email.message import Message
import hashlib
from html.parser import HTMLParser
import ipaddress
import json
import os
from pathlib import Path
import socket
import stat
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener
from urllib.robotparser import RobotFileParser

from validate_evidence import validate_evidence, validate_file

PROJECT = Path(__file__).resolve().parents[1]
TEST_ROOT = PROJECT / 'tests' / 'fixtures' / 'static_sources'
MAX_BYTES = 1024 * 1024
TIMEOUT = 15
USER_AGENT = 'ADD-StaticSource/1.0'
TYPES = ('source_supported_fact', 'unresolved_lead', 'unknown_insufficient_coverage')
DENIED = {'reports', '.git', '.preview', 'credentials', 'secrets', 'memory'}


def scoped_path(value, root):
    return _checked_path(value, root)


def _checked_path(value, root, *, reports_root=None):
    """Reject traversal and links before reading, including Windows junctions/ADS."""
    if ".." in Path(value).parts:
        raise ValueError("path traversal refused")
    path = Path(os.path.abspath(value))
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise ValueError(f'path outside allowed root: {root}') from exc
    for index, part in enumerate(path.relative_to(PROJECT).parts):
        authorized_reports = (reports_root is not None and index == 0 and part == "reports"
                              and path.is_relative_to(reports_root))
        if (part.lower() in DENIED and not authorized_reports) or ':' in part or part.endswith((' ', '.')):
            raise ValueError('forbidden path component')
        # Task-owned .tmp-* output directories are the sole hidden exception.
        if part.startswith('.') and not part.startswith('.tmp-'):
            raise ValueError('forbidden hidden path component')
    for node in [PROJECT, *[PROJECT.joinpath(*path.relative_to(PROJECT).parts[:i])
                            for i in range(1, len(path.relative_to(PROJECT).parts) + 1)]]:
        try:
            info = node.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
            raise ValueError('links/reparse points are not allowed')
        if stat.S_ISREG(info.st_mode) and info.st_nlink > 1:
            raise ValueError('hard-linked files are not allowed')
    if not relative.parts:
        raise ValueError('a file or new output subdirectory is required')
    return path


RUN_MARKER = 'synthetic-run.json'
RUN_CONTRACT = {'scope': 'ADD synthetic capability run', 'version': 1}


def task_run_root(value, *, create=False):
    """Explicit project-child synthetic run only; marker is scope, not authority."""
    root = scoped_path(value, PROJECT)
    if root.parent != PROJECT or not root.name.startswith('.tmp-add-run-'):
        raise ValueError('run root must be a project-child .tmp-add-run-* directory')
    marker = scoped_path(root / RUN_MARKER, root)
    if create:
        root.mkdir(exist_ok=False)
        marker.write_text(json.dumps(RUN_CONTRACT), encoding='utf-8')
    elif not root.is_dir() or json.loads(marker.read_text(encoding='utf-8')) != RUN_CONTRACT:
        raise ValueError('missing or invalid synthetic run contract')
    return root


def _url_parts(url):
    parts = urlsplit(url)
    if (parts.scheme not in ('http', 'https') or not parts.hostname or parts.username
            or parts.password or any(ord(c) < 33 for c in url)):
        raise ValueError('only credential-free public http/https URLs are allowed')
    return parts


def _check_public_url(url):
    parts = _url_parts(url)
    port = parts.port or (443 if parts.scheme == 'https' else 80)
    addresses = socket.getaddrinfo(parts.hostname, port, type=socket.SOCK_STREAM)
    if not addresses or any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses):
        raise ValueError('non-public destination refused')


def _bounded_read(stream):
    raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError('source exceeds 1 MiB limit')
    return raw


class SafeRedirect(HTTPRedirectHandler):
    def __init__(self, check_robots=False):
        self.check_robots = check_robots

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        _check_public_url(newurl)
        if self.check_robots:
            _robots_allowed(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _open(url, check_robots=False):
    _check_public_url(url)
    # Do not inherit proxy credentials or browser cookies from the environment.
    opener = build_opener(ProxyHandler({}), SafeRedirect(check_robots))
    return opener.open(Request(url, headers={'User-Agent': USER_AGENT,
                                            'Accept-Encoding': 'identity'}), timeout=TIMEOUT)


def _robots_allowed(url):
    parts = urlsplit(url)
    robots_url = urlunsplit((parts.scheme, parts.netloc, '/robots.txt', '', ''))
    try:
        with _open(robots_url) as response:
            text = _bounded_read(response).decode('utf-8-sig')
    except HTTPError as exc:
        if exc.code == 404:
            return
        raise ValueError(f'robots unavailable: HTTP {exc.code}') from exc
    parser = RobotFileParser()
    parser.parse(text.splitlines())
    if not parser.can_fetch(USER_AGENT, url):
        raise ValueError('robots disallows this URL')


def _fetch(url, metadata):
    _robots_allowed(url)
    with _open(url, check_robots=True) as response:
        metadata.update(final_url=response.geturl(), content_type=response.headers.get('Content-Type'),
                        http_status=response.status)
        if response.headers.get('Content-Encoding', 'identity').lower() != 'identity':
            raise ValueError('compressed response is not supported')
        return _bounded_read(response)


class TextParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hidden = []
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'template'):
            self.hidden.append(tag)
        if not self.hidden and tag in ('p', 'div', 'br', 'li', 'tr', 'td', 'th', 'h1', 'h2', 'h3', 'title'):
            self.parts.append('\n')

    def handle_endtag(self, tag):
        if self.hidden and tag == self.hidden[-1]:
            self.hidden.pop()
        elif not self.hidden and tag in ('p', 'div', 'li', 'tr', 'h1', 'h2', 'h3', 'title'):
            self.parts.append('\n')

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def readable(raw, content_type):
    header = Message()
    header['content-type'] = content_type or 'application/octet-stream'
    media = header.get_content_type()
    if media not in ('text/plain', 'text/html'):
        raise ValueError(f'unsupported media type: {media}')
    try:
        text = raw.decode(header.get_content_charset() or 'utf-8-sig', errors='strict')
    except (UnicodeError, LookupError) as exc:
        raise ValueError('unsupported or invalid encoding; no replacement text generated') from exc
    if '\x00' in text:
        raise ValueError('binary content refused')
    if media == 'text/html':
        parser = TextParser()
        parser.feed(text)
        parser.close()
        text = '\n'.join(line.strip() for line in ''.join(parser.parts).splitlines() if line.strip())
    if not text.strip():
        raise ValueError('no readable static text')
    return text


def collect(source, output, *, evidence_id, title=None, publisher=None, claim=None, excerpt=None,
            evidence_type='unresolved_lead', level='L2', run_root=None, metadata_path=None):
    from research_run import resolve_run, is_real, run_path, staged_input, real_metadata
    allowed = resolve_run(run_root) if run_root is not None else None
    real = is_real(allowed)
    if real and metadata_path is None:
        raise ValueError('real run requires explicit metadata JSON')
    if not real and metadata_path is not None:
        raise ValueError('real metadata requires a real run')
    if evidence_type not in TYPES or level not in ('L0', 'L1', 'L2'):
        raise ValueError('unsupported evidence type or snapshot level')
    if evidence_type == 'source_supported_fact' and (not excerpt or level == 'L0'):
        raise ValueError('source-supported fact requires an excerpt and L1/L2')
    if not real and not all(isinstance(v, str) and v.strip() for v in (title, publisher, claim)):
        raise ValueError('title, publisher and claim are caller-supplied nonempty metadata')
    output = run_path(output, allowed or PROJECT)
    if output.exists():
        raise FileExistsError('output must be a new directory')
    is_url = '://' in source
    if allowed is not None and not real and is_url:
        raise ValueError('task-owned synthetic run accepts local inputs only')
    local = None
    if not is_url:
        local = staged_input(source, allowed) if real else scoped_path(source, allowed or TEST_ROOT)
        if local.suffix.lower() not in ('.txt', '.html', '.htm'):
            raise ValueError('only explicitly named test text/HTML files are allowed')
    else:
        _url_parts(source)
    now = datetime.now(timezone.utc).isoformat()
    metadata = dict(requested_url=source if is_url else None, final_url=None,
                    source_path=str(local) if local else None, content_type=None, http_status=None)
    obj = dict(evidence_id=evidence_id,
               subject={'candidate_name': '流程测试来源（非人物）', 'identity_notes': '不执行人物身份核验'},
               evidence_type=evidence_type, claim=claim,
               source=dict(title=title, publisher=publisher, url=source if is_url else None,
                           local_path=str(local) if local else None,
                           source_type='other' if is_url else 'user_provided_file',
                           published_date=None, event_date=None),
               retrieval={'retrieved_at': now}, excerpt=None, excerpt_locator=None,
               context='调用者提供的陈述；脚本仅验证摘录存在，不判断其真伪或支持关系。',
               identity_resolution='not_applicable',
               quality={'source_quality': 'unknown', 'provenance_status': 'unknown',
                        'quality_notes': '保存快照不提升来源等级；发布主体由调用者提供，未核验。'},
               supports={'relevance': 'unknown', 'supports_statement': '支持关系待人工复核。'},
               limitations=['仅静态读取，不执行脚本；不核验来源真实性、身份或法律结论。'],
               uncertainty='unknown', snapshot={'level': level, 'status': 'not_saved', 'path': None,
                                              'sha256': None, 'media_type': None, 'notes': None},
               human_review='not_started')
    if real:
        obj = real_metadata(metadata_path, allowed, evidence_id, excerpt, local, source if is_url else None)
        if level == 'L0' and obj['evidence_type'] in ('source_supported_fact', 'public_viewpoint', 'relationship_fact'):
            raise ValueError('source-backed Evidence requires L1/L2')
        obj.update(excerpt=None, excerpt_locator=None)
        obj['snapshot'] = dict(level=level, status='not_saved', path=None, sha256=None, media_type=None, notes=None)
    # Validate caller metadata using the existing contract before any I/O.
    probe = dict(obj, evidence_type='unresolved_lead')
    errors = validate_evidence(probe)
    if errors:
        raise ValueError('; '.join(errors))
    raw = text = None
    failure = None
    try:
        if local:
            metadata['content_type'] = 'text/html' if local.suffix.lower() in ('.htm', '.html') else 'text/plain'
            with local.open('rb') as stream:
                raw = _bounded_read(stream)
        else:
            raw = _fetch(source, metadata)
        text = readable(raw, metadata['content_type'])
        if excerpt and excerpt not in text:
            raise ValueError('requested excerpt not found in derived readable text')
    except (OSError, ValueError, URLError) as exc:
        failure = f'{type(exc).__name__}: {exc}'
        if isinstance(exc, HTTPError):
            metadata.update(final_url=exc.geturl(), http_status=exc.code)
        raw = text = None
    if failure and real:
        raise ValueError(f'real source capture failed; caller metadata not reclassified: {failure}')
    if failure:
        obj.update(evidence_type='unknown_insufficient_coverage',
                   claim='本次未能取得可用来源证据，不表示相关事实不存在。',
                   context=f'原始待核验陈述：{claim}', uncertainty='material')
        obj['limitations'].append(failure)
        obj['snapshot'].update(level='L0', status='unavailable', notes=failure)
        metadata['error'] = failure
    else:
        metadata['source_sha256'] = hashlib.sha256(raw).hexdigest()
        derived_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        metadata['readable_sha256'] = derived_hash
        if level != 'L0' and excerpt:
            offset = text.index(excerpt)
            obj['excerpt'] = excerpt
            obj['excerpt_locator'] = (f'readable UTF-8 text sha256={derived_hash}; '
                                      f'characters [{offset}, {offset + len(excerpt)}) (zero-based Unicode)')
        if level == 'L2':
            obj['snapshot'].update(status='saved', path=str(output / 'source.raw'),
                                   sha256=metadata['source_sha256'], media_type=metadata['content_type'],
                                   notes=json.dumps({'readable_path': str(output / 'readable.txt'),
                                                     'readable_sha256': derived_hash}, ensure_ascii=False))
        else:
            obj['snapshot']['notes'] = '正文未保存；若有摘录，以本次派生文本hash和字符偏移定位。'
    obj['retrieval']['retrieval_notes'] = json.dumps(metadata, ensure_ascii=False)
    errors = validate_evidence(obj)
    if errors:
        raise ValueError('; '.join(errors))
    output.mkdir(parents=True, exist_ok=False)
    if obj['snapshot']['status'] == 'saved':
        (output / 'source.raw').write_bytes(raw)
        (output / 'readable.txt').write_bytes(text.encode('utf-8'))
    path = output / 'evidence.json'
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    errors = validate_file(path)
    if errors:
        raise ValueError('; '.join(errors))
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source')
    parser.add_argument('--output', required=True)
    for key in ('evidence-id', 'title', 'publisher', 'claim'):
        parser.add_argument('--' + key, required=key == 'evidence-id')
    parser.add_argument('--run-root')
    parser.add_argument('--metadata', dest='metadata_path')
    parser.add_argument('--excerpt')
    parser.add_argument('--evidence-type', choices=TYPES, default='unresolved_lead')
    parser.add_argument('--level', choices=('L0', 'L1', 'L2'), default='L2')
    args = vars(parser.parse_args())
    try:
        path = collect(**args)
        obj = json.loads(path.read_text(encoding='utf-8'))
        print(f"VALID {obj['snapshot']['status']}: {path}")
        return 3 if obj['snapshot']['status'] == 'unavailable' else 0
    except (OSError, ValueError) as exc:
        print(f'ERROR: {exc}')
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
