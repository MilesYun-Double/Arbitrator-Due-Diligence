# Bundled PDF extraction candidate

Pinned component: **pypdf 6.19.0**, original unmodified pure-Python wheel.

- Upstream: https://github.com/py-pdf/pypdf
- Release metadata verified 2026-09-25: https://pypi.org/pypi/pypdf/6.19.0/json
- Artifact: https://files.pythonhosted.org/packages/3c/2c/c43c03eaf630435f023f1dc61ec4a4a78951ad5530a62c71cc89bde307b7/pypdf-6.19.0-py3-none-any.whl
- Size: 395480 bytes.
- SHA-256: `7e5d6e730e7dae87d560a2cee218b852f6498c8be61966f3cd02ead971e48d14` (verified against release metadata and checked before loading).
- License: BSD-3-Clause. `pypdf-LICENSE.txt` is copied unchanged from the wheel's `pypdf-6.19.0.dist-info/licenses/LICENSE`; original metadata/license remain inside the wheel. Preserve both when redistributing. ADD's Apache license does not replace this license.

This capability requires an **already available Python >=3.11**. The release supports >=3.9, but <3.11 requires typing_extensions; ADD deliberately does not ship or auto-install that additional dependency in this scope. No crypto/image/font/OCR extras are included. Encrypted input is rejected.

`scripts/pdf_source.py` uses zipimport from this exact wheel and refuses a hash mismatch or an already-loaded different pypdf. No pip invocation, network download or global configuration change occurs at runtime. A future Skill ZIP must include this directory alongside scripts and be extracted before execution; a wheel inside an unopened ZIP is not an executable environment. A host without compatible Python remains unsupported/UNKNOWN, not silently repaired by installation.

Local synthetic tests and fresh `python -E -S` CLI calls demonstrate the package can run without site-packages here. This is a bounded adoption candidate, not proof of arbitrary PDF quality, hostile-input isolation, all platforms or all hosts. Upstream code was not modified.
