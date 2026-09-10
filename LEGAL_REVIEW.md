# Legal review checklist

The five pages under `/legal/` are **drafts**. They are structured, jurisdiction-aware and
better than having nothing, but they have not been reviewed by counsel.
`HubSign-Pricing-Plan.md` §6 already said the commercial terms need that review; this
extends it to the rest.

While `REVIEW_PENDING = True` in `landing/legal.py`, every legal page shows a review banner.
Flip that flag to `False` once counsel signs off — it removes the banner everywhere at once.

---

## 1. Blocking — facts only you can supply

These render as `[[NEEDS CONFIRMATION: ...]]` in the published pages and are reported by
`manage.py check` as `landing.W001`. Fill them in at `landing/company.py`.

| Detail | Why it is required |
|---|---|
| **Registered mailing address** | GDPR Art. 13(1)(a) identity/contact; CASL requires a physical mailing address in any commercial electronic message |
| **Ontario corporation number** | Ordinary corporate identification on published terms |
| **Privacy Officer name/title** | PIPEDA Principle 1 (Accountability) requires a designated, named individual |
| **Privacy contact address** | The channel for access and correction requests. `privacy@hubsign.io` is suggested but not created |

Also confirm:

- **The phone number.** `+1 810-626-EDGE` is a **Michigan** area code published by an Ontario
  company. Either it is a real US line (fine — but say which entity it reaches), or it is a
  placeholder that should be replaced.
- **`support@hubsign.io` exists.** It appears in the accessibility statement as the channel for
  reporting barriers, and previously only appeared in dead template copies.

## 2. Questions that change what the pages must say

1. **Employee headcount.** AODA's Integrated Accessibility Standards Regulation makes WCAG
   conformance a *legal obligation* for Ontario private organizations at 50+ employees. Below
   that it is best practice. The site targets WCAG 2.1 AA either way; the answer changes whether
   `/legal/accessibility/` is describing a statutory duty or a voluntary commitment.
2. **Do you have EU/UK customers today?** Offering goods or services to people in the EU/UK
   without an establishment there can require an **Art. 27 representative**. Canada holds an EU
   adequacy decision for PIPEDA-subject organizations, so transfers themselves are fine.
3. **Do you have Quebec users?** Law 25 obligations already reflected. Separately, the Charter
   of the French Language (as amended by Bill 96) may require a **French version** of a
   commercial website directed at Quebec residents. Not currently provided.
4. **Is there a Jamaican establishment?** `HubSign-Pricing-Plan.md` §6 refers to an in-region
   operation. Jamaica's Data Protection Act 2020 requires **registration with the Information
   Commissioner** and appointment of a **Data Protection Officer**.
5. **Consumer or business buyers?** Starter/Plus/Pro are priced for individuals. If consumers
   buy them, Ontario's Consumer Protection Act, 2023 and Quebec's CPA apply in full, and
   UK/EEA consumers get a statutory 14-day withdrawal right that cannot be waived.

## 3. The refund policy is deliberately unwritten

You chose to leave the commercial terms to counsel. `/legal/refunds/` therefore states plainly
that the policy is being finalised, tells people how to cancel, and sets out the statutory
rights that apply regardless. It commits to nothing.

`HubSign-Pricing-Plan.md` §6 already drafted three options — pro-rata refund of unused months,
account credit, or a 30-day money-back window only — with worked examples and competitor
benchmarks. That section is the input for the conversation with counsel.

Points from that section worth raising, whichever option is chosen:

- Ontario CPA 2023 and Quebec's CPA regulate **automatic renewal and advance notice**; a
  30-days-out renewal reminder is close to required in several jurisdictions.
- **Self-serve cancellation** matters more than the refund itself. A no-refund policy plus a
  cancellation maze is what turns annoyance into a chargeback.
- **Data export on exit** will close more deals than the refund terms. `/legal/refunds/` already
  commits to not withholding data over a billing dispute — confirm you can honour that.

## 4. Product claims the site makes that this repo cannot verify

These describe the HubSign **application**, which lives in a different codebase. If any is not
true today, it should come off the page — they are in `landing/views.py` and
`templates/landing/index.html`.

- "Sealing is one-way — stamps, certificate and field placement are fixed the moment the last recipient signs."
- "A Final Audit Report is appended, recording who signed, when, from where, and the document's integrity hash."
- "Verifiable independently from the QR code and share link printed on the certificate."
- "Two downloads, one sealed original."
- "Webhooks · 7 events" — also stated as a headline statistic. The seven are never enumerated.
- "REST API v1 stable, v2 in beta."
- "OCR confidence scoring" and the "needs-review flag" described in the FAQ.
- "Rule evaluation fails open by design."
- "Self-signup can be restricted to your domain."
- SSO against Microsoft Entra ID, Google Workspace, Okta and Auth0 — the page now says
  "Microsoft Entra ID (formerly Azure AD)", which is the current product name.

**Already fixed:** the meta description claimed "Fully compliant digital signatures" without
naming a standard, and the annual badge claimed a flat "Save 20%" when Business and Enterprise
Shared save 17%. Both were changed.

**Already removed:** dead files containing "Fully compliant. Out of the box.", "legally
binding", "256-bit Encryption", ESIGN/UETA/eIDAS badges and fake signer names. None was served,
but all were one `{% include %}` from being live. Do not reintroduce compliance badges without
evidence for each standard named.

## 5. Unrelated but worth knowing

**`?plan=` slug drift.** `LANDING_PLAN_PARAM_SPEC.md` documents the slugs app.hubsign.io
accepts as `free | individual | team | business | enterprise`, and says anything else is
*silently ignored*. The pricing CTAs now send `starter`, `plus` and `pro` — so three of the six
plan buttons lose their plan preselection after signup. This is an app-side change, not a
landing-site one, but the two need to agree.
