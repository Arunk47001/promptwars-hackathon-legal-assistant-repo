# Namma Nyaya — A GenAI Legal Companion for Bengaluru

## Summary

Namma Nyaya ("Our Justice" in Kannada) is a GenAI-powered legal companion built specifically for Bengaluru, India, rather than as a generic "simplify legal documents" tool. It lets people upload any legal document in any form (photo, scan, WhatsApp forward, voice note), get it explained in their own language at multiple levels of depth, have it checked against Bengaluru-specific and India-specific legal norms for red flags, ask cited questions about it, and — critically — get a concrete "what do I do now" action plan pointing to the exact local forum, portal, document, timeline, and cost. It differentiates itself through hyperlocal grounding (Khata types, RERA Karnataka, Kaveri portal, BBMP/BDA processes, Koramangala-vs-Whitefield rental norms), multilingual voice-first access (Kannada, Hindi, Tamil, Telugu, English), and a navigator layer that goes beyond explanation into actionable next steps — while staying firmly in "legal information, not legal advice" territory with strong responsible-AI guardrails. This matters because Bengaluru's population is unusually mixed (migrant tech workers, gig workers, first-time home buyers, senior citizens, small businesses, apartment residents) and each group faces different, often predatory, legal friction that generic legal-tech tools don't address because they aren't localized to Karnataka law, Kannada language, or Bengaluru's specific institutions.

## Problem / motivation

- Most "AI legal document simplifier" products are generic and India-agnostic: they don't know what an A-Khata vs B-Khata is, don't cite the Indian Contract Act or the new BNS/BNSS/BSA codes, and don't tell a user which Bengaluru office or portal to go to next.
- Legal documents that matter most to Bengaluru residents (rental agreements, offer letters, sale deeds, Khata documents) are frequently in Kannada or mix Kannada and English, and existing tools have poor or no OCR/understanding for Indian regional languages.
- Different population segments in Bengaluru face distinct, recurring legal problems that are largely undocumented in a single accessible tool:
  - Migrant tech professionals: exploitative rental deposits/deductions, one-sided lock-ins, unenforceable non-competes, training bonds, opaque ESOP terms.
  - First-time home buyers: A-Khata/B-Khata/e-Khata confusion, BDA/BMRDA approvals, DC conversion, OC/EC verification, RERA Karnataka registration, builder delays.
  - Gig/delivery workers, auto drivers, domestic workers: opaque platform contracts, unclear rights under Karnataka's gig-worker welfare law, traffic challans, wage disputes.
  - Senior citizens and families: wills, partition, gift deeds, maintenance rights, and a rising volume of "digital arrest" and cyber-fraud scams.
  - Small businesses/startups: vendor contracts, founder agreements, GST/tax notices, Shops & Establishments registration, DPDP Act compliance.
  - Apartment residents: RWA disputes, maintenance charges, builder-to-owners'-association handover.
- Even when a document is understood, most people don't know the next concrete step (which forum, which portal, what to file, how long it takes, what it costs) — this is where most legal-simplification tools stop, leaving users stuck.
- The 2023-24 replacement of IPC/CrPC/Evidence Act with BNS/BNSS/BSA has created widespread confusion, since most public references (including old articles and even some officials) still use old section numbers.

## Proposed idea

Build a multilingual, multimodal AI companion that:
1. Ingests any legal document a Bengaluru resident might encounter, in any common input format and in Kannada/Hindi/Tamil/Telugu/English.
2. Explains it at three levels of depth (one-line gist, clause-by-clause plain language, "legal view" with citations), togglable per-language so, e.g., a Kannada-speaking parent and an English-speaking adult child can both read the same document comfortably.
3. Flags red flags by comparing clauses against actual Indian/Karnataka law and locally-known norms (not a generic abstract "risk score").
4. Supports compare/diff workflows (landlord draft vs. fair model agreement, offer letter A vs. B, contract version 1 vs. version 2).
5. Answers user questions with citations back to the specific clause in their document and the specific section of law, with a confidence indicator, and refuses to answer (says "I don't know") when no source supports an answer.
6. Auto-translates old IPC/CrPC/Evidence Act section references to their new BNS/BNSS/BSA equivalents and vice versa.
7. Acts as a "navigator": for each recognized situation, generates the concrete next step — correct forum/authority, required documents, a draft letter/complaint/application where appropriate, rough timeline, and rough cost.
8. Offers a set of differentiating, Bengaluru-flavored features layered on top: "Before You Sign" prep mode, a property due-diligence checklist generator, a one-page "lawyer-ready brief" generator, a deadline/obligation tracker with reminders, a voice-first WhatsApp bot, an anonymized community "fairness index," and a scam-document detector.
9. Operates under explicit responsible-AI guardrails: information-not-advice framing, escalation to human/legal-aid help for high-stakes situations, retrieval grounded in a curated, citable source base with no fabrication, DPDP-Act-aligned privacy handling (PII masking, consent, minimal retention), and bias testing across languages.

## Scope

