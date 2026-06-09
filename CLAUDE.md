# Site Wise — agent notes

Daily research project: one deep report per day on a high-traffic site, written for someone building a full-modal web search index. Authoring rules live in `pages/methodology.html`; workflow and structure in `README.md`; the outline in `reports/template.html`. Read those before writing any report.

## Non-negotiables for every report

- Probe first, write second. Run the probes (robots.txt, headers, DNS, sitemap census, structured-data sample, public API sample) before researching sources; record them in the Probe Log with the **actual date the probe ran**.
- Every number: figure + as-of date + source link. Sums/derivations are marked "calculated by Site Wise".
- Every `inferred` tag carries an inline `Basis:` naming a concrete signal. No basis → delete the claim.
- Open items appear exactly once, in Open Questions, each with the measurement that would close it.
- Lede ≤ 25 words. Whole report should land near 20KB; if it's pushing 30KB+, it has accumulated boilerplate — cut, don't tag.
- Verify before committing: `python3 scripts/lint_report.py <file>` must report zero problems (default run lints only the latest date dir — pass the path explicitly when regenerating older reports), then `python3 scripts/build_site.py`.

## Regenerating the legacy reports (backlog)

These seven predate the probe-first template and should be regenerated **in place** (same path, same filename, original date dir kept):

- [x] `reports/2026-06-03/youtube.com.html`
- [x] `reports/2026-06-04/wikipedia.org.html`
- [ ] `reports/2026-06-05/facebook.com.html`
- [ ] `reports/2026-06-06/reddit.com.html`
- [ ] `reports/2026-06-07/google.com.html`
- [ ] `reports/2026-06-08/instagram.com.html`
- [ ] `reports/2026-06-09/tiktok.com.html`

Rules: start from `reports/template.html`, run fresh probes (Probe Log dated the regeneration day, not the directory date), re-source all numbers (don't trust the old report's claims — several lack sources), lint each file explicitly, rebuild docs, tick the checkbox here. Salvage from the old version only what survives the evidence rules; the old Search-and-Retrieval prose is mostly cross-site boilerplate now covered by the methodology page. One commit per report, message style: `Regenerate 2026-06-0X host report on probe-first template`. `reports/2026-06-10/amazon.com.html` is the reference example of the target standard.

## Operational notes

- `sec.gov` returns 403 to WebFetch; use `curl -s -A "SiteWise research (kunka@apitech.ai)" <url>` and strip tags locally. Big platforms (amazon, instagram) often block plain curl too — a failed fetch is itself a Probe Log observation, not a dead end.
- `local_demos/` is intentionally git-ignored and private. Never move it into `docs/`, link it from published pages, or commit it.
- Mobile rendering: `build_site.py` injects `data-label` into table cells so tables become stacked cards on phones — table column headers must stay short. To eyeball a page at phone width: install playwright in /tmp (`cd /tmp && npm i playwright`), then screenshot at viewport 390px.
- Commit style: infra changes and report content go in separate commits. Daily report commits look like `Add 2026-06-10 Amazon report`. Push only when asked; pushing `main` triggers the GitHub Pages deploy.
