#!/usr/bin/env python3
"""Synthetic validated Evidence -> one canonical model -> offline Markdown/HTML."""
import argparse
from copy import deepcopy
import html
import json
from pathlib import Path
import platform
import sys
from time import perf_counter
from urllib.parse import urlsplit, quote

from static_source import PROJECT, scoped_path
from validate_evidence import validate_evidence

INPUT_ROOT = PROJECT / 'tests' / 'fixtures' / 'report_sources'
MODULES = {'identity': '身份核对', 'background': '专业背景', 'publications': '公开著作',
           'viewpoints': '指定观点', 'relationships': '公开专业关系', 'conflicts': '冲突线索'}
BASE_MODULES = {'identity', 'background', 'publications', 'relationships'}
LABELS = {'claim': '陈述', 'evidence_type': '证据类型', 'subject': '对应主体',
          'source': '来源', 'retrieval': '检索', 'excerpt': '原文摘录',
          'excerpt_locator': '摘录定位', 'context': '上下文', 'identity_resolution': '身份状态',
          'quality': '来源质量', 'supports': '支持与关联', 'limitations': '限制',
          'uncertainty': '不确定性', 'snapshot': '快照', 'human_review': '人工复核状态'}


def json_text(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + '\n'


def validate_inputs(items, base_dir):
    if not isinstance(items, list) or not items:
        raise ValueError('nonempty Evidence array required')
    ids = set()
    for item in items:
        # Existing Validator can read snapshot paths. Bound these before calling it.
        if isinstance(item, dict) and isinstance(item.get('snapshot'), dict):
            path = item['snapshot'].get('path')
            if path:
                if not isinstance(path, str) or not Path(path).is_absolute():
                    raise ValueError('snapshot path must be absolute within authorized synthetic root')
                scoped_path(path, INPUT_ROOT)
        try:
            errors = validate_evidence(item, existing_ids=ids, base_dir=base_dir)
        except (TypeError, ValueError, OSError) as exc:
            raise ValueError(f'invalid Evidence: {exc}') from exc
        if errors:
            raise ValueError('; '.join(errors))
        ids.add(item['evidence_id'])


def build_model(items, task):
    """Caller has validated items; metadata only assigns, never interprets claims."""
    required = {'title', 'scope', 'enabled_modules', 'assignments'}
    if not isinstance(task, dict) or set(task) != required:
        raise ValueError('task requires title, scope, enabled_modules, assignments only')
    if not all(isinstance(task[k], str) and task[k].strip() for k in ('title', 'scope')):
        raise ValueError('task title/scope must be nonempty text')
    enabled, assignments = task['enabled_modules'], task['assignments']
    if (not isinstance(enabled, dict) or set(enabled) != set(MODULES)
            or any(type(v) is not bool for v in enabled.values())
            or not all(enabled[k] for k in BASE_MODULES)):
        raise ValueError('explicit boolean modules required; basic modules must be enabled')
    if not isinstance(assignments, dict) or set(assignments) != {e['evidence_id'] for e in items}:
        raise ValueError('assign each Evidence ID exactly once; no missing or extra IDs')
    if any(not isinstance(v, str) or v not in MODULES or not enabled[v] for v in assignments.values()):
        raise ValueError('Evidence cannot be assigned to unknown/disabled modules')
    sections = []
    for key, title in MODULES.items():
        refs = [e['evidence_id'] for e in items if assignments[e['evidence_id']] == key]
        status = '未执行' if not enabled[key] else ('已提供证据（不代表完整覆盖）' if refs else '未提供证据 / unknown')
        sections.append(dict(key=key, title=title, status=status, evidence_ids=refs))
    return dict(model_version='1', task=deepcopy(task), sections=sections, evidence=deepcopy(items))


def fields(value, prefix=''):
    """Lossless leaf text presentation; explicit null and empty arrays survive."""
    if isinstance(value, dict) and value:
        for key, child in value.items():
            yield from fields(child, f'{prefix}.{key}' if prefix else LABELS.get(key, key))
    elif isinstance(value, list) and value:
        for index, child in enumerate(value):
            yield from fields(child, f'{prefix}[{index}]')
    else:
        yield prefix, value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)


def blocks(model):
    """Shared presentation order for both formats; only reads the supplied model."""
    yield 1, model['task']['title'], None, []
    yield 2, '任务范围', None, [('范围（调用者元数据）', model['task']['scope'])]
    by_id = {e['evidence_id']: e for e in model['evidence']}
    for section in model['sections']:
        rows = [('模块状态', section['status'])]
        if section['key'] == 'conflicts' and section['status'] == '未执行':
            rows.append(('说明', '未进行针对具体案件主体的关系比对'))
        yield 2, section['title'], None, rows
        for eid in section['evidence_ids']:
            yield 3, eid, 'evidence-' + eid, list(fields(by_id[eid]))
    yield 2, '覆盖与限制', None, []
    for e in model['evidence']:
        yield 3, e['evidence_id'], None, list(fields({k: e[k] for k in
            ('evidence_type', 'identity_resolution', 'uncertainty', 'limitations')}))
    yield 2, '人工复核项', None, [('说明', '逐条保留输入复核状态；自动验证不等于律师复核。')]
    for e in model['evidence']:
        yield 3, e['evidence_id'], None, list(fields({k: e[k] for k in
            ('human_review', 'supports', 'limitations')}))
    yield 2, '来源索引', None, []
    for e in model['evidence']:
        yield 3, e['evidence_id'], None, list(fields({'source': e['source'],
            'retrieval': e['retrieval'], 'excerpt_locator': e.get('excerpt_locator')}))


