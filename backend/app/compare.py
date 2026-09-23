"""Compare/diff engine (C12).

Given two documents' extracted text, pulls out a small set of key fields
(deposit amount, notice periods, lock-in terms) via regex extraction and
surfaces differences, highlighting fields that map to C11's red-flag
categories. Deliberately simple/deterministic (field extraction + diff)
rather than an LLM clause-alignment step, so results are reproducible and
testable without a live key.
"""
from __future__ import annotations

import re

from app.models import ClauseDiff

_DEPOSIT_RE = re.compile(
    r"(?:security\s+deposit[^.\n]{0,40}?|deposit\s+of\s+)(\d+)\s*(?:months?|month's)",
    re.IGNORECASE,
)
_TENANT_NOTICE_RE = re.compile(
    r"tenant[^.\n]{0,60}?(\d+)\s*months?\s*notice", re.IGNORECASE
)
_LANDLORD_NOTICE_RE = re.compile(
    r"landlord[^.\n]{0,60}?(\d+)\s*months?\s*notice", re.IGNORECASE
)
_LOCK_IN_RE = re.compile(r"lock[- ]?in[^.\n]{0,60}?(\d+)\s*months?", re.IGNORECASE)
_EMPLOYEE_NOTICE_RE = re.compile(
    r"employee[^.\n]{0,60}?(\d+)\s*(?:days?|months?)\s*notice", re.IGNORECASE
)


def _extract_fields(text: str) -> dict[str, str | None]:
    fields: dict[str, str | None] = {
        "security_deposit_months": None,
        "tenant_notice_months": None,
        "landlord_notice_months": None,
        "lock_in_months": None,
        "employee_notice": None,
    }
    if m := _DEPOSIT_RE.search(text):
        fields["security_deposit_months"] = m.group(1)
    if m := _TENANT_NOTICE_RE.search(text):
        fields["tenant_notice_months"] = m.group(1)
    if m := _LANDLORD_NOTICE_RE.search(text):
        fields["landlord_notice_months"] = m.group(1)
    if m := _LOCK_IN_RE.search(text):
        fields["lock_in_months"] = m.group(1)
    if m := _EMPLOYEE_NOTICE_RE.search(text):
        fields["employee_notice"] = m.group(0)
    return fields


_FIELD_TO_RED_FLAG_CATEGORY = {
    "security_deposit_months": "deposit_size",
    "tenant_notice_months": "lock_in_asymmetry",
    "landlord_notice_months": "lock_in_asymmetry",
    "lock_in_months": "lock_in_asymmetry",
    "employee_notice": "lock_in_asymmetry",
}


def compare_documents(text_a: str, text_b: str) -> list[ClauseDiff]:
    fields_a = _extract_fields(text_a)
    fields_b = _extract_fields(text_b)

    diffs: list[ClauseDiff] = []
    for field_name in fields_a:
        value_a = fields_a[field_name]
        value_b = fields_b[field_name]
        diffs.append(
            ClauseDiff(
                field=field_name,
                value_a=value_a,
                value_b=value_b,
                differs=value_a != value_b,
                red_flag_category=_FIELD_TO_RED_FLAG_CATEGORY.get(field_name),
            )
        )
    return diffs
