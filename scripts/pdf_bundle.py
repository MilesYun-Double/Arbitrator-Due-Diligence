"""Pinned PDF runtime artifact closure; unpack locally, never pip install or use host packages."""
import hashlib
import importlib
import os
from pathlib import Path
import platform
import sys
import types
import zipfile

from static_source import PROJECT, scoped_path

BUNDLE = PROJECT / 'vendor/pdf'
WHEELS = {
    'reportlab-4.4.10-add-runtime-1.zip': '3217e78468b2d0d6f47512a2d467e2433500b006ccec2d5b5d04ab191b5600d1',
    'pillow-12.3.0-cp312-cp312-win_amd64.whl': 'a2b55dd6b2a4c4b7d87ffa56bdb33fdc5fdb9a462173861a7bc097f17d91cb09',
    'charset_normalizer-3.4.7-py3-none-any.whl': '3dce51d0f5e7951f8bb4900c257dad282f49190fdbebecd4ba99bcc41fef404d',
}
_HOOKS = ('reportlab_mods', 'reportlab_settings', 'reportlab.local_rl_mods', 'reportlab.local_rl_settings')
_OWN_HOOKS = {}


def load_dependencies(runtime, *, run_root=None):
    from research_run import resolve_run, run_path
    allowed = resolve_run(run_root) if run_root is not None else PROJECT
    if sys.implementation.name != 'cpython' or sys.version_info[:2] != (3, 12) or sys.platform != 'win32' or platform.machine().lower() not in ('amd64', 'x86_64'):
        raise ValueError('bundled Pillow candidate requires Windows x64 / CPython 3.12; no automatic installation')
    runtime = run_path(runtime, allowed)
    if not runtime.name.startswith('.tmp-'):
        raise ValueError('runtime must be an explicit task-owned .tmp-* directory')
    for name in ('reportlab', 'PIL', 'charset_normalizer'):
        module = sys.modules.get(name)
        if module is not None and not Path(module.__file__).is_relative_to(runtime):
            raise ValueError(f'foreign preloaded dependency: {name}; use fresh Python')
    if any(key.startswith('RL_') for key in os.environ):
        raise ValueError('RL_* settings present; use a clean process, no configuration changed')
    fresh = not runtime.exists()
    expected = set()
    expanded = 0
    # Authenticate all artifacts before writing/executing any dependency.
    for name, digest in WHEELS.items():
        path = scoped_path(BUNDLE / name, PROJECT)
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f'bundled dependency hash mismatch: {name}')
    for name in WHEELS:
        with zipfile.ZipFile(BUNDLE / name) as archive:
            for info in archive.infolist():
                if info.is_dir(): continue
                target = run_path(runtime / info.filename, allowed)
                expected.add(target)
                data = archive.read(info)
                expanded += len(data)
                if fresh:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with target.open('xb') as stream: stream.write(data)
                elif not target.is_file() or hashlib.sha256(target.read_bytes()).digest() != hashlib.sha256(data).digest():
                    raise ValueError('runtime differs from pinned artifacts; use a new directory')
    actual = set()
    for current, directories, files in os.walk(runtime, followlinks=False):
        for name in directories + files:
            node = run_path(Path(current) / name, allowed)
            if name in files: actual.add(node)
    if actual != expected:
        raise ValueError('unexpected runtime files; no overwrite/cleanup attempted')
    # ReportLab upstream normally probes user home hooks and system font paths.
    # Explicit in-process neutral hooks prevent those reads, without editing upstream.
    for name in _HOOKS:
        if name in sys.modules and sys.modules[name] is not _OWN_HOOKS.get(name):
            raise ValueError(f'preloaded ReportLab hook: {name}')
        if name not in _OWN_HOOKS:
            module = types.ModuleType(name)
            if name.endswith('settings'):
                module.T1SearchPath = []; module.TTFSearchPath = []; module.CMapSearchPath = []
            _OWN_HOOKS[name] = module
        sys.modules[name] = _OWN_HOOKS[name]
    # Only this process: do not create/consume unchecked bytecode in runtime.
    sys.dont_write_bytecode = True
    if str(runtime) not in sys.path: sys.path.insert(0, str(runtime))
    for name, version in (('reportlab', '4.4.10'), ('PIL', '12.3.0'), ('charset_normalizer', '3.4.7')):
        module = importlib.import_module(name)
        if module.__version__ != version or not Path(module.__file__).is_relative_to(runtime):
            raise ValueError(f'wrong dependency origin/version: {name}')
    from reportlab.platypus import SimpleDocTemplate, Paragraph
    from reportlab.pdfbase.ttfonts import TTFont
    return dict(runtime_unpacked=fresh, wheel_bytes=sum((BUNDLE / n).stat().st_size for n in WHEELS),
                expanded_dependency_bytes=expanded)
