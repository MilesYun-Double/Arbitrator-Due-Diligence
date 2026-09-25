"""Deterministic PDF test bytes, not an ADD report renderer.

Uses PDF text operators and an explicit Unicode CMap; no screenshots/OCR or
third-party generation dependency. STSong-Light is a standard CJK font reference,
not an embedded font resource. Viewer font substitution is outside this test.
"""

CHINESE = '合成资料：数字原生 PDF。'
SECOND = '第二页：仅用于流程测试。'
ENGLISH = 'Evidence sample 2026 https://example.invalid/test'


def make_pdf(pages=None):
    pages = pages if pages is not None else [CHINESE, SECOND + '\n' + ENGLISH, '']
    cmap = (b'/CIDInit /ProcSet findresource begin\n12 dict begin\nbegincmap\n'
            b'/CIDSystemInfo << /Registry (Adobe) /Ordering (UCS) /Supplement 0 >> def\n'
            b'/CMapName /ADD-Test def\n/CMapType 2 def\n1 begincodespacerange\n'
            b'<0000> <FFFF>\nendcodespacerange\n1 beginbfrange\n'
            b'<0000> <FFFF> <0000>\nendbfrange\nendcmap\n'
            b'CMapName currentdict /CMap defineresource pop\nend\nend')

    def stream(data):
        return b'<< /Length ' + str(len(data)).encode() + b' >>\nstream\n' + data + b'\nendstream'

    objects = [b'<< /Type /Catalog /Pages 2 0 R >>', b'',
               b'<< /Type /Font /Subtype /Type0 /BaseFont /STSong-Light '
               b'/Encoding /UniGB-UCS2-H /DescendantFonts [4 0 R] /ToUnicode 5 0 R >>',
               b'<< /Type /Font /Subtype /CIDFontType0 /BaseFont /STSong-Light '
               b'/CIDSystemInfo << /Registry (Adobe) /Ordering (GB1) /Supplement 5 >> '
               b'/FontDescriptor 6 0 R /DW 1000 >>', stream(cmap),
               b'<< /Type /FontDescriptor /FontName /STSong-Light /Flags 6 '
               b'/FontBBox [-25 -254 1000 880] /ItalicAngle 0 /Ascent 880 /Descent -120 '
               b'/CapHeight 880 /StemV 80 >>']
    kids = []
    for text in pages:
        page_id = len(objects) + 1
        kids.append(f'{page_id} 0 R')
        objects.append((f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] '
                        f'/Resources << /Font << /F1 3 0 R >> >> /Contents {page_id + 1} 0 R >>').encode())
        lines = text.splitlines()
        content = b'BT /F1 14 Tf 50 780 Td 22 TL\n' if lines else b''
        for line in lines:
            content += b'<' + line.encode('utf-16-be').hex().encode() + b'> Tj T*\n'
        if lines:
            content += b'ET'
        objects.append(stream(content))
    objects[1] = f'<< /Type /Pages /Count {len(pages)} /Kids [{" ".join(kids)}] >>'.encode()
    data = bytearray(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n')
    offsets = [0]
    for i, obj in enumerate(objects, 1):
        offsets.append(len(data))
        data += f'{i} 0 obj\n'.encode() + obj + b'\nendobj\n'
    xref = len(data)
    data += f'xref\n0 {len(offsets)}\n0000000000 65535 f \n'.encode()
    for offset in offsets[1:]:
        data += f'{offset:010d} 00000 n \n'.encode()
    data += (f'trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\n'
             f'startxref\n{xref}\n%%EOF\n').encode()
    return bytes(data)
