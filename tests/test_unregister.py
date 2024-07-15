# stdlib
from decimal import Decimal

# 3rd party
import pytest

# this package
import sdjson


@pytest.mark.usefixtures("monkeypatch_sdjson")
def test_unregister() -> None:
	# Create and register a custom encoder for Decimal that turns it into a string
	@sdjson.encoders.register(Decimal)
	def encode_str(obj):
		return str(obj)

	# Test that we get the expected output from the first encoder
	assert sdjson.dumps(Decimal(1)) == '"1"'

	# Unregister that encoder
	sdjson.unregister_encoder(Decimal)

	# We should now get an error
	with pytest.raises(TypeError, match="Object of type [']*Decimal[']* is not JSON serializable") as e:
		sdjson.dumps(Decimal(2))
	assert e.type is TypeError
