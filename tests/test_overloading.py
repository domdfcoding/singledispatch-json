# stdlib
from decimal import Decimal

# this package
import sdjson


def test_overloading():
	
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
	
	# Cleanup
	sdjson.encoders.unregister(Decimal)