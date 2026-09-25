"""Derive the ADD ReportLab runtime ZIP from one authenticated upstream wheel.

No pip install, network, or upstream Python/font modifications. The wheel RECORD
is rebuilt because removed files must not remain in the redistributed inventory.
"""
import argparse
import base64
import csv
import hashlib
import io
import json
from pathlib import Path
import zipfile

UPSTREAM_NAME = 'reportlab-4.4.10-py3-none-any.whl'
UPSTREAM_SHA256 = '5abc815746ae2bc44e7ff25db96814f921349ca814c992c7eac3c26029bf7c24'
ARTIFACT_NAME = 'reportlab-4.4.10-add-runtime-1.zip'
RECORD = 'reportlab-4.4.10.dist-info/RECORD'
EXCLUDED = tuple('reportlab/fonts/' + n for n in (
    'DarkGarden-changelog.txt', 'DarkGarden-copying-gpl.txt',
    'DarkGarden-copying.txt', 'DarkGarden-readme.txt', 'DarkGarden.sfd',
    'DarkGardenMK.afm', 'DarkGardenMK.pfb'))


def derive(raw):
    if hashlib.sha256(raw).hexdigest() != UPSTREAM_SHA256:
        raise ValueError('upstream ReportLab wheel hash mismatch')
    with zipfile.ZipFile(io.BytesIO(raw)) as source:
        names = source.namelist()
        if len(names) != len(set(names)) or set(n for n in names if 'darkgarden' in n.lower()) != set(EXCLUDED):
            raise ValueError('unexpected upstream DarkGarden inventory')
        files = {n: source.read(n) for n in names if n not in EXCLUDED and n != RECORD}
        removed = [dict(path=n, bytes=len(source.read(n)), sha256=hashlib.sha256(source.read(n)).hexdigest()) for n in EXCLUDED]
    inventory = io.StringIO(newline='')
    writer = csv.writer(inventory, lineterminator='\n')
    for name, data in sorted(files.items()):
        digest = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b'=').decode('ascii')
        writer.writerow((name, 'sha256=' + digest, len(data)))
    writer.writerow((RECORD, '', ''))
    files[RECORD] = inventory.getvalue().encode('utf-8')
    result = io.BytesIO()
    with zipfile.ZipFile(result, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as target:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            target.writestr(info, data, compresslevel=9)
    return result.getvalue(), removed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--upstream', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    data, removed = derive(args.upstream.read_bytes())
    with args.output.open('xb') as stream:
        stream.write(data)
    print(json.dumps(dict(filename=args.output.name, sha256=hashlib.sha256(data).hexdigest(), bytes=len(data), excluded=removed), indent=2))


if __name__ == '__main__':
    main()
