import pytest

from utils import __from_bytes_to_human


@pytest.mark.parametrize("b,human", [
    (1023, "1023"),
    (1025, "1 KB"),
    (1_000_000, "976.6 KB"),
    (1_000_000_000, "953.67 MB"),
    (10_000_000_000, "9.31 GB")
    ]
)
def test_from_bytes_to_human(b, human):
    out = __from_bytes_to_human(b)

    assert out == human

