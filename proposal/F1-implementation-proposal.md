# Proposal: Implement the Integration Scenario Registry (F1)

**To:** Bridget, LYRASIS  
**From:** Ryan Morrison-Westphal  
**Date:** September 18, 2026  
**Subject:** Quote for implementing Tech Spec F1 — Integration Scenario Registry (v0.4 Final)  
**Rate:** $120 / hour  
**Reference:** *Integration Scenario Registry Technical Specification*, Document Status: Final, Version 0.4 (July 2026)

---

## 1. Summary

I am interested in implementing the accepted **GitHub-native** Integration Scenario Registry.

This proposal covers **Phase I** as defined in the final spec: a public registry of CST integration scenarios stored as YAML in GitHub, validated by GitHub Actions, discovered via a static search UI on GitHub Pages, with Issue Form / PR contribution workflows and seed content.

**Phase II** (HTTP REST API over the same data) is scoped as an **optional add-on**, consistent with the spec’s deferral of machine write/harvest endpoints.

During the specification phase I produced a **small exploratory sample** (a few example scenario YAML files and a draft schema sketch). That sample illustrates the intended data shape; it is **not** a production-ready registry. Phase I still includes building Actions, contribution forms, index automation, the search UI, documentation, and a full seed set from scratch.

| Package | Estimated hours | Fee @ $120/hr |
|---------|-----------------|---------------|
| **Phase I — MVP (recommended)** | **100–120** | **$12,000 – $14,400** |
| Optional: Phase II — read API wrapper (O1) | 16–24 | $1,920 – $2,880 |
| Optional: Issue → YAML automation (O2) | 12–16 | $1,440 – $1,920 |
| Optional: post-MVP support retainer (O3) | 5–10 / month | $600 – $1,200 / month |

**Recommended ask:** approve **Phase I** as a **fixed-fee engagement of $13,200** for the Phase I deliverables listed below. Optional O1–O3 are separate add-ons, not included in that fee.

---

## 2. Understanding of scope (Phase I)

Per the final spec, Phase I delivers:

| Capability | Spec mapping |
|------------|--------------|
| Public read of scenario records | Actors: Public user; BS-01–BS-04 |
| Structured deposit via GitHub Issue Form → maintainer PR, and/or direct YAML PR | Deposit paths; BS-05 (GitHub-bound) |
| Schema validation + duplicate advisories in CI | G-03; Error scenarios |
| UUID assignment / filename enforcement via Actions | Requirements map: UUID |
| `registry/index.json` rebuild on merge | Search UI data source |
| GitHub Pages SPA: filter, keyword, UUID search, detail page | Static UI sketch; BS-01–BS-04 |
| Seed **10–15** records (CST mix + related specs) | Seed content plan |
| Contributor / admin documentation | Other Requirements → Documentation |
| Reviewer merge gate + GitHub notifications | Moderation; BS-07 (partial) |
| No hard deletes; Retired/Recalled excluded from index | Deletions; No delete |

**Explicitly out of Phase I** (unless added as options below):

- `POST` / `PATCH` registry REST API (BS-06, BS-D08 API path, BS-10 harvest) — Phase II
- Custom role-based email service beyond GitHub notifications
- Automated Issue → YAML conversion bot (optional O2)
- Ongoing post-MVP support (optional O3)
- Link health monitoring cron
- AI prompt documents / export-to-integration-guide crawler
- Ongoing product ownership / community governance (G-01, G-02 — Lyrasis/PM)

---

## 3. Approach

1. **Build the registry data layer** under `lyrasisorghome` (or agreed org/repo): JSON Schema, vocabularies, validation scripts, index build, GitHub Actions.
2. **Ship contribution UX:** Issue Form, PR template, maintainer runbook for Issue → YAML conversion (automation optional as O2).
3. **Build GitHub Pages search UI** that consumes `index.json` (filters, keyword, UUID, detail, “View as JSON,” copy canonical URL).
4. **Populate 10–15 seed records** from existing Interoperability Project specs and agreed community examples.
5. **Write public docs** covering auth, submit, update, search, review, export of `index.json`, troubleshooting.
6. **Handoff:** repo settings checklist, Roles/Reviewers walkthrough, acceptance against BS-01–BS-05 / BS-07–BS-09 (GitHub bindings).