This project is being built for a time-boxed hackathon ("promptwars-hackathon"). The full vision above is large; the sections below separate what a hackathon build should actually target (MVP) from what is explicit stretch/full-vision scope, so the team doesn't try to boil the ocean in the time available.

### MVP (hackathon-scope, in-scope)

Pick a narrow but convincing vertical slice that demonstrates the differentiated hyperlocal value proposition end-to-end, rather than shallow coverage of everything. Recommended slice: **rental agreements + offer letters for migrant tech professionals**, because these are the most common, highest-volume documents, easiest to source sample data for, and don't require handling the highest-stakes categories (criminal, custody, large property transactions) that demand the most guardrail rigor.

In scope for MVP:
- Document upload: PDF and photo/image upload (OCR) for at least English + Kannada text. Voice note upload can be a stretch if time allows, but is not required for MVP.
- Three-level explanation (one-line gist, clause-by-clause plain language, legal-view with citation) for the chosen document types, in at least English and Kannada, with a language toggle.
- Local red-flag detection for rental agreements and offer letters specifically: deposit size norms, painting/cleaning deduction clauses, lock-in asymmetry, non-compete enforceability (Section 27, Indian Contract Act), training bond enforceability.
- Basic compare/diff: two documents (e.g., two offer letters, or landlord draft vs. a supplied "fair model" rental agreement) side by side on key clauses.
- Q&A with citations grounded in a small curated source set (a hand-picked set of statutes/sections relevant to the MVP's document types — Indian Contract Act, Karnataka Rent Act provisions, Karnataka Shops & Establishments Act as relevant), with an explicit "I don't know" fallback when no source is found.
- IPC/CrPC/Evidence Act → BNS/BNSS/BSA section-number lookup/mapping tool (this is small, self-contained, and high-value; suitable as a standalone MVP feature even before it's chained to the document flow).
- Navigator: at least 2-3 fully worked-out "Situation → Where to go → What the app generates" playbooks (e.g., deposit not returned; a template legal notice/demand letter), including the referenced forum, documents needed, and generated draft output.
- Baseline responsible-AI guardrails: an explicit "this is information, not legal advice" disclaimer surfaced in the UI; detection of at least one high-stakes trigger category (e.g., mentions of arrest, criminal charge, custody, divorce) that redirects the user to a "please consult a lawyer / free legal aid" message instead of answering; basic PII masking (Aadhaar/PAN pattern detection and redaction) before any document content is sent to a model or stored.

### Stretch / full-vision (explicitly out of scope for MVP, candidates if time remains or for post-hackathon roadmap)

- Full multilingual OCR/voice coverage across Kannada, Hindi, Tamil, Telugu, English for all document types (MVP targets English + Kannada text only, and text-first rather than voice-first).
- Full document-type coverage beyond rental/offer letters: sale deeds, Khata documents, wills, gift deeds, partition deeds, platform/gig-worker contracts, vendor/founder agreements, GST/tax notices, RWA documents.
- Property due-diligence checklist generator (A-Khata/B-Khata/e-Khata, EC via Kaveri, OC, DC conversion, RERA ID) — meaningful but deep enough (external portal knowledge, property-specific personalization) to be its own stretch milestone.
- "Before You Sign" mode (pre-meeting question/negotiation-point generator).
- Lawyer-ready one-page brief generator from full chat + document history.
- Deadline/obligation tracker with WhatsApp reminder delivery (requires WhatsApp Business API integration and persistent user data — a meaningful infra lift).
- Voice-first WhatsApp bot for low-literacy/non-app users (high inclusion value, but a separate integration surface from a web-based MVP demo).
- Community "fairness index" (requires an aggregated, anonymized dataset that a hackathon timeframe won't be able to populate meaningfully — would need seeded/synthetic data with a clear "illustrative, not statistically validated" disclaimer if demoed at all).
- Scam-document detector (fake court notices/police summons/digital-arrest letters) — valuable but needs its own curated pattern/reference set to avoid false confidence.
- Full navigator coverage of all seven listed situation types (deposit, builder delay, consumer complaint, cyber fraud, RTI, free legal aid eligibility, traffic challans) — MVP covers a small subset; the rest is roadmap.
- Any real filing/submission integration with government portals (e-Daakhil, RERA Karnataka, cybercrime.gov.in, RTI portals) — MVP should only generate drafts for the user to file themselves, never auto-submit anything.
- Production-grade retrieval pipeline over the full India Code + Karnataka Gazette + Indian Kanoon corpus — MVP uses a small hand-curated set of sources scoped to the chosen document types.
- Formal bias-testing framework across languages — MVP should at minimum spot-check Kannada vs. English answer quality but a rigorous bias-testing process is a full-vision commitment, not a hackathon deliverable.

### Explicitly out of scope regardless of timeframe (for this product, not just this hackathon)

- Providing definitive legal advice or representing itself as a substitute for a licensed advocate.
- Auto-filing or auto-submitting any legal complaint, RTI, or court document on the user's behalf without explicit human review and action.
- Storing documents or PII beyond what is strictly needed for the session, without explicit user consent.

## Key components / flow

1. **Ingestion layer** — accepts file upload (PDF/image) and, in fuller scope, voice notes; runs OCR (multilingual for Kannada/Hindi/Tamil/Telugu/English, e.g. via Bhashini/AI4Bharat/Sarvam-class models) to produce clean text; detects and masks Aadhaar/PAN/other PII patterns before any further processing or storage.
2. **Classification layer** — identifies document type (rental agreement, offer letter, sale deed, etc.) and routes to the appropriate explanation/red-flag/navigator logic; detects high-stakes trigger categories (criminal, arrest, custody, divorce, large property value) for early guardrail escalation.
3. **Explanation engine** — produces the three-level output (gist / clause-by-clause / legal view with citation) per clause or section, with a language toggle independent of the underlying source language.
4. **Red-flag engine** — a rules+retrieval hybrid that compares clauses against (a) a curated set of statutory provisions and (b) known local norms (e.g., typical Bengaluru deposit multiples), producing specific, sourced flags rather than an opaque score.
5. **Compare/diff engine** — aligns clauses across two documents or two versions of the same document and surfaces differences, especially quietly-inserted or changed clauses.
6. **Q&A / retrieval layer** — grounded retrieval over the curated source base (statutes, gazette notifications, portal instructions, and, in fuller scope, case law via Indian Kanoon); every answer must cite the specific clause and the specific legal source, include a confidence indicator, and fall back to "I don't know" when ungrounded.
7. **Old-to-new law mapping utility** — a lookup table/service mapping IPC/CrPC/Evidence Act sections to BNS/BNSS/BSA sections and back; usable standalone or inline within Q&A answers.
8. **Navigator engine** — a library of situation → forum/portal → generated-output playbooks (starting with a small MVP set), each producing a draft document (letter, complaint, application) plus a document checklist, rough timeline, and rough cost.
9. **Differentiator modules** (largely stretch scope) — Before-You-Sign prep, property due-diligence checklist, lawyer-ready brief generator, deadline/obligation tracker, WhatsApp voice bot, fairness index, scam-document detector — each a bounded add-on to the core pipeline above rather than a redesign of it.
10. **Responsible-AI guardrail layer** — cross-cutting: disclaimer surfacing, high-stakes escalation, grounding/no-fabrication enforcement on the Q&A and red-flag engines, PII masking and consent flow, and (in fuller scope) cross-language accuracy testing.

## Open questions / risks

- **Source curation scope for MVP.** Exactly which statutes/sections/portal references will be hand-curated for the demo, and who verifies their accuracy? This needs to be nailed down early since the whole "no made-up law" guarantee depends on it, and legal accuracy review is itself a bottleneck in a hackathon timeframe.
- **OCR quality for Kannada legal documents.** Real sale deeds/Khata documents often have poor scan quality, handwriting, or stamps; it's unconfirmed how well available OCR (Bhashini/AI4Bharat/Sarvam or alternatives) performs on this specific document class versus general Kannada text — needs early spike/testing before committing demo scope.
- **Definition of "local norms" for red-flagging.** Claims like "10-month deposits are common but high in Bengaluru" imply access to real aggregate rental-market data that likely doesn't exist in a structured, licensable form — need to decide whether MVP uses illustrative/anecdotal norms (clearly labeled as such) or skips quantitative norm claims entirely in favor of only law-grounded flags.
- **High-stakes detection false negatives.** A trigger-word/category detector for "criminal, arrest, custody, divorce" situations is a blunt instrument; risk of the app answering something it shouldn't, or of over-triggering and refusing legitimate low-stakes questions. Needs explicit test cases either way.
- **Confidence indicator methodology.** The spec calls for a "confidence indicator" on Q&A answers, but how confidence is computed (retrieval-score-based, model-self-reported, rule-based) is undefined and needs a decision before build.
- **Legal disclaimer and liability framing.** Even as a hackathon project, the team should get the "information, not advice" language and escalation behavior reviewed for correctness — this isn't just a UX nicety but a real risk-mitigation must-have if the product is ever used beyond a demo.
- **PII masking coverage.** Aadhaar/PAN pattern masking is called out explicitly, but other Indian PII (voter ID, driving license, bank account numbers appearing in documents like sale deeds) may also need masking — scope needs to be defined.
- **Data retention and consent flow specifics.** "Allow processing without storing documents" and "require explicit consent" are stated as principles but the actual default (store vs. ephemeral-only) and consent UX are undecided.
- **WhatsApp/voice bot feasibility within hackathon time.** This is flagged as high-inclusion-value but requires WhatsApp Business API access, which may not be obtainable within a hackathon window — needs an early go/no-go decision rather than being assumed available.
- **Fairness index data risk.** Without genuine aggregated data, any "fairness index" demo risks presenting fabricated-looking statistics as real; if attempted at all, needs a hard-coded "illustrative example, not statistically validated" disclaimer.
- **Judging/demo narrative.** Given the breadth of the full vision, there's a risk of the demo trying to show too many shallow features instead of one deep, convincing vertical slice — the MVP section above is written to force a narrower choice, but the team should explicitly commit to (and rehearse) one end-to-end user story before the demo.

## Status

Draft — 2026-09-23
