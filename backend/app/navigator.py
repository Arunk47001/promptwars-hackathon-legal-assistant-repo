"""Navigator playbooks (C15).

At least 2-3 fully worked MVP playbooks, each returning forum/authority,
required documents, a generated draft, a rough timeline, and a rough cost —
per the spec's "what do I do now" navigator framing. Templated/deterministic
generation (Python string templates filled with user-supplied facts) rather
than a free-form Gemini call, so the draft output is reliable and
reproducible for a demo; the curated source block (C9) backs the legal
framing used in each draft.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass
class PlaybookResult:
    id: str
    title: str
    forum: str
    required_documents: list[str]
    draft: str
    timeline: str
    cost: str


@dataclass
class PlaybookSpec:
    id: str
    title: str
    description: str
    builder: Callable[[dict], PlaybookResult]


def _deposit_not_returned(facts: dict) -> PlaybookResult:
    tenant_name = facts.get("tenant_name", "[Tenant Name]")
    landlord_name = facts.get("landlord_name", "[Landlord Name]")
    address = facts.get("property_address", "[Property Address]")
    deposit_amount = facts.get("deposit_amount", "[Deposit Amount]")
    vacate_date = facts.get("vacate_date", "[Date premises were vacated]")

    draft = f"""LEGAL NOTICE

To: {landlord_name}
From: {tenant_name}
Re: Non-refund of security deposit — {address}

I vacated the above premises on {vacate_date} and have not received my
security deposit of Rs. {deposit_amount}, which was due to be refunded
within a reasonable time after handover, subject only to deductions for
damage beyond normal wear and tear (Indian Contract Act principles on
restitution/unjust retention apply here).

I hereby demand that you refund the full security deposit of
Rs. {deposit_amount} within 15 days of receipt of this notice, failing
which I will be constrained to pursue legal remedies, including approaching
the Rent Court / Small Causes Court / consumer forum as advised, and shall
hold you liable for costs and interest thereon.

Please treat this as a formal legal notice.

[Tenant signature]
[Date]
"""
    return PlaybookResult(
        id="deposit_not_returned",
        title="Security deposit not returned",
        forum=(
            "Rent Court (under the applicable Karnataka rent control "
            "framework) or the Small Causes Court for the deposit amount; "
            "a consumer complaint is also sometimes viable if the landlord "
            "qualifies as a service provider under the Consumer Protection "
            "Act — confirm with a lawyer/DLSA which forum fits your amount."
        ),
        required_documents=[
            "Signed rental agreement",
            "Proof of deposit payment (receipt/bank transfer record)",
            "Proof of vacating the premises (handover email, photos, keys receipt)",
            "This legal notice (sent by registered post/courier, keep proof of dispatch)",
            "Any correspondence with the landlord about the deposit",
        ],
        draft=draft,
        timeline=(
            "Send notice -> wait 15 days for response -> if unresolved, file "
            "in the appropriate forum. Small-claims-style matters often "
            "resolve in a few months; contested cases can take longer."
        ),
        cost=(
            "Sending a legal notice: roughly Rs. 500-2000 if drafted with a "
            "lawyer's help (this tool's draft is free to use as a starting "
            "point). Court filing fees for small claims are typically low "
            "(a few hundred to a few thousand rupees depending on the "
            "amount and forum)."
        ),
    )


def _builder_delay(facts: dict) -> PlaybookResult:
    buyer_name = facts.get("buyer_name", "[Buyer Name]")
    builder_name = facts.get("builder_name", "[Builder/Promoter Name]")
    project_name = facts.get("project_name", "[Project Name]")
    promised_date = facts.get("promised_date", "[Promised Possession Date]")
    rera_reg_no = facts.get("rera_registration_number", "[RERA Registration No.]")

    draft = f"""COMPLAINT — RERA KARNATAKA (K-RERA)

To: The Real Estate Regulatory Authority, Karnataka (K-RERA)
From: {buyer_name}
Re: Delay in possession — {project_name} (RERA Reg. No. {rera_reg_no}),
Promoter: {builder_name}

I booked a unit in the above project, with a promised possession date of
{promised_date}, which has now passed without possession being handed over
and without any registered extension of the project's RERA timeline that I
am aware of.

I request K-RERA to direct the promoter ({builder_name}) to:
1. Hand over possession at the earliest with a firm, committed date; and
2. Pay interest/compensation for the delay period as provided under the
   Real Estate (Regulation and Development) Act, 2016 and the Karnataka
   RERA rules.

I am enclosing the relevant booking/agreement documents in support of this
complaint.

[Buyer signature]
[Date]
"""
    return PlaybookResult(
        id="builder_delay",
        title="Builder possession delay (RERA)",
        forum="K-RERA (Karnataka Real Estate Regulatory Authority), via the RERA Karnataka online complaint portal.",
        required_documents=[
            "Booking/allotment letter and sale agreement",
            "Payment receipts for all installments paid",
            "Any correspondence with the builder about possession timelines",
            "RERA project registration number (from the K-RERA website)",
            "This complaint draft",
        ],
        timeline=(
            "K-RERA complaints are typically expected to be disposed of "
            "within about 60 days of filing per the RERA Act's own framing, "
            "though real-world timelines vary; hearings may take multiple "
            "sittings."
        ),
        cost=(
            "RERA complaint filing fees are relatively low (typically a few "
            "thousand rupees or less depending on relief sought) compared to "
            "civil suits; legal representation is optional but recommended "
            "for contested claims."
        ),
    )


PLAYBOOKS: dict[str, PlaybookSpec] = {
    "deposit_not_returned": PlaybookSpec(
        id="deposit_not_returned",
        title="Security deposit not returned",
        description=(
            "Landlord has not refunded your rental security deposit after "
            "you vacated the premises."
        ),
        builder=_deposit_not_returned,
    ),
    "builder_delay": PlaybookSpec(
        id="builder_delay",
        title="Builder possession delay (RERA)",
        description=(
            "A builder/promoter has delayed handing over possession of a "
            "booked flat/property past the promised date."
        ),
        builder=_builder_delay,
    ),
}


def list_playbooks() -> list[PlaybookSpec]:
    return list(PLAYBOOKS.values())


def run_playbook(playbook_id: str, facts: dict) -> PlaybookResult | None:
    spec = PLAYBOOKS.get(playbook_id)
    if not spec:
        return None
    return spec.builder(facts)
