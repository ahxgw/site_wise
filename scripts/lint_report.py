#!/usr/bin/env python3
"""Lint Site Wise reports for evidence discipline.

Checks:
- lede is at most 25 words (it doubles as the index-card summary)
- every `inferred` tag sits in a block that names its basis ("Basis:")
- every `verified` tag sits in a block with a source link or a probe reference
- leftover template placeholders ($host, $date, "max 25 words", etc.)

By default lints the most recent report date; use --all for every report.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"

LEDE_WORD_LIMIT = 25
BLOCK_OPENERS = ("<li", "<tr", "<dd", "<p", "<div")
BLOCK_CLOSERS = ("</li>", "</tr>", "</dd>", "</p>", "</div>")
PROBE_HINTS = ("probe", "observed", "robots.txt", "curl", "dig ", "sitemap")
PLACEHOLDER_PATTERNS = (r"\$host", r"\$date", r"\$grouped_hosts", r"max 25 words", r"Max 200 words")


def enclosing_block(text: str, index: int) -> str:
    start = max((text.rfind(opener, 0, index) for opener in BLOCK_OPENERS), default=0)
    ends = [pos for closer in BLOCK_CLOSERS if (pos := text.find(closer, index)) != -1]
    end = min(ends) if ends else min(index + 500, len(text))
    return text[start:end]


def plain(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<.*?>", "", text)).strip()


def lint_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    problems: list[str] = []

    lede = re.search(r'<p class="lede">(.*?)</p>', text, re.S)
    if lede:
        words = plain(lede.group(1)).split()
        if len(words) > LEDE_WORD_LIMIT:
            problems.append(f"lede is {len(words)} words (limit {LEDE_WORD_LIMIT})")

    for match in re.finditer(r'class="evidence inferred"', text):
        block = enclosing_block(text, match.start())
        if "basis" not in block.lower():
            problems.append(f"inferred without 'Basis:': {plain(block)[:110]}")

    for match in re.finditer(r'class="evidence verified"', text):
        block = enclosing_block(text, match.start())
        if "<a " not in block and not any(hint in block.lower() for hint in PROBE_HINTS):
            problems.append(f"verified without source link or probe: {plain(block)[:110]}")

    for pattern in PLACEHOLDER_PATTERNS:
        if re.search(pattern, text):
            problems.append(f"template placeholder left in report: {pattern}")

    return problems


def target_reports(lint_all: bool, paths: list[str]) -> list[Path]:
    if paths:
        return [Path(p) for p in paths]
    dated = sorted(d for d in REPORTS_DIR.iterdir() if d.is_dir() and re.match(r"\d{4}-\d{2}-\d{2}", d.name))
    if not dated:
        return []
    if lint_all:
        return sorted(REPORTS_DIR.glob("*/*.html"))
    return sorted(dated[-1].glob("*.html"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="Report HTML files to lint. Defaults to the latest date.")
    parser.add_argument("--all", action="store_true", help="Lint every report, including legacy ones.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when problems are found.")
    args = parser.parse_args()

    total = 0
    for path in target_reports(args.all, args.paths):
        problems = lint_file(path)
        total += len(problems)
        label = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
        for problem in problems:
            print(f"{label}: {problem}")

    if total == 0:
        print("No problems found.")
    else:
        print(f"{total} problem(s).")
    return 1 if (args.strict and total) else 0


if __name__ == "__main__":
    raise SystemExit(main())
