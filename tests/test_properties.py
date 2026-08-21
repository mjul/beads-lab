from hypothesis import given
from hypothesis import strategies as st

from beads_lab import reverse_string


@given(st.text())
def test_reverse_string_is_involutive(s: str) -> None:
    assert reverse_string(reverse_string(s)) == s


@given(st.text())
def test_reverse_string_preserves_length(s: str) -> None:
    assert len(reverse_string(s)) == len(s)
