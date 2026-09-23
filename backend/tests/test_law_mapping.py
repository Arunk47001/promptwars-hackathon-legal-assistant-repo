from app.law_mapping import MAPPINGS, NewCode, OldCode, lookup_by_new_section, lookup_by_old_section


def test_at_least_ten_seeded_mappings():
    assert len(MAPPINGS) >= 10


def test_lookup_ipc_to_bns():
    results = lookup_by_old_section(OldCode.IPC, "302")
    assert results
    assert any(r.new_code == NewCode.BNS and r.new_section == "103" for r in results)


def test_lookup_bns_to_ipc_reverse_direction():
    results = lookup_by_new_section(NewCode.BNS, "103")
    assert results
    assert any(r.old_code == OldCode.IPC and r.old_section == "302" for r in results)


def test_crpc_to_bnss():
    results = lookup_by_old_section(OldCode.CRPC, "154")
    assert results
    assert results[0].new_code == NewCode.BNSS
    assert results[0].new_section == "173"


def test_unknown_section_returns_empty():
    assert lookup_by_old_section(OldCode.IPC, "99999") == []
