# stdlib
from enum import Enum, IntEnum
from math import isnan

# this package
import sdjson

SMALL = 1
BIG = 1 << 32
HUGE = 1 << 64
REALLY_HUGE = 1 << 96


class BigNum(IntEnum):
	small = SMALL
	big = BIG
	huge = HUGE
	really_huge = REALLY_HUGE


E = 2.718281
PI = 3.141593
TAU = 2 * PI


class FloatNum(float, Enum):
	e = E
	pi = PI
	tau = TAU


INF = float("inf")
NEG_INF = float("-inf")
NAN = float("nan")


class WierdNum(float, Enum):
	inf = INF
	neg_inf = NEG_INF
	nan = NAN


def test_floats() -> None:
	for enum in FloatNum:
		assert sdjson.dumps(enum) == repr(enum.value)
		assert float(sdjson.dumps(enum)) == enum
		assert sdjson.loads(sdjson.dumps(enum)) == enum


def test_weird_floats() -> None:
	for enum, expected in zip(WierdNum, ("Infinity", "-Infinity", "NaN")):
		assert sdjson.dumps(enum) == expected
		if not isnan(enum):
			assert float(sdjson.dumps(enum)) == enum
			assert sdjson.loads(sdjson.dumps(enum)) == enum
		else:
			assert isnan(float(sdjson.dumps(enum)))
			assert isnan(sdjson.loads(sdjson.dumps(enum)))


def test_ints() -> None:
	for enum in BigNum:
		assert sdjson.dumps(enum) == str(enum.value)
		assert int(sdjson.dumps(enum)) == enum
		assert sdjson.loads(sdjson.dumps(enum)) == enum


def test_list() -> None:
	assert sdjson.dumps(list(BigNum)) == str([SMALL, BIG, HUGE, REALLY_HUGE])
	assert sdjson.loads(sdjson.dumps(list(BigNum))) == list(BigNum)
	assert sdjson.dumps(list(FloatNum)) == str([E, PI, TAU])
	assert sdjson.loads(sdjson.dumps(list(FloatNum))) == list(FloatNum)
	assert sdjson.dumps(list(WierdNum)) == "[Infinity, -Infinity, NaN]"
	assert sdjson.loads(sdjson.dumps(list(WierdNum)))[:2] == list(WierdNum)[:2]
	assert isnan(sdjson.loads(sdjson.dumps(list(WierdNum)))[2])


def test_dict_keys() -> None:
	s: int
	b: int
	h: int
	r: int
	e: float
	p: float
	t: float
	i: float
	j: float
	n: float

	s, b, h, r = BigNum
	e, p, t = FloatNum
	i, j, n = WierdNum

	d = {
			s: "tiny",
			b: "large",
			h: "larger",
			r: "largest",
			e: "Euler's number",
			p: "pi",
			t: "tau",
			i: "Infinity",
			j: "-Infinity",
			n: "NaN",
			}

	nd = sdjson.loads(sdjson.dumps(d))

	assert nd[str(SMALL)] == "tiny"
	assert nd[str(BIG)] == "large"
	assert nd[str(HUGE)] == "larger"
	assert nd[str(REALLY_HUGE)] == "largest"
	assert nd[repr(E)] == "Euler's number"
	assert nd[repr(PI)] == "pi"
	assert nd[repr(TAU)] == "tau"
	assert nd["Infinity"] == "Infinity"
	assert nd["-Infinity"] == "-Infinity"
	assert nd["NaN"] == "NaN"


def test_dict_values() -> None:
	d = dict(
			tiny=BigNum.small,
			large=BigNum.big,
			larger=BigNum.huge,
			largest=BigNum.really_huge,
			e=FloatNum.e,
			pi=FloatNum.pi,
			tau=FloatNum.tau,
			i=WierdNum.inf,
			j=WierdNum.neg_inf,
			n=WierdNum.nan,
			)
	nd = sdjson.loads(sdjson.dumps(d))
	assert nd["tiny"] == SMALL
	assert nd["large"] == BIG
	assert nd["larger"] == HUGE
	assert nd["largest"] == REALLY_HUGE
	assert nd['e'] == E
	assert nd["pi"] == PI
	assert nd["tau"] == TAU
	assert nd['i'] == INF
	assert nd['j'] == NEG_INF
	assert isnan(nd['n'])
