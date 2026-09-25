"""One canonical model to MD/HTML/PDF, with an embedded licensed font and readback."""
import argparse
import hashlib
import html
import io
import json
from pathlib import Path
import platform
import re
import sys
from time import perf_counter

from report import blocks, build_model, render_markdown, render_html, json_text
from validate_evidence import validate_evidence
from static_source import PROJECT, scoped_path
from pdf_bundle import load_dependencies, WHEELS, BUNDLE
from pdf_source import load_pypdf

MODEL_ROOT = PROJECT / 'tests/fixtures/pdf_reports'
FONT_PATH = BUNDLE / 'LXGWWenKai-Regular.ttf'
FONT_HASH = '39ad71264b588165b469e35e6afb162a378dacd1f95348160240ba9038ac3009'
FONT_NAME = 'ADDWenKai'


def check_model(model):
    """Check canonical structure without opening any Evidence source/snapshot."""
    if not isinstance(model, dict) or set(model) != {'model_version', 'task', 'sections', 'evidence'}:
        raise ValueError('invalid canonical model')
    items = model['evidence']
    if not isinstance(items, list) or not items: raise ValueError('nonempty canonical Evidence required')
    ids = set()
    for item in items:
        try: errors = validate_evidence(item, existing_ids=ids)
        except (TypeError, ValueError) as exc: raise ValueError('invalid canonical Evidence') from exc
        if errors: raise ValueError('; '.join(errors))
        ids.add(item['evidence_id'])
    if model != build_model(items, model['task']):
        raise ValueError('canonical sections/version do not match validated Evidence and task')


def lines(model):
    for level, title, _, rows in blocks(model):
        yield level, title
        for label, value in rows: yield 0, f'{label}：{value}'


def render_pdf(model, runtime):
    """Dependencies must already be loaded; no network, source reads or model edits."""
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph
    from reportlab.pdfgen.canvas import Canvas
    font_path = scoped_path(FONT_PATH, PROJECT)
    if hashlib.sha256(font_path.read_bytes()).hexdigest() != FONT_HASH:
        raise ValueError('font hash mismatch')
    font_start = perf_counter()
    cached = FONT_NAME in pdfmetrics.getRegisteredFontNames()
    if not cached: pdfmetrics.registerFont(TTFont(FONT_NAME, str(font_path)))
    font = pdfmetrics.getFont(FONT_NAME)
    if Path(font.face.filename) != font_path:
        raise ValueError('font origin mismatch')
    presentation = list(lines(model))
    characters = set(''.join(text for _, text in presentation) + '第 0123456789 页')
    missing = sorted(ord(c) for c in characters if c not in '\n\r\t' and not font.face.charToGlyph.get(ord(c)))
    if missing: raise ValueError('missing glyph: ' + ', '.join(f'U+{c:04X}' for c in missing))
    if any(ord(c)<32 and c not in '\n\r\t' for c in characters):
        raise ValueError('unsupported control character')
    font_ms = (perf_counter()-font_start)*1000
    styles = {level: ParagraphStyle(f'level{level}',fontName=FONT_NAME,fontSize=size,leading=leading,
                                    spaceBefore=before,spaceAfter=after,wordWrap='CJK',
                                    splitLongWords=True,keepWithNext=bool(level))
              for level,size,leading,before,after in [(0,9.5,14,0,4),(1,18,25,0,14),(2,13,19,12,7),(3,11,16,8,5)]}
    story=[]
    for level, text in presentation:
        # Paragraph supports markup: only our escaped text and explicit line breaks enter.
        safe = html.escape(text,quote=False).replace('\r\n','\n').replace('\r','\n').replace('\t','    ').replace('\n','<br/>')
        story.append(Paragraph(safe,styles[level]))
    output=io.BytesIO()
    def footer(canvas, doc):
        canvas.saveState();canvas.setFont(FONT_NAME,9)
        canvas.drawCentredString(A4[0]/2,25,f'第 {doc.page} 页')
        canvas.restoreState()
    def canvas_factory(*args, **kwargs):
        kwargs.update(initialFontName=FONT_NAME,initialFontSize=9.5,invariant=1,pageCompression=1)
        return Canvas(*args, **kwargs)
    doc=SimpleDocTemplate(output,pagesize=A4,leftMargin=44,rightMargin=44,topMargin=42,bottomMargin=44,
                          title=model['task']['title'],author='Arbitrator Due Diligence')
    doc.build(story,onFirstPage=footer,onLaterPages=footer,canvasmaker=canvas_factory)
    return output.getvalue(),dict(font_bytes=font_path.stat().st_size,font_sha256=FONT_HASH,
                                 font_already_loaded=cached,font_load_ms=font_ms)


