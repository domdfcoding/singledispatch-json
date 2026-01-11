# stdlib
import textwrap
from io import StringIO
from typing import Optional

# this package
import sdjson


def test_indent() -> None:
	h = [
			["blorpie"],
			["whoops"],
			[],
			"d-shtaeou",
			"d-nthiouh",
			"i-vhbjkhnth",
			{"nifty": 87},
			{"field": "yes", "morefield": False},
			]

	expect = textwrap.dedent(
			"""\
	[
	\t[
	\t\t"blorpie"
	\t],
	\t[
	\t\t"whoops"
	\t],
	\t[],
	\t"d-shtaeou",
	\t"d-nthiouh",
	\t"i-vhbjkhnth",
	\t{
	\t\t"nifty": 87
	\t},
	\t{
	\t\t"field": "yes",
	\t\t"morefield": false
	\t}
	]""",
			)

	d1 = sdjson.dumps(h)
	d2 = sdjson.dumps(h, indent=2, sort_keys=True, separators=(',', ": "))
	d3 = sdjson.dumps(h, indent='\t', sort_keys=True, separators=(',', ": "))
	d4 = sdjson.dumps(h, indent=2, sort_keys=True)
	d5 = sdjson.dumps(h, indent='\t', sort_keys=True)

	h1 = sdjson.loads(d1)
	h2 = sdjson.loads(d2)
	h3 = sdjson.loads(d3)

	assert h1 == h
	assert h2 == h
	assert h3 == h
	assert d2 == expect.expandtabs(2)
	assert d3 == expect
	assert d4 == d2
	assert d5 == d3


def test_indent0() -> None:
	h = {3: 1}

	def check(indent: Optional[int], expected: str) -> None:
		d1 = sdjson.dumps(h, indent=indent)
		assert d1 == expected

		sio = StringIO()
		sdjson.dump(h, sio, indent=indent)
		assert sio.getvalue() == expected

	# indent=0 should emit newlines
	check(0, '{\n"3": 1\n}')
	# indent=None is more compact
	check(None, '{"3": 1}')
