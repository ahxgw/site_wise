#!/usr/bin/env python3
"""Build the mobile-friendly static Site Wise reader under docs/."""

from __future__ import annotations

import html
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"
ASSETS_DIR = ROOT / "assets"


def report_title(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"<h1>(.*?)</h1>", text, re.S)
    if not match:
        return path.stem
    return re.sub(r"<.*?>", "", match.group(1)).strip()


def report_summary(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(r'<p class="lede">(.*?)</p>', text, re.S)
    if not match:
        return ""
    return re.sub(r"\s+", " ", re.sub(r"<.*?>", "", match.group(1))).strip()


def report_date(path: Path) -> str:
    try:
        return path.parent.name
    except IndexError:
        return ""


def copy_reports() -> list[Path]:
    target_reports = DOCS_DIR / "reports"
    if target_reports.exists():
        shutil.rmtree(target_reports)
    target_reports.mkdir(parents=True, exist_ok=True)

    copied = []
    for source in sorted(REPORTS_DIR.glob("*/*.html"), reverse=True):
        target_dir = target_reports / source.parent.name
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / source.name
        html_text = source.read_text(encoding="utf-8")
        html_text = html_text.replace('href="../../docs/index.html"', 'href="../../index.html"')
        target.write_text(html_text, encoding="utf-8")
        copied.append(target)
    return copied


def copy_assets() -> None:
    target = DOCS_DIR / "assets"
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(ASSETS_DIR, target)


def write_index(reports: list[Path]) -> None:
    cards = []
    for path in reports:
        rel = path.relative_to(DOCS_DIR)
        source_path = ROOT / "reports" / path.parent.name / path.name
        cards.append(
            f"""<a class="report-card" href="{html.escape(str(rel))}">
  <strong>{html.escape(report_title(source_path))}</strong>
  <span>{html.escape(report_date(source_path))}</span>
  <p>{html.escape(report_summary(source_path))}</p>
</a>"""
        )

    index = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Site Wise</title>
  <link rel="stylesheet" href="assets/site.css">
</head>
<body>
  <main class="site-shell">
    <header class="site-hero">
      <p class="eyebrow">Site Wise</p>
      <h1>Daily Site Profiles</h1>
      <p class="lede">A mobile-friendly archive for deep profiles of high-traffic websites.</p>
      <p class="note">Open this page from GitHub Pages on a phone to read the reports directly.</p>
    </header>
    <section class="report-list">
      {''.join(cards)}
    </section>
  </main>
</body>
</html>
"""
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    (DOCS_DIR / "index.html").write_text(index, encoding="utf-8")


def main() -> int:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    copy_assets()
    reports = copy_reports()
    write_index(reports)
    print(f"Built {len(reports)} report(s) under {DOCS_DIR.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
