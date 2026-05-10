"""End-to-end build of Paper/MedFollow_JBI_submission.docx from
Paper/index.html using the html2doc skill, with figure paths rewritten
to absolute (so pandoc can locate them) and table vertical rules
stripped (Elsevier style requirement).

Pipeline:
  1. Stage 1: KaTeX -> MathML (Node + katex)
  2. (helper) Rewrite relative figures/ paths to absolute
  3. Stage 2: MathML -> DOCX with native OMML equations (Pandoc)
  4. Stage 3: Apply academic styling (python-docx, camera-ready-generic profile)
  5. (helper) Strip vertical rules from all tables (Paper/scripts/strip_table_vrules.py)
  6. Optionally re-run the DOCX audit

Usage:
    /c/Python314/python Paper/scripts/build_docx.py [--audit]

Requires:
  - Node.js + katex installed at C:\\Users\\apart\\.claude\\skills\\html2doc\\node_modules
  - Python deps: pypandoc, python-docx
  - Pandoc 3.1+ on PATH
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "Paper"
SKILL = Path(os.environ.get("HTML2DOC_SKILL", r"C:\Users\apart\.claude\skills\html2doc"))
PYTHON = os.environ.get("PYTHON", r"C:\Python314\python.exe")
TMP = PAPER / ".tmp_html2doc"


def run(cmd: list[str], **kw) -> None:
    print(f"$ {' '.join(map(str, cmd))}")
    r = subprocess.run(cmd, **kw)
    if r.returncode != 0:
        sys.exit(f"FAILED with exit code {r.returncode}: {' '.join(map(str, cmd))}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", action="store_true", help="Run audit_docx.py after build")
    args = parser.parse_args()

    TMP.mkdir(exist_ok=True)

    mathml_html = TMP / "paper_mathml.html"
    converted = TMP / "paper_converted.docx"
    final = PAPER / "MedFollow_JBI_submission.docx"

    # 1. KaTeX -> MathML
    env = os.environ.copy()
    env["NODE_PATH"] = str(SKILL / "node_modules")
    run([
        "node", str(SKILL / "scripts" / "katex_to_mathml.js"),
        "--input", str(PAPER / "index.html"),
        "--output", str(mathml_html),
    ], env=env)

    # 2. Rewrite figures/ paths to absolute so pandoc can resolve them
    text = mathml_html.read_text(encoding="utf-8")
    abs_dir = PAPER.as_posix()
    new = re.sub(r"""src=(["'])(figures/[^"']+)\1""",
                 lambda m: f'src={m.group(1)}{abs_dir}/{m.group(2)}{m.group(1)}', text)
    mathml_html.write_text(new, encoding="utf-8")
    print(f"  rewrote figures/* paths to absolute under {abs_dir}/")

    # 3. MathML -> DOCX
    run([PYTHON, str(SKILL / "scripts" / "convert_to_docx.py"),
         "--input", str(mathml_html),
         "--output", str(converted),
         "--profile", "camera-ready-generic"])

    # 4. Academic styling
    run([PYTHON, str(SKILL / "scripts" / "apply_academic_style.py"),
         "--input", str(converted),
         "--output", str(final),
         "--profile", "camera-ready-generic"])

    # 5. Strip vertical rules
    run([PYTHON, str(PAPER / "scripts" / "strip_table_vrules.py")])

    # 6. Optional audit
    if args.audit:
        run([PYTHON, str(PAPER / "scripts" / "audit_docx.py")])

    # Cleanup
    shutil.rmtree(TMP)
    print()
    print(f"DONE: {final.relative_to(ROOT)} ({final.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
