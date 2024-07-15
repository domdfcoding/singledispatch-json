"""
Test registering custom encoders in multiple files
"""

# stdlib
from decimal import Decimal
from fractions import Fraction

# 3rd party
import pytest

# this package
import sdjson


@pytest.mark.usefixtures("monkeypatch_sdjson")
def test_multiple_files() -> None:

	# this package
	from .glossia import talon, thorn  # noqa: F401

	# Test that we get the expected output when encoding a Decimal
	assert sdjson.dumps(Decimal(1)) == '"1"'

	# Test that we get the expected output when encoding a Fraction
	assert sdjson.dumps(Fraction(2, 3)) == '"2/3"'

	# Cleanup
	sdjson.encoders.unregister(Decimal, True)
	sdjson.encoders.unregister(Fraction, True)
