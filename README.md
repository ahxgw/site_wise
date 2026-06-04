# Site Wise

Site Wise is a daily research project for understanding high-traffic websites in depth.

Each day, the project selects one site from a local private `top_site.jsonl` file by traffic rank and produces a structured analysis of its origin, product, traffic, business model, technical signals, moat, risks, and lessons. The long-term goal is to build a practical map of how the web actually works: who owns the major destinations, why users go there, how traffic flows, where money is made, and what patterns repeat across categories.

## Core Question

For each website, answer:

> What is this site, why did it become important, how does it work, and what can we learn from it?

For every report, also answer the index-builder version of the question:

> If we had to build a full-modal index for this site, what exactly can be indexed, how many objects exist, which modalities dominate, how are objects keyed and joined, how fresh is the corpus, and what reuse is allowed?

## Inputs

- `top_site.jsonl`: local private candidate-site data, one JSON object per line. This file is intentionally ignored by Git and should not be committed.
- Public web sources: official pages, company filings, help centers, news, product docs, historical records, and observable site behavior.
- Technical observations: DNS, redirects, page structure, metadata, performance, security headers, CDN signals, and visible third-party integrations.

To run site selection locally, create `top_site.jsonl` at the repository root with records like:

```json
{"host": "example.com", "traffic_score": 1.0, "authority_score": 2.0}
```

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

For phone viewing, GitHub Pages is deployed by the `Deploy GitHub Pages` workflow in `.github/workflows/pages.yml`. The workflow publishes the built `docs/` directory from `main` whenever the reader, reports, assets, build script, or workflow changes. In the repository settings, set Pages to use GitHub Actions as the source.

## Report Structure

Use `reports/template.html` as the default outline. The main sections are:

- One-sentence understanding
- Basic profile
- Key metrics, including traffic, revenue, object counts, modality mix, data volume, freshness, metadata coverage, and licensing coverage
- Timeline
- User intent and core scenarios
- Traffic and distribution
- Product anatomy
- Business model
- Moat
- Technical signals
- Search and retrieval perspective, written from the perspective of building a full-modal index
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

1. Pick one host from the local private `top_site.jsonl`.
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
- `order`: use the first unreported site in the local private `top_site.jsonl`.

## Research Principles

- Separate verified facts from inference.
- Prefer primary sources when available.
- Include dates for major events.
- Be numerically sensitive. Treat object counts, modality split, data volume, freshness/update rate, structured metadata coverage, and licensing/reuse coverage as first-class facts, not appendix details.
- Format large numbers for reading. In report prose and tables, prefer compact units such as `70K`, `1.2M`, `20B`, `1.1PB`, and `987TiB`; do not display long raw integers unless the exact ID-like value is itself meaningful. Exact raw values can live in source notes or structured profiles when needed.
- For each quantitative claim, include the figure, as-of date, source, and whether the number is directly reported or calculated by Site Wise.
- If a critical number is unavailable, write `open` and say what query, API, dump, panel, or measurement would be needed to standardize it.
- Search/retrieval analysis must assume a full-modal index: text, images, video, audio, documents, structured records, comments/reviews, metadata, entities, generated derivatives, and cross-modal joins.
- Define the indexable unit precisely. Examples: page, paragraph, post, video, transcript segment, frame/keyframe, thumbnail, audio track, comment, product, review, file, table row, entity, or bounding region.
- Identify stable IDs and joins across modalities: canonical URL, internal ID, revision ID, creator/account ID, entity ID, media ID, transcript timestamp, caption language, thumbnail, EXIF/geodata, license, and structured metadata.
- State the legitimate indexing path: public crawl, sitemap, RSS, official API, bulk dump, firehose, partner feed, paid endpoint, browser rendering, or no legitimate bulk path.
- Record uncertainty instead of smoothing it away.
- Look for the system behind the site: incentives, distribution, ownership, user behavior, and technical constraints.
- End each report with reusable lessons, not just trivia.