def compact(value): return re.sub(r'\s+','',value)


def readback(raw,model):
    pypdf=load_pypdf()
    reader=pypdf.PdfReader(io.BytesIO(raw))
    page_texts=[page.extract_text() or '' for page in reader.pages]
    labels=[];uri_links=[];fonts=set()
    for index,(page,text) in enumerate(zip(reader.pages,page_texts),1):
        if f'第 {index} 页' not in text: raise ValueError('missing PDF page label')
        labels.append(index)
        for reference in page.get('/Annots',[]):
            action=reference.get_object().get('/A',{})
            if action.get('/S')=='/URI': uri_links.append(str(action.get('/URI')))
        for reference in page['/Resources']['/Font'].values():
            font=reference.get_object();desc=font.get('/FontDescriptor')
            if not desc or '/FontFile2' not in desc.get_object() or 'LXGWWenKai' not in str(font.get('/BaseFont')):
                raise ValueError('unexpected/non-embedded PDF font')
            fonts.add(str(font['/BaseFont']))
    if uri_links: raise ValueError('this renderer emits plain URL text, no actions')
    # Ignore layout whitespace/page labels, but compare the entire ordered presentation.
    actual=''.join(re.sub(r'第 \d+ 页\s*','',text,count=1) for text in page_texts)
    expected=''.join(text for _,text in lines(model))
    if compact(actual)!=compact(expected):
        raise ValueError('PDF readback differs from canonical presentation')
    return dict(page_count=len(reader.pages),page_labels=labels,embedded_fonts=sorted(fonts),
                uri_links=uri_links,content_consistent=True)


def generate_pdf(model_path,output,runtime):
    started=perf_counter()
    model_path=scoped_path(model_path,MODEL_ROOT);output=scoped_path(output,PROJECT)
    if output.exists():raise FileExistsError('output must be a new directory')
    model=json.loads(model_path.read_text(encoding='utf-8-sig'))
    check_model(model)
    stage=perf_counter();bundle=load_dependencies(runtime);dependency_ms=(perf_counter()-stage)*1000
    formats_start=perf_counter()
    md=render_markdown(model);ht=render_html(model)
    stage=perf_counter();raw,font=render_pdf(model,runtime);render_ms=(perf_counter()-stage)*1000
    output.mkdir(parents=True,exist_ok=False)
    stage=perf_counter();(output/'report.pdf').write_bytes(raw);write_ms=(perf_counter()-stage)*1000
    for name,text in [('report.json',json_text(model)),('report.md',md),('report.html',ht)]:
        (output/name).write_bytes(text.encode('utf-8'))
    formats_ms=(perf_counter()-formats_start)*1000
    stage=perf_counter();checked=readback((output/'report.pdf').read_bytes(),model);readback_ms=(perf_counter()-stage)*1000
    timing=dict(clock='time.perf_counter',python=platform.python_version(),platform=platform.platform(),
                evidence_count=len(model['evidence']),pdf_bytes=len(raw),**bundle,**font,**checked,
                dependency_load_ms=dependency_ms,pdf_render_ms=render_ms,pdf_write_ms=write_ms,
                readback_ms=readback_ms,formats_total_ms=formats_ms,total_ms=(perf_counter()-started)*1000,
                total_boundary='entry through formats, readback and environment metadata; excludes timing sidecar write and interpreter/import startup')
    (output/'timing.json').write_bytes(json_text(timing).encode('utf-8'))
    return timing


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('model_path');p.add_argument('--output',required=True);p.add_argument('--runtime',required=True)
    try: print(json_text(generate_pdf(**vars(p.parse_args()))));return 0
    except (OSError,ValueError,ImportError) as exc:print(f'ERROR: {exc}',file=sys.stderr);return 2


if __name__=='__main__':raise SystemExit(main())