def safe_url(value):
    try:
        p = urlsplit(value)
        if (p.scheme in ('https', 'http') and p.hostname and not p.username and not p.password
                and not any(ord(c) < 33 or c == '\\' for c in value)):
            return value
    except ValueError:
        pass
    return None


def md_text(value):
    # Escape source markup, keeping ordinary prose/IDs readable in the .md file.
    # Newlines cannot create injected Markdown headings or list items.
    escaped = html.escape(value, quote=False)
    return ''.join('\\' + c if c in '\\`*_[]#!|' else
                   '<br>' if c == '\n' else '&#13;' if c == '\r' else c for c in escaped)


def render_markdown(model):
    output = []
    for level, title, anchor, rows in blocks(model):
        output.append('#' * level + ' ' + md_text(title) + '\n')
        for label, value in rows:
            display = md_text(value)
            if label.endswith('.url') and safe_url(value):
                href = quote(value, safe=':/?#[]@!$&*,;=%')
                display = f'[{display}]({href})'
            output.append(f'- **{md_text(label)}**：{display}')
        output.append('')
    return '\n'.join(output).rstrip('\n') + '\n'


def render_html(model):
    output = ['<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">',
              '<meta name="viewport" content="width=device-width,initial-scale=1">',
              '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; base-uri \'none\'; form-action \'none\'">',
              '<title>' + html.escape(model['task']['title']) + '</title>',
              '<style>body{max-width:960px;margin:2rem auto;padding:0 1rem;font-family:system-ui;line-height:1.6}dt{font-weight:bold}dd{margin:0 0 .7rem;white-space:pre-wrap;overflow-wrap:anywhere}h2{border-bottom:1px solid #ccc}</style></head><body>']
    for level, title, anchor, rows in blocks(model):
        attr = f' id="{html.escape(anchor, quote=True)}"' if anchor else ''
        output.append(f'<h{level}{attr}>{html.escape(title)}</h{level}>')
        if rows: output.append('<dl>')
        for label, value in rows:
            display = html.escape(value, quote=True)
            if label.endswith('.url') and safe_url(value):
                display = f'<a href="{html.escape(value, quote=True)}" rel="noreferrer">{display}</a>'
            output.append(f'<dt>{html.escape(label)}</dt><dd>{display}</dd>')
        if rows: output.append('</dl>')
    output.append('</body></html>')
    return '\n'.join(output) + '\n'


def generate(evidence_path, task_path, output):
    start = perf_counter()
    evidence_path = scoped_path(evidence_path, INPUT_ROOT)
    task_path = scoped_path(task_path, INPUT_ROOT)
    output = scoped_path(output, PROJECT)
    if output.exists(): raise FileExistsError('output must be a new directory')
    items = json.loads(evidence_path.read_text(encoding='utf-8-sig'))
    task = json.loads(task_path.read_text(encoding='utf-8-sig'))
    stage = perf_counter()
    validate_inputs(items, evidence_path.parent)
    validation_ms = (perf_counter() - stage) * 1000
    stage = perf_counter()
    model = build_model(items, task)
    model_ms = (perf_counter() - stage) * 1000
    stage = perf_counter()
    markdown = render_markdown(model)
    markdown_ms = (perf_counter() - stage) * 1000
    stage = perf_counter()
    rendered_html = render_html(model)
    html_ms = (perf_counter() - stage) * 1000
    artifacts = {'report.json': json_text(model), 'report.md': markdown, 'report.html': rendered_html}
    output.mkdir(parents=True, exist_ok=False)
    sizes = {}
    for name, content in artifacts.items():
        data = content.encode('utf-8')
        (output / name).write_bytes(data)
        sizes[name] = len(data)
    timing = dict(clock='time.perf_counter', python=platform.python_version(),
                  platform=platform.platform(), evidence_count=len(items), output_bytes=sizes,
                  validation_ms=validation_ms, model_ms=model_ms, markdown_ms=markdown_ms,
                  html_ms=html_ms, total_ms=(perf_counter() - start) * 1000,
                  total_boundary='generate entry through artifacts/metadata; excludes timing sidecar write, interpreter startup and module imports')
    (output / 'timing.json').write_bytes(json_text(timing).encode('utf-8'))
    return timing


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('evidence_path'); parser.add_argument('task_path'); parser.add_argument('--output', required=True)
    try:
        print(json_text(generate(**vars(parser.parse_args()))))
        return 0
    except (ValueError, OSError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__': raise SystemExit(main())
