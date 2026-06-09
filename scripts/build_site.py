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
PAGES_DIR = ROOT / "pages"
SUMMARY_WORD_LIMIT = 40


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


def truncate_words(text: str, limit: int = SUMMARY_WORD_LIMIT) -> str:
    words = text.split()
    if len(words) <= limit:
        return text
    return " ".join(words[:limit]) + "…"


def inject_table_labels(html_text: str) -> str:
    """Add data-label="<column header>" to every td so the mobile CSS can
    render table rows as stacked cards with per-cell headings."""

    def process_table(table_match: re.Match) -> str:
        table = table_match.group(0)
        headers = [
            html.unescape(re.sub(r"<.*?>", "", header)).strip()
            for header in re.findall(r"<th[^>]*>(.*?)</th>", table, re.S)
        ]
        if not headers:
            return table

        def process_row(row_match: re.Match) -> str:
            cell_index = -1

            def add_label(td_match: re.Match) -> str:
                nonlocal cell_index
                cell_index += 1
                attrs = td_match.group(1)
                if cell_index >= len(headers) or "data-label" in attrs:
                    return td_match.group(0)
                label = html.escape(headers[cell_index], quote=True)
                return f'<td data-label="{label}"{attrs}>'

            return re.sub(r"<td([^>]*)>", add_label, row_match.group(0))

        return re.sub(r"<tr[^>]*>.*?</tr>", process_row, table, flags=re.S)

    return re.sub(r"<table[^>]*>.*?</table>", process_table, html_text, flags=re.S)


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
        html_text = html_text.replace('href="../../docs/', 'href="../../')
        html_text = inject_table_labels(html_text)
        target.write_text(html_text, encoding="utf-8")
        copied.append(target)
    return copied


def copy_pages() -> None:
    """Copy shared standalone pages (e.g. methodology) into docs/."""
    if not PAGES_DIR.exists():
        return
    for source in sorted(PAGES_DIR.glob("*.html")):
        (DOCS_DIR / source.name).write_text(
            inject_table_labels(source.read_text(encoding="utf-8")), encoding="utf-8"
        )


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
  <p>{html.escape(truncate_words(report_summary(source_path)))}</p>
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
    copy_pages()
    reports = copy_reports()
    write_index(reports)
    print(f"Built {len(reports)} report(s) under {DOCS_DIR.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
