# stdlib
import re
from decimal import Decimal

# 3rd party
import pytest
from coincidence import check_file_regression
from pytest_regressions.file_regression import FileRegressionFixture

# this package
import sdjson


@pytest.mark.usefixtures("monkeypatch_sdjson")
def test_overloading(file_regression: FileRegressionFixture) -> None:

	try:
		# Create and register a custom encoder
		@sdjson.encoders.register(Decimal)
		def encoder_1(obj):
			return "Result from first registration"

		# Test that we get the expected output from the first encoder
		assert sdjson.dumps(Decimal(1)) == '"Result from first registration"'

		# Create and register a new custom encoder that overloads the previous one
		@sdjson.encoders.register(Decimal)
		def encoder_2(obj):
			return "Result from second registration"

		# Test that we get the expected output from the second encoder
		assert sdjson.dumps(Decimal(2)) == '"Result from second registration"'

		print(sdjson.encoders.registry.items())
		check_file_regression(remove_memaddr(str(sdjson.encoders.registry.items())), file_regression)

	finally:
		# Cleanup
		sdjson.encoders.unregister(Decimal, True)


def remove_memaddr(string: str) -> str:
	return re.sub("at 0x(.*)>", "at 0x...>", string)
