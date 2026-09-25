# PDF renderer bundled candidate — Issue #9

Fixed upstream records and original-wheel hashes are in `upstream.json`. No wheel or font source was modified. These are implementation candidates for the authorized synthetic report path, not a universal-host release.

|Component|Version|License / distribution conditions|
|---|---|---|
|ReportLab open source|4.4.10|BSD-3-Clause; retain copyright, conditions/disclaimer; no endorsement. Original wheel LICENSE preserved and copied to reportlab-LICENSE.txt.|
|Pillow|12.3.0, CPython3.12 Windows x64 wheel|MIT-CMU main code plus the wheel's compiled-library notices; preserve the entire 78016-byte pillow-LICENSE.txt, not just the main license.|
|charset-normalizer|3.4.7, pure Python wheel|MIT; preserve charset_normalizer-LICENSE.txt. No optional compiled speedup.|
|LXGW WenKai Regular|1.522, pinned commit e8b5b48b79f19f29aa68b0a178eab3472ea9f7e8|SIL OFL-1.1, preserve LXGWWenKai-OFL.txt and copyright. Commercial bundling/embedding allowed, no standalone font sale. Font remains OFL; generated documents need not be OFL. Unmodified full font is shipped.|

## Actual closure / notices

The Pillow wheel includes Brotli, FreeType, HarfBuzz, lcms2, libavif (including its reproduced notices), libjpeg-turbo, libpng, libwebp, OpenJPEG, TIFF, liblzma/XZ and zlib-ng notices. The complete upstream license collection is retained. The wheel contains PIL .py/.pyi/.pyd files and metadata, not the XZ GPL command scripts or build system.

- FreeType is dual licensed. **This distribution selects the FreeType License (FTL), not GPL.** This product includes software developed by the FreeType Project (https://freetype.org). All rights reserved. Retain the FTL text and attribution with the product. The included upstream license compilation also contains the unselected GPL text; its presence is not acceptance of that option.
- XZ's included notice states liblzma is 0BSD; GPL/LGPL statements apply to other tools/scripts/build files, not the liblzma used here. This product includes code from XZ Utils (https://tukaani.org/xz/).
- ReportLab's wheel also carries Bitstream Vera fonts/license. They are not selected by our renderer, but distribution still retains `bitstream-vera-LICENSE.txt` and the original wheel copy. Their names cannot be reused for modified font distributions and fonts cannot be sold alone.
- Keep all upstream notices intact, including patent/warranty/non-endorsement terms; ADD Apache-2.0 does not replace third-party licenses. No mandatory GPL/AGPL component was identified in this selected closure; do not generalize this conclusion to other wheels/versions.

Sources: fixed PyPI URLs in upstream.json; font and OFL from the same pinned GitHub commit. The GitHub release-asset download stalled and was stopped; the font actually bundled came from the pinned raw repository, with its own recorded SHA-256. License checking is the minimum technical redistribution check, not legal advice or a commercial-release approval.

## Packaging and runtime

Keep all three wheels, full font, license files and this record in `vendor/pdf/`. Keep the existing `vendor/pypdf-6.19.0-py3-none-any.whl` / license for readback. The host must already provide **Windows x64 / CPython 3.12** for this Pillow wheel. No runtime, pip installer, system font or paid service is bundled/required by the renderer itself. Other runtime/OS combinations fail explicitly; their compatible-wheel packaging has not been verified. There is one business implementation, not multiple host-specific branches.

`scripts/pdf_bundle.py` authenticates original wheels, unpacks them only into the caller's explicit project-local `.tmp-*` runtime, and verifies every original file on reuse. It never silently repairs existing content. The runtime is a wheel extraction, not a pip installation; no global config/site-packages changes. In-process bytecode writing is disabled for these imports so unchecked cache files are not consumed on later reuse. Foreign preloaded packages/hooks and RL_* environment settings are rejected; ReportLab's home-directory hooks and system font search paths are explicitly neutralized in process. Upstream code is unchanged.

The whole original font is 25575676 bytes; three compressed wheels total 9244495 bytes and expand to 19638564 bytes. Thus this renderer's wheel+font payload is 34820171 bytes, plus licenses/docs; existing pypdf adds 395480 bytes. On first execution another 19638564 bytes of wheel runtime is written. Per-run hashes and unpack/verify costs are measured, not omitted. Future font size reduction would require separate coverage/license/quality verification; it is not done here.
