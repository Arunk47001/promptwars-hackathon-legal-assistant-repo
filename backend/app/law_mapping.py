"""Old-to-new criminal law section-mapping utility (C14).

Standalone lookup mapping IPC/CrPC/Evidence Act sections to their BNS/BNSS/BSA
equivalents and back. This is a small, curated static table — per the task
breakdown, it does not need to be exhaustive for MVP, but seeds at least 10
commonly-referenced sections in both directions.

ACCURACY NOTE: mappings below reflect the widely-published IPC->BNS /
CrPC->BNSS / Evidence Act->BSA correspondence tables circulated after the
2023-24 code replacement. As with C9's legal source set, this is a
hackathon-curated table, not independently legal-reviewed — verify against
an authoritative source before any non-demo use.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class OldCode(str, Enum):
    IPC = "IPC"
    CRPC = "CrPC"
    EVIDENCE_ACT = "Evidence Act"


class NewCode(str, Enum):
    BNS = "BNS"
    BNSS = "BNSS"
    BSA = "BSA"


_OLD_TO_NEW_CODE = {
    OldCode.IPC: NewCode.BNS,
    OldCode.CRPC: NewCode.BNSS,
    OldCode.EVIDENCE_ACT: NewCode.BSA,
}
_NEW_TO_OLD_CODE = {v: k for k, v in _OLD_TO_NEW_CODE.items()}


@dataclass(frozen=True)
class Mapping:
    old_code: OldCode
    old_section: str
    new_code: NewCode
    new_section: str
    description: str


# Seeded common sections (>= 10), old -> new, both directions derived from this.
MAPPINGS: list[Mapping] = [
    Mapping(OldCode.IPC, "302", NewCode.BNS, "103", "Punishment for murder"),
    Mapping(OldCode.IPC, "376", NewCode.BNS, "64", "Punishment for rape"),
    Mapping(OldCode.IPC, "420", NewCode.BNS, "318", "Cheating and dishonestly inducing delivery of property"),
    Mapping(OldCode.IPC, "375", NewCode.BNS, "63", "Rape — definition"),
    Mapping(OldCode.IPC, "354", NewCode.BNS, "74", "Assault or criminal force to woman with intent to outrage her modesty"),
    Mapping(OldCode.IPC, "34", NewCode.BNS, "3(5)", "Acts done by several persons in furtherance of common intention"),
    Mapping(OldCode.IPC, "141", NewCode.BNS, "189", "Unlawful assembly"),
    Mapping(OldCode.IPC, "302", NewCode.BNS, "103(1)", "Murder — punishment (alt. sub-section reference)"),
    Mapping(OldCode.IPC, "406", NewCode.BNS, "316", "Punishment for criminal breach of trust"),
    Mapping(OldCode.IPC, "498A", NewCode.BNS, "85", "Husband or relative of husband subjecting woman to cruelty"),
    Mapping(OldCode.IPC, "506", NewCode.BNS, "351", "Punishment for criminal intimidation"),
    Mapping(OldCode.IPC, "509", NewCode.BNS, "79", "Word, gesture or act intended to insult the modesty of a woman"),
    Mapping(OldCode.CRPC, "154", NewCode.BNSS, "173", "Information in cognizable cases (FIR registration)"),
    Mapping(OldCode.CRPC, "161", NewCode.BNSS, "180", "Examination of witnesses by police"),
    Mapping(OldCode.CRPC, "41", NewCode.BNSS, "35", "When police may arrest without warrant"),
    Mapping(OldCode.CRPC, "125", NewCode.BNSS, "144", "Order for maintenance of wives, children and parents"),
    Mapping(OldCode.CRPC, "482", NewCode.BNSS, "528", "Saving of inherent powers of High Court"),
    Mapping(OldCode.EVIDENCE_ACT, "45", NewCode.BSA, "39", "Opinions of experts"),
    Mapping(OldCode.EVIDENCE_ACT, "65B", NewCode.BSA, "63", "Admissibility of electronic records"),
    Mapping(OldCode.EVIDENCE_ACT, "27", NewCode.BSA, "23", "How much of information received from accused may be proved"),
]


def lookup_by_old_section(code: OldCode, section: str) -> list[Mapping]:
    section = section.strip()
    return [
        m for m in MAPPINGS if m.old_code == code and m.old_section.lower() == section.lower()
    ]


def lookup_by_new_section(code: NewCode, section: str) -> list[Mapping]:
    section = section.strip()
    return [
        m for m in MAPPINGS if m.new_code == code and m.new_section.lower() == section.lower()
    ]


def lookup_any(section: str, code_hint: str | None = None) -> list[Mapping]:
    """Look up a section number in either direction, optionally scoped by a
    code hint (e.g. 'IPC', 'BNS')."""
    section = section.strip()
    results: list[Mapping] = []
    for m in MAPPINGS:
        if code_hint and code_hint.upper() not in (m.old_code.value.upper(), m.new_code.value.upper()):
            continue
        if m.old_section.lower() == section.lower() or m.new_section.lower() == section.lower():
            results.append(m)
    return results
