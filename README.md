# Site Wise

Site Wise is a daily research project for understanding high-traffic websites in depth.

Each day, the project selects one site from `top_site.jsonl` by traffic rank and produces a structured analysis of its origin, product, traffic, business model, technical signals, moat, risks, and lessons. The long-term goal is to build a practical map of how the web actually works: who owns the major destinations, why users go there, how traffic flows, where money is made, and what patterns repeat across categories.

## Core Question

For each website, answer:

> What is this site, why did it become important, how does it work, and what can we learn from it?

## Inputs

- `top_site.jsonl`: candidate sites, one JSON object per line.
- Public web sources: official pages, company filings, help centers, news, product docs, historical records, and observable site behavior.
- Technical observations: DNS, redirects, page structure, metadata, performance, security headers, CDN signals, and visible third-party integrations.

## Daily Output

Each daily report should live as a mobile-friendly HTML file under:

```text
reports/YYYY-MM-DD/host.html
```

Example:

```text
reports/2026-06-03/youtube.com.html
```

Reports should be readable as standalone web pages, but structured enough that facts can later be extracted into JSON profiles.

## Mobile Reader

The `docs/` directory contains the static reader for GitHub Pages. Build it with:

```bash
python3 scripts/build_site.py
```

This copies HTML reports into `docs/reports/`, copies shared CSS into `docs/assets/`, and writes `docs/index.html`.

For phone viewing, publish the repository with GitHub Pages using `main` branch / `docs` folder. Once Pages is active, open the Pages URL on your phone and read reports from the index.

## Report Structure

Use `reports/template.html` as the default outline. The main sections are:

- One-sentence understanding
- Basic profile
- Timeline
- User intent and core scenarios
- Traffic and distribution
- Product anatomy
- Business model
- Moat
- Technical signals
- Risks and future
- Lessons
- Sources

## Structured Profiles

The schema in `schema/site_profile.schema.json` defines the target structure for machine-readable site profiles. Reports can be written first, then distilled into structured JSON later.

The structured layer should help answer cross-site questions such as:

- Which top sites are owned by the same parent company?
- Which sites rely heavily on search traffic?
- Which sites have high traffic but low authority?
- Which business models dominate each category?
- Which countries, languages, and ecosystems are overrepresented?

## Site Selection Ideas

Possible selection strategies:

- Go from highest `traffic_score` to lowest.
- Preserve the original file order as the tie-breaker.
- Aggregate language or regional variants when they represent one product. For example, `ru.wikipedia.org`, `es.wikipedia.org`, and other language editions are treated as one `wikipedia.org` research target.
- Rotate weekly themes, such as search, video, AI, commerce, news, sports, tools, adult, or regional portals.
- Start with infrastructure-level destinations like `youtube.com`, `google.com`, `wikipedia.org`, `amazon.com`, `reddit.com`, `tiktok.com`, and `chatgpt.com`.

## Daily Workflow

1. Pick one host from `top_site.jsonl`.
2. Create `reports/YYYY-MM-DD/host.html` from `reports/template.html`.
3. Gather sources and technical observations.
4. Fill the report with sourced facts, explicit inferences, and open questions.
5. Optionally create or update a structured profile that conforms to `schema/site_profile.schema.json`.
6. Commit the report and any profile updates.

You can pick the next site with:

```bash
python3 scripts/select_site.py
```

Create a draft report for the selected site with:

```bash
python3 scripts/select_site.py --create-draft
```

After writing or updating reports, rebuild the mobile reader:

```bash
python3 scripts/build_site.py
```

Selection strategies:

- `traffic`: use the highest-traffic unreported site, aggregating configured variants such as Wikipedia language editions.
- `order`: use the first unreported site in `top_site.jsonl`.

## Research Principles

- Separate verified facts from inference.
- Prefer primary sources when available.
- Include dates for major events.
- Record uncertainty instead of smoothing it away.
- Look for the system behind the site: incentives, distribution, ownership, user behavior, and technical constraints.
- End each report with reusable lessons, not just trivia.
