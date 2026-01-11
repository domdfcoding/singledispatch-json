# stdlib
from io import StringIO
from typing import Set

# 3rd party
import pytest
from coincidence.selectors import not_pypy

# this package
import sdjson


def test_dump() -> None:
	sio = StringIO()
	sdjson.dump({}, sio)
	assert sio.getvalue() == "{}"


def test_dumps() -> None:
	assert sdjson.dumps({}) == "{}"


@not_pypy(reason="Failing on PyPy3.6-7.1.1")
def test_dump_skipkeys() -> None:
	v = {b"invalid_key": False, "valid_key": True}
	with pytest.raises(TypeError):
		sdjson.dumps(v)

	s = sdjson.dumps(v, skipkeys=True)
	o = sdjson.loads(s)
	assert "valid_key" in o
	assert b"invalid_key" not in o


@pytest.mark.parametrize(
		"data, expects",
		[
				({True: False, False: True}, '{"false": true, "true": false}'),
				({2: 3.0, 4.0: 5, False: 1, 6: True}, '{"false": 1, "2": 3.0, "4.0": 5, "6": true}'),
				],
		)
def test_encode_truefalse(data: Set, expects: str):
	assert sdjson.dumps(data, sort_keys=True) == expects


# Issue 16228: Crash on encoding resized list
def test_encode_mutated():
	a = [object()] * 10

	def crasher(obj) -> None:
		del a[-1]

	assert sdjson.dumps(a, default=crasher) == "[null, null, null, null, null]"


# Issue 24094
def test_encode_evil_dict():

	class D(dict):

		def keys(self):
			return L

	class X:

		def __hash__(self) -> int:
			del L[0]
			return 1337

		def __lt__(self, o):
			return 0

	L = [X() for i in range(1122)]
	d = D()
	d[1337] = "true.dat"
	assert sdjson.dumps(d, sort_keys=True) == '{"1337": "true.dat"}'