---

## 4. Work packages and effort

Hour ranges are planning estimates used to set the fixed fee. Under a fixed-fee agreement, LYRASIS pays for the **agreed deliverables**, not for hours actually spent (see §5).

### Phase I — included

| # | Work package | Hours | Notes |
|---|--------------|------:|-------|
| W1 | Repo scaffold + schema (G-03) + vocabularies aligned to final data model | 8–12 | Includes fields from final spec (`github_id`, system profiles, etc.); exploratory sample YAML is a starting reference only |
| W2 | GitHub Actions: validate PR, UUID assignment/enforcement, index rebuild, duplicate advisories | 18–24 | Includes setup time for Actions workflows and merge-path automation |
| W3 | Issue Form + PR template + contributor checklist | 6–8 | Controlled vocabularies in form dropdowns; three related contribution artifacts |
| W4 | GitHub Pages SPA (search, filter, sort, detail, JSON link, copy URL) | 28–36 | Largest item; BS-01–BS-04 |
| W5 | Seed content: 10–15 records + `related_spec_url` where applicable | 10–14 | Content gathering with CST contacts may add calendar time |
| W6 | Public documentation site (or docs in-repo) per Documentation section | 12–16 | Screenshots of real flows |
| W7 | Admin handoff, branch protection, CODEOWNERS/reviewers, acceptance walkthrough | 6–8 | Includes one training call |
| W8 | Contingency (spec drift, review cycles, a11y polish, CI troubleshooting) | 12–14 | Buffer for unfamiliar Actions tooling and review rounds |
| | **Phase I total** | **100–120** | |

### Optional add-ons (not in Phase I fee)

| # | Work package | Hours | Fee |
|---|--------------|------:|-----|
| O1 | **Phase II read API:** thin wrapper (e.g. Cloudflare Worker) implementing `GET /api/v1/scenarios`, `/{id}`, `/vocabularies`, `/schema` over `index.json` | 16–24 | $1,920 – $2,880 |
| O2 | **Issue → YAML automation:** when a contributor submits via Issue Form, a GitHub Action (or small bot) drafts `registry/scenarios/{uuid}.yaml` and opens a PR for human review/merge — reducing manual maintainer conversion | 12–16 | $1,440 – $1,920 |
| O3 | **Post-MVP monthly support** (bugfixes, small enhancements, seed assist) after Phase I acceptance — separate retainer agreement | 5–10 / mo | $600 – $1,200 / mo |

**Not estimated here:** authenticated write API (POST/PATCH), which implies auth design beyond GitHub and is a larger Phase II+ product decision.

---

## 5. Pricing

### How the fixed fee works

Phase I is offered as a **fixed fee for a fixed scope**.

- The **100–120 hour range** is an internal estimate used to price the work fairly.
- The **$13,200 fixed fee** is the price for completing the Phase I deliverables in §7, whether actual effort lands nearer 100 or 120 hours.
- If LYRASIS requests **new scope** (e.g. write API, formal WCAG audit, Issue→YAML bot), that is a **written change order**, not an automatic +10 hours on the same fee.
- Alternatively, Phase I can be billed **time-and-materials** with a **not-to-exceed (NTE) ceiling of $14,400** (120 hours). Under T&M, only hours worked are billed, up to the ceiling, unless a change order raises the NTE.

| Offer | Structure | Amount |
|-------|-----------|-------:|
| **Phase I fixed fee (recommended)** | Fixed price for Phase I deliverables | **$13,200** |
| Phase I T&M alternative | Hourly @ $120, NTE 120 hours | Up to $14,400 |
| Optional O1 Phase II read API | Fixed (if elected) | $2,400 |
| Optional O2 Issue → YAML automation | Fixed (if elected) | $1,680 |
| Optional O3 post-MVP retainer | Monthly, after Phase I acceptance | $600 – $1,200 / mo |

