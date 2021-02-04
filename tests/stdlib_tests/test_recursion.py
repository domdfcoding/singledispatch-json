# stdlib
from typing import Dict, List

# 3rd party
import pytest
from coincidence import not_pypy

# this package
import sdjson


class JSONTestObject:
	pass


def test_listrecursion() -> None:
	x: List[List] = []
	x.append(x)

	try:
		sdjson.dumps(x)
	except ValueError:
		pass
	else:
		pytest.fail("didn't raise ValueError on list recursion")

	x = []
	y = [x]
	x.append(y)

	try:
		sdjson.dumps(x)
	except ValueError:
		pass
	else:
		pytest.fail("didn't raise ValueError on alternating list recursion")

	y = []
	x = [y, y]
	# ensure that the marker is cleared
	sdjson.dumps(x)


def test_dictrecursion() -> None:
	x: Dict[str, Dict] = {}
	x["test"] = x

	try:
		sdjson.dumps(x)
	except ValueError:
		pass
	else:
		pytest.fail("didn't raise ValueError on dict recursion")

	x = {}
	y = {'a': x, 'b': x}
	# ensure that the marker is cleared
	sdjson.dumps(x)


def test_defaultrecursion() -> None:

	class RecursiveJSONEncoder(sdjson.JSONEncoder):
		recurse = False

		def default(self, o):
			if o is JSONTestObject:
				if self.recurse:
					return [JSONTestObject]
				else:
					return "JSONTestObject"
			return sdjson.JSONEncoder.default(self, o)

	enc = RecursiveJSONEncoder()
	assert enc.encode(JSONTestObject) == '"JSONTestObject"'
	enc.recurse = True
	try:
		enc.encode(JSONTestObject)
	except ValueError:
		pass
	else:
		pytest.fail("didn't raise ValueError on default recursion")


def test_highly_nested_objects_decoding() -> None:
	# test that loading highly-nested objects doesn't segfault when C
	# accelerations are used. See #12017
	with pytest.raises(RecursionError):
		sdjson.loads('{"a":' * 100000 + '1' + '}' * 100000)
	with pytest.raises(RecursionError):
		sdjson.loads('{"a":' * 100000 + "[1]" + '}' * 100000)
	with pytest.raises(RecursionError):
		sdjson.loads('[' * 100000 + '1' + ']' * 100000)


@not_pypy("Breaks coverage tracing on PyPy")
def test_highly_nested_objects_encoding() -> None:
	# See #12051
	l: List[List]
	d: Dict[str, Dict]
	l, d = [], {}

	for x in range(100000):
		l, d = [l], {'k': d}

	with pytest.raises(RecursionError):
		sdjson.dumps(l)
	with pytest.raises(RecursionError):
		sdjson.dumps(d)


@not_pypy("Breaks coverage tracing on PyPy")
def test_endless_recursion() -> None:
	# See #12051
	class EndlessJSONEncoder(sdjson.JSONEncoder):

		def default(self, o):
			"""
			If check_circular is False, this will keep adding another list.
			"""
			return [o]

	with pytest.raises(RecursionError):
		EndlessJSONEncoder(check_circular=False).encode(5j)
