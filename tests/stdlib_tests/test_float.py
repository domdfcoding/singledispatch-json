# stdlib
import math

# 3rd party
import pytest

# this package
import sdjson


def test_floats() -> None:
	for num in [1617161771.7650001, math.pi, math.pi**100, math.pi**-100, 3.1]:
		assert float(sdjson.dumps(num)) == num
		assert sdjson.loads(sdjson.dumps(num)) == num


def test_ints() -> None:
	for num in [1, 1 << 32, 1 << 64]:
		assert sdjson.dumps(num) == str(num)
		assert int(sdjson.dumps(num)) == num


def test_out_of_range() -> None:
	assert sdjson.loads("[23456789012E666]") == [float("inf")]
	assert sdjson.loads("[-23456789012E666]") == [float("-inf")]


def test_allow_nan() -> None:
	for val in (float("inf"), float("-inf"), float("nan")):
		out = sdjson.dumps([val])
		if val == val:  # inf
			assert sdjson.loads(out) == [val]
		else:  # nan
			res = sdjson.loads(out)
			assert len(res) == 1
			assert res[0] != res[0]
		with pytest.raises(ValueError, match="Out of range float values are not JSON compliant"):
			sdjson.dumps([val], allow_nan=False)
