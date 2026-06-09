#!/usr/bin/env python3
"""Select a Site Wise daily research target."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from string import Template


ROOT = Path(__file__).resolve().parents[1]
TOP_SITE_PATH = ROOT / "top_site.jsonl"
TEMPLATE_PATH = ROOT / "reports" / "template.html"
REPORTS_DIR = ROOT / "reports"
AGGREGATED_HOSTS = {
    "facebook.com": {
        "match_hosts": ("m.facebook.com", "mbasic.facebook.com", "touch.facebook.com"),
        "match_suffixes": (),
        "note": "Mobile/basic/touch Facebook hosts are analyzed together as Facebook.",
    },
    "imdb.com": {
        "match_hosts": ("m.imdb.com",),
        "match_suffixes": (),
        "note": "Mobile IMDb hosts are analyzed together as IMDb.",
    },
    "youtube.com": {
        "match_hosts": ("m.youtube.com",),
        "match_suffixes": (),
        "note": "Mobile YouTube hosts are analyzed together as YouTube.",
    },
    "wikipedia.org": {
        "match_hosts": (),
        "match_suffixes": (".wikipedia.org",),
        "note": "Language editions are analyzed together as Wikipedia.",
    },
    "yelp.com": {
        "match_hosts": ("m.yelp.com",),
        "match_suffixes": (),
        "note": "Mobile Yelp hosts are analyzed together as Yelp.",
    }
}


def load_sites(path: Path) -> list[dict]:
    sites = []
    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                sites.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_number}: {exc}") from exc
    return sites


def report_exists(host: str) -> bool:
    return any(REPORTS_DIR.glob(f"*/{host}.html"))


def canonical_host(host: str) -> str:
    for canonical, rule in AGGREGATED_HOSTS.items():
        if host == canonical:
            return canonical
        if host in rule.get("match_hosts", ()):
            return canonical
        if any(host.endswith(suffix) for suffix in rule["match_suffixes"]):
            return canonical
    return host


def aggregate_sites(sites: list[dict]) -> list[dict]:
    grouped: dict[str, dict] = {}

    for rank, site in enumerate(sites, start=1):
        host = site["host"]
        canonical = canonical_host(host)
        traffic = float(site.get("traffic_score") or 0)
        authority = float(site.get("authority_score") or 0)

        group = grouped.setdefault(
            canonical,
            {
                "host": canonical,
                "traffic_score": traffic,
                "authority_score": authority,
                "rank": rank,
                "members": [],
            },
        )
        group["rank"] = min(group["rank"], rank)
        group["traffic_score"] = max(float(group["traffic_score"]), traffic)
        group["authority_score"] = max(float(group["authority_score"]), authority)
        group["members"].append(site)

    aggregated = []
    for site in grouped.values():
        if len(site["members"]) > 1 or site["host"] in AGGREGATED_HOSTS:
            site["aggregated"] = True
            site["aggregation_note"] = AGGREGATED_HOSTS[site["host"]]["note"]
        else:
            site.pop("members")
        aggregated.append(site)

    return aggregated


def is_reported(site: dict) -> bool:
    if report_exists(site["host"]):
        return True
    return any(report_exists(member["host"]) for member in site.get("members", []))


def traffic_key(site: dict) -> tuple[float, int]:
    return (-float(site.get("traffic_score") or 0), int(site.get("rank") or 0))


def select_site(sites: list[dict], strategy: str) -> dict:
    candidates = [site for site in aggregate_sites(sites) if not is_reported(site)]
    if not candidates:
        raise ValueError("No unreported sites remain.")

    if strategy == "traffic":
        return sorted(candidates, key=traffic_key)[0]
    if strategy == "order":
        return candidates[0]

    raise ValueError(f"Unknown strategy: {strategy}")


def create_draft(site: dict, date: str) -> Path:
    template = Template(TEMPLATE_PATH.read_text(encoding="utf-8"))
    report_dir = REPORTS_DIR / date
    report_dir.mkdir(parents=True, exist_ok=True)

    path = report_dir / f"{site['host']}.html"
    if path.exists():
        raise FileExistsError(f"Report already exists: {path}")

    content = template.safe_substitute(
        host=site["host"],
        date=date,
        grouped_hosts=", ".join(member["host"] for member in site.get("members", [])),
    )
    path.write_text(content, encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strategy",
        choices=["traffic", "order"],
        default="traffic",
        help="How to choose the next site. Defaults to traffic.",
    )
    parser.add_argument(
        "--date",
        default=dt.date.today().isoformat(),
        help="Report date in YYYY-MM-DD format. Defaults to today.",
    )
    parser.add_argument(
        "--create-draft",
        action="store_true",
        help="Create reports/YYYY-MM-DD/host.html from the report template.",
    )
    args = parser.parse_args()

    sites = load_sites(TOP_SITE_PATH)
    site = select_site(sites, args.strategy)

    print(json.dumps(site, ensure_ascii=False))

    if args.create_draft:
        path = create_draft(site, args.date)
        print(path.relative_to(ROOT))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
