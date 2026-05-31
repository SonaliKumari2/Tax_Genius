"""Unit tests for rule-based tax estimation (no API key required)."""

from app import estimate_income_tax


def test_zero_income():
    assert estimate_income_tax(0) == 0


def test_exempt_slab():
    assert estimate_income_tax(250_000) == 0


def test_five_percent_slab():
    assert estimate_income_tax(400_000) == 7_500


def test_ten_percent_slab():
    assert estimate_income_tax(600_000) == 22_500


def test_fifteen_percent_slab():
    assert estimate_income_tax(800_000) == 45_000


def test_top_slab():
    assert estimate_income_tax(2_000_000) == 337_500


def test_slab_boundaries():
    assert estimate_income_tax(500_000) == 12_500
    assert estimate_income_tax(750_000) == 37_500
    assert estimate_income_tax(1_500_000) == 187_500
