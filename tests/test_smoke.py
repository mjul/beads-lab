from beads_lab import reverse_string


def test_reverse_string_smoke() -> None:
    assert reverse_string("abc") == "cba"
