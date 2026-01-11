# stdlib
import textwrap

# 3rd party
import pytest

# this package
import sdjson


def test_separators() -> None:
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
      [
        "blorpie"
      ] ,
      [
        "whoops"
      ] ,
      [] ,
      "d-shtaeou" ,
      "d-nthiouh" ,
      "i-vhbjkhnth" ,
      {
        "nifty" : 87
      } ,
      {
        "field" : "yes" ,
        "morefield" : false
      }
    ]""",
			)

	d1 = sdjson.dumps(h)
	d2 = sdjson.dumps(h, indent=2, sort_keys=True, separators=(" ,", " : "))

	h1 = sdjson.loads(d1)
	h2 = sdjson.loads(d2)

	assert h1 == h
	assert h2 == h
	assert d2 == expect


def test_illegal_separators() -> None:
	h = {1: 2, 3: 4}
	with pytest.raises(TypeError):
		sdjson.dumps(h, separators=(b", ", ": "))  # type: ignore[arg-type]
	with pytest.raises(TypeError):
		sdjson.dumps(h, separators=(", ", b": "))  # type: ignore[arg-type]
	with pytest.raises(TypeError):
		sdjson.dumps(h, separators=(b", ", b": "))  # type: ignore[arg-type]