**O3** is intentionally **not** part of the Phase I price: it is ongoing support after MVP handoff, only if LYRASIS wants a continuing engagement.

**Payment suggestion (fixed fee):** 40% on kickoff, 40% on MVP feature-complete (UI + CI + docs draft), 20% on acceptance / handoff.

**Expenses:** None expected. Hosting is GitHub (org account). If Lyrasis requires a paid Cloudflare (or similar) plan for O1, that subscription is billed to Lyrasis directly.

---

## 6. Timeline (indicative)

Assuming kickoff within two weeks of approval and timely access to the target GitHub org:

| Milestone | Target |
|-----------|--------|
| Kickoff + repo access + schema freeze | Week 1 |
| CI + contribution forms live; seed draft started | Weeks 2–4 |
| Pages UI beta for Lyrasis review | Weeks 5–6 |
| Docs + seed complete; acceptance | Weeks 7–8 |
| Handoff / training | Week 8–9 |

**Calendar duration:** ~7–9 weeks elapsed for Phase I, depending on review turnaround and seed-content availability from CST communities.

Optional Phase II / O2: +2–3 weeks after Phase I acceptance.

---

## 7. Deliverables checklist

- [ ] Registry repository under agreed LYRASIS org (structure, LICENSE, README)
- [ ] `registry/schema.json`, `vocabularies.yaml`, `scenarios/*.yaml`, generated `index.json`
- [ ] GitHub Actions for validation, UUID handling, index rebuild
- [ ] Issue Form + PR template + contributor checklist
- [ ] GitHub Pages search / detail UI meeting BS-01–BS-04
- [ ] 10–15 seed records
- [ ] Public user/admin documentation
- [ ] Handoff notes: roles, branch protection, how to approve/merge, how to extend vocabularies
- [ ] Short acceptance demo mapped to Phase I behavior scenarios

---

## 8. Assumptions and dependencies

1. Lyrasis provides **admin or maintainer access** to create/configure the registry repo in the correct org.
2. Product owners confirm **canonical base URL** for `record_url` / Pages site before seed finalization.
3. Seed content beyond the first ~4 spec-linked records depends on **CST contacts** providing examples; delays there extend calendar time, not necessarily billable hours if blocked.
4. “Email notifications” in Phase I = **GitHub’s native notification model** (as finalized in the spec), not a custom mailer.
5. Behavior scenarios written for a generic web app are satisfied via **GitHub bindings** (PR / Issue Form / Pages / `git log`), not a separate custom edit UI or live REST write API.
6. Accessibility: UI will follow sensible defaults (semantic HTML, keyboard filters, contrast); formal WCAG audit is out of scope unless added.
7. Phase I includes a **manual** maintainer path for Issue Form → YAML PR. Automated conversion is optional O2.

---

## 9. Why this is a good fit

- Continuity from F1 technical design work on the Interoperability Project.
- Spec already chose GitHub-native; hosting cost is near zero for Phase I.
- Phase I stays within the “simplest architecture” intent of the Performance section while leaving a clean Phase II path (`index.json` → API wrapper, no schema change).

---

## 10. Next steps

If this looks useful, I suggest:

1. Confirm **Phase I fixed fee ($13,200)** — or T&M with NTE $14,400 — and whether you want O1/O2 in the same SOW (O3 only after MVP if desired).
2. Confirm target GitHub org/repo name and who will be Global Registry Administrators.
3. Schedule a 30–45 minute kickoff to freeze any remaining open gaps (G-01/G-02 remain PM-owned).

Happy to adjust scope (e.g. fewer seed records, or Phase II in the same engagement) if that better matches budget or timeline.

—
Ryan Morrison-Westphal

---

## Appendix A — Hour → dollar quick reference

| Hours | @ $120 |
|------:|-------:|
| 100 | $12,000 |
| 110 | $13,200 |
| 120 | $14,400 |
| 20 (Phase II mid) | $2,400 |

