"""Actual synthetic collectors -> saved Evidence -> report -> PDF/readback smoke."""
import argparse
import hashlib
import importlib.abc
import json
from pathlib import Path
import sys
from time import perf_counter
import traceback
import types
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from static_source import collect, task_run_root, scoped_path
from pdf_source import collect_pdf
import report
import pdf_report
import pdf_bundle


def run(root, without_pillow=False):
    start=perf_counter()
    if not sys.flags.no_site: raise ValueError('smoke requires fresh Python -B -E -S')
    root=task_run_root(root,create=True)
    attempts=[]
    class PILGuard(importlib.abc.MetaPathFinder):
        def find_spec(self,fullname,path=None,target=None):
            if fullname=='PIL' or fullname.startswith('PIL.'):
                attempts.append(fullname)
                if without_pillow: raise ModuleNotFoundError('PIL explicitly unavailable in isolated experiment')
    guard=PILGuard();sys.meta_path.insert(0,guard)
    timing={}
    result={'without_pillow':without_pillow,'site_disabled':bool(sys.flags.no_site)}
    def measured(key, action):
        before=perf_counter();value=action();timing[key]=(perf_counter()-before)*1000;return value
    def save(name,value):
        (root/name).write_text(report.json_text(value),encoding='utf-8')
    try:
        inputs=root/'inputs';inputs.mkdir()
        fixtures={'page.html':'static_sources/page.html','source.txt':'static_sources/source.txt','digital.pdf':'pdf_sources/digital.pdf'}
        for name,relative in fixtures.items():
            (inputs/name).write_bytes(scoped_path(ROOT/'tests/fixtures'/relative,ROOT/'tests/fixtures').read_bytes())
        result['input_bytes']={n:(inputs/n).stat().st_size for n in fixtures}
        common=dict(title='合成来源（非人物）',publisher='ADD synthetic fixture',claim='仅验证合成材料中的摘录，不作人物或法律判断。',run_root=root)
        html=measured('static_html_to_evidence_ms',lambda:collect(str(inputs/'page.html'),root/'html-source',evidence_id='E-CHAIN-HTML',excerpt='合成机构成立于2020年。',evidence_type='source_supported_fact',**common))
        text=measured('static_text_to_evidence_ms',lambda:collect(str(inputs/'source.txt'),root/'text-source',evidence_id='E-CHAIN-TEXT',excerpt='该材料仅用于流程测试。',**common))
        pdf=measured('pdf_source_to_evidence_ms',lambda:collect_pdf(inputs/'digital.pdf',root/'pdf-source',evidence_id='E-CHAIN-PDF',excerpt='第二页：仅用于流程测试。',page=2,**common))
        def merge():
            items=[json.loads(p.read_text(encoding='utf-8')) for p in (html,text,pdf)]
            report.validate_inputs(items,root,run_root=root)
            if any(e['snapshot']['status']!='saved' for e in items): raise ValueError('collector did not save actual source')
            save('evidence.json',items)
            return items
        items=measured('validation_merge_ms',merge)
        # Explicit fixed synthetic assignments, never inferred from a research claim.
        task=dict(title='完整合成链（非真实尽调）',scope='只验证本地合成来源处理；未指定观点与案件主体。',
                  enabled_modules={k:k not in ('viewpoints','conflicts') for k in report.MODULES},
                  assignments={'E-CHAIN-HTML':'background','E-CHAIN-TEXT':'background','E-CHAIN-PDF':'publications'})
        save('task.json',task)
        t=report.generate(root/'evidence.json',root/'task.json',root/'canonical',run_root=root)
        timing.update({k:t[k] for k in ('validation_ms','model_ms','markdown_ms','html_ms')})
        result.update(evidence_count=len(items),input_pdf_pages=json.loads((root/'pdf-source/timing.json').read_text())['page_count'])
        if without_pillow:
            # Experiment only: isolate the bounded non-Pillow archives. This does
            # not change the production loader or patch upstream ReportLab code.
            def experimental_loader(runtime, *, run_root=None):
                runtime=scoped_path(runtime,root);runtime.mkdir(exist_ok=False)
                for name,digest in pdf_bundle.WHEELS.items():
                    if name.startswith('pillow-'): continue
                    raw=(pdf_bundle.BUNDLE/name).read_bytes()
                    if hashlib.sha256(raw).hexdigest()!=digest:raise ValueError('experiment archive hash')
                    with zipfile.ZipFile(pdf_bundle.BUNDLE/name) as z:
                        for member in z.infolist():
                            scoped_path(runtime/member.filename,runtime)
                        z.extractall(runtime)
                for name in pdf_bundle._HOOKS:
                    module=types.ModuleType(name)
                    if name.endswith('settings'):
                        module.T1SearchPath=[];module.TTFSearchPath=[];module.CMapSearchPath=[]
                    sys.modules[name]=module
                sys.dont_write_bytecode=True
                sys.path.insert(0,str(runtime))
                return {'experiment':'authenticated non-Pillow archive extraction; upstream unmodified'}
            pdf_report.load_dependencies=experimental_loader
        t=pdf_report.generate_pdf(root/'canonical/report.json',root/'rendered',root/'.tmp-runtime',run_root=root)
        timing.update({k:t[k] for k in ('dependency_load_ms','pdf_render_ms','pdf_write_ms','readback_ms')})
        result.update(pdf_bytes=t['pdf_bytes'],output_pdf_pages=t['page_count'],embedded_fonts=t['embedded_fonts'],content_consistent=t['content_consistent'],dependency_archive_bytes=t['wheel_bytes'],expanded_dependency_bytes=t['expanded_dependency_bytes'],font_bytes=t['font_bytes'])
        for name in ('report.json','report.md','report.html'):
            if (root/'canonical'/name).read_bytes()!=(root/'rendered'/name).read_bytes():raise ValueError('canonical format drift')
        model=json.loads((root/'rendered/report.json').read_text(encoding='utf-8'))
        if model['evidence']!=items:raise ValueError('generated Evidence changed')
        for item in items:
            for value in [item['evidence_id'],*item['limitations']]:
                if report.md_text(value) not in (root/'rendered/report.md').read_text(encoding='utf-8'):raise ValueError('MD evidence missing')
                if report.html.escape(value,quote=True) not in (root/'rendered/report.html').read_text(encoding='utf-8'):raise ValueError('HTML evidence missing')
        result['result']='PASS'
    except Exception as exc:
        result.update(result='FAIL',error=f'{type(exc).__name__}: {exc}',traceback=traceback.format_exc())
    finally:
        timing['total_internal_ms']=(perf_counter()-start)*1000
        result.update(timing=timing,pil_import_attempts=attempts,loaded_product_modules={n:str(getattr(m,'__file__','')) for n,m in sys.modules.items() if n.split('.')[0] in ('PIL','reportlab','charset_normalizer','pypdf') and getattr(m,'__file__',None)})
        result['pil_loaded']=any(n=='PIL' or n.startswith('PIL.') for n in sys.modules)
        save('chain-result.json',result)
        sys.meta_path.remove(guard)
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--run-root',required=True);p.add_argument('--without-pillow',action='store_true')
    args=p.parse_args();r=run(args.run_root,args.without_pillow)
    print(json.dumps({'result':r['result'],'run_root':args.run_root,'pil_loaded':r['pil_loaded']},ensure_ascii=False))
    return 0 if r['result']=='PASS' else 3


if __name__=='__main__':raise SystemExit(main())
