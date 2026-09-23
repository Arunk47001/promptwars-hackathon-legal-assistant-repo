"""Curated legal source set (C9).

A small, hand-curated set of statutory excerpts relevant to the MVP's chosen
document types (rental agreements, offer letters), each with a citation
label (statute + section), formatted into one reusable context block sized
for context-stuffing alongside a document's clauses into a Gemini Pro-class
prompt (per the plan's locked context-stuffing retrieval approach — no
vector store).

ACCURACY NOTE (per task-breakdown "Notes and assumptions" / C9): these
excerpts are paraphrased/condensed for a hackathon POC and have NOT been
independently legally reviewed. The task breakdown assumes the team itself
hand-verifies them before real-world use; treat the text below as
"good-faith curated for demo purposes," not a verified legal reference. Any
citation the app returns must trace back to one of the `id` values below —
this is the whole point of the context-stuffing approach (no fabricated
citations).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LegalSource:
    id: str
    statute: str
    section: str
    title: str
    text: str


CURATED_SOURCES: list[LegalSource] = [
    LegalSource(
        id="contract-act-s10",
        statute="Indian Contract Act, 1872",
        section="Section 10",
        title="What agreements are contracts",
        text=(
            "All agreements are contracts if they are made by the free consent "
            "of parties competent to contract, for a lawful consideration and "
            "with a lawful object, and are not hereby expressly declared to be "
            "void."
        ),
    ),
    LegalSource(
        id="contract-act-s27",
        statute="Indian Contract Act, 1872",
        section="Section 27",
        title="Agreement in restraint of trade void",
        text=(
            "Every agreement by which any one is restrained from exercising a "
            "lawful profession, trade or business of any kind, is to that "
            "extent void. Courts in India have generally held that post-"
            "employment non-compete clauses (restricting an employee from "
            "working elsewhere after leaving a job) fall under this restraint "
            "and are void/unenforceable, though reasonable restrictions during "
            "the term of employment, and confidentiality/non-solicitation "
            "clauses, are treated differently and may be enforceable."
        ),
    ),
    LegalSource(
        id="contract-act-s73",
        statute="Indian Contract Act, 1872",
        section="Section 73",
        title="Compensation for loss or damage caused by breach of contract",
        text=(
            "When a contract has been broken, the party who suffers by such "
            "breach is entitled to receive, from the party who has broken the "
            "contract, compensation for any loss or damage caused to him "
            "thereby which naturally arose in the usual course of things from "
            "such breach. This is the general basis for assessing whether a "
            "training-bond 'liquidated damages' clause reflects a genuine "
            "pre-estimate of loss versus an unenforceable penalty."
        ),
    ),
    LegalSource(
        id="contract-act-s74",
        statute="Indian Contract Act, 1872",
        section="Section 74",
        title="Compensation for breach where penalty is stipulated",
        text=(
            "When a contract has been broken, if a sum is named as the amount "
            "to be paid in case of breach, the party complaining of breach is "
            "entitled, whether or not actual damage is proved, to receive "
            "reasonable compensation not exceeding the amount so named. "
            "Courts have used this to strike down training-bond amounts that "
            "are disproportionate to the employer's actual training cost, "
            "treating them as penalties rather than genuine damages."
        ),
    ),
    LegalSource(
        id="karnataka-rent-act-deposit",
        statute="Karnataka Rent Act (Karnataka Rent Control framework, as "
        "commonly applied to residential tenancies)",
        section="Deposit / advance rent provisions",
        title="Security deposit norms",
        text=(
            "Karnataka does not impose one single statutory cap on residential "
            "security deposits in the way some other states do; however, "
            "local practice and tenancy guidance generally treats deposits "
            "in the range of 2-3 months' rent as customary for most "
            "Bengaluru residential lets, with deposits materially above that "
            "range (e.g. 10 months' rent) being unusual and worth flagging "
            "for the tenant's attention as a norm deviation, not a per-se "
            "illegal amount, since no MVP-verified statutory cap exists for "
            "this excerpt."
        ),
    ),
    LegalSource(
        id="karnataka-rent-act-notice",
        statute="Karnataka Rent Act (Karnataka Rent Control framework)",
        section="Termination / notice provisions",
        title="Notice period fairness",
        text=(
            "Tenancy agreements in Karnataka are expected to specify notice "
            "periods for termination by either party; a material asymmetry "
            "(e.g. tenant required to give 3 months notice while the "
            "landlord may terminate with 1 month or less) is a common "
            "one-sidedness red flag raised in tenant-rights guidance, even "
            "where not independently void, because it disproportionately "
            "burdens the tenant relative to the landlord."
        ),
    ),
    LegalSource(
        id="karnataka-rent-act-deductions",
        statute="Karnataka Rent Act (Karnataka Rent Control framework)",
        section="Deposit deduction provisions",
        title="Deductions from security deposit",
        text=(
            "Deductions from a security deposit are generally expected to "
            "correspond to actual damage beyond normal wear and tear. A "
            "clause that mandates a fixed painting/cleaning deduction "
            "regardless of the actual condition of the premises at handover "
            "is a commonly flagged unfair-deduction pattern in Bengaluru "
            "tenancy guidance."
        ),
    ),
    LegalSource(
        id="shops-establishments-act-notice",
        statute="Karnataka Shops and Commercial Establishments Act, 1961",
        section="Termination of employment / notice provisions",
        title="Notice and termination fairness for employees",
        text=(
            "The Karnataka Shops and Commercial Establishments Act sets out "
            "conditions of employment including notice for termination for "
            "certain categories of establishments/employees. Offer letters "
            "that impose materially longer notice/resignation periods on the "
            "employee than the employer's own termination notice are a "
            "commonly flagged asymmetry against the spirit of this Act's "
            "fair-notice framing, even where the offer letter is a private "
            "contract layered on top of statutory minimums."
        ),
    ),
]


_SOURCE_BY_ID = {s.id: s for s in CURATED_SOURCES}


def get_source(source_id: str) -> LegalSource | None:
    return _SOURCE_BY_ID.get(source_id)


def all_source_ids() -> set[str]:
    return set(_SOURCE_BY_ID.keys())


def build_context_block() -> str:
    """Format the full curated set into one citation-labeled context block
    for context-stuffing into a Gemini Pro-class prompt (per the plan's
    locked no-vector-store retrieval approach). Comfortably fits alongside a
    typical rental agreement/offer letter's clause text within Gemini's long
    context window (this is a few hundred words total)."""
    lines = ["CURATED LEGAL SOURCE SET (cite only using the [id] shown):"]
    for src in CURATED_SOURCES:
        lines.append(
            f"\n[{src.id}] {src.statute}, {src.section} — {src.title}\n{src.text}"
        )
    return "\n".join(lines)


CONTEXT_BLOCK = build_context_block()


# Simple keyword -> source-id map used to deterministically pick which
# curated sources are relevant to a given document's text, independent of
# whether the Gemini call behind it is live or mocked. This guarantees any
# citation the app surfaces always traces back to a real CURATED_SOURCES id
# (never a fabricated one), satisfying C10/C11/C13's "no fabricated
# citations" acceptance criteria structurally rather than by trusting
# free-form model text.
_KEYWORD_SOURCE_MAP: dict[str, list[str]] = {
    "non-compete": ["contract-act-s27"],
    "non compete": ["contract-act-s27"],
    "restraint of trade": ["contract-act-s27"],
    "training bond": ["contract-act-s73", "contract-act-s74"],
    "bond amount": ["contract-act-s73", "contract-act-s74"],
    "liquidated damages": ["contract-act-s74"],
    "security deposit": ["karnataka-rent-act-deposit"],
    "deposit": ["karnataka-rent-act-deposit"],
    "notice period": ["karnataka-rent-act-notice", "shops-establishments-act-notice"],
    "lock-in": ["karnataka-rent-act-notice"],
    "lock in": ["karnataka-rent-act-notice"],
    "painting": ["karnataka-rent-act-deductions"],
    "cleaning": ["karnataka-rent-act-deductions"],
    "deduction": ["karnataka-rent-act-deductions"],
    "resignation": ["shops-establishments-act-notice"],
    "termination": ["shops-establishments-act-notice"],
}


def find_relevant_sources_strict(text: str) -> list[LegalSource]:
    """Like find_relevant_sources but with NO fallback source — returns an
    empty list if nothing matches. Used by the Q&A engine (C13) so it can
    tell the difference between "grounded in a real source" and "nothing in
    the curated set supports this," which is what triggers the explicit
    'I don't know' response shape."""
    lowered = text.lower()
    matched_ids: set[str] = set()
    for keyword, ids in _KEYWORD_SOURCE_MAP.items():
        if keyword in lowered:
            matched_ids.update(ids)
    return [s for s in CURATED_SOURCES if s.id in matched_ids]


def find_relevant_sources(text: str) -> list[LegalSource]:
    """Return the curated sources whose keywords appear in `text`, in
    CURATED_SOURCES order, de-duplicated. Falls back to the general
    contract-formation source if nothing else matches, so callers always have
    at least one grounded citation to offer for contract-shaped documents."""
    lowered = text.lower()
    matched_ids: set[str] = set()
    for keyword, ids in _KEYWORD_SOURCE_MAP.items():
        if keyword in lowered:
            matched_ids.update(ids)
    if not matched_ids:
        matched_ids.add("contract-act-s10")
    return [s for s in CURATED_SOURCES if s.id in matched_ids]
