# stdlib
import codecs
from collections import OrderedDict

# 3rd party
import pytest

# this package
import sdjson

# test_encoding1 and test_encoding2 from 2.x are irrelevant (only str
# is supported as input, not bytes).


def test_encoding3() -> None:
	u = "αΩ"
	j = sdjson.dumps(u)
	assert j == '"\\u03b1\\u03a9"'


def test_encoding4() -> None:
	u = "αΩ"
	j = sdjson.dumps([u])
	assert j == '["\\u03b1\\u03a9"]'


def test_encoding5() -> None:
	u = "αΩ"
	j = sdjson.dumps(u, ensure_ascii=False)
	assert j == f'"{u}"'


def test_encoding6() -> None:
	u = "αΩ"
	j = sdjson.dumps([u], ensure_ascii=False)
	assert j == f'["{u}"]'


def test_big_unicode_encode() -> None:
	u = '𝄠'
	assert sdjson.dumps(u) == '"\\ud834\\udd20"'
	assert sdjson.dumps(u, ensure_ascii=False) == '"𝄠"'


def test_big_unicode_decode() -> None:
	u = "z𝄠x"
	assert sdjson.loads('"' + u + '"') == u
	assert sdjson.loads('"z\\ud834\\udd20x"') == u


def test_unicode_decode() -> None:
	for i in range(0, 0xd7ff):
		u = chr(i)
		s = f'"\\u{i:04x}"'
		assert sdjson.loads(s) == u


def test_unicode_preservation() -> None:
	assert type(sdjson.loads('""')) == str
	assert type(sdjson.loads('"a"')) == str
	assert type(sdjson.loads('["a"]')[0]) == str


def test_bytes_encode() -> None:
	with pytest.raises(TypeError):
		sdjson.dumps(b"hi")
	with pytest.raises(TypeError):
		sdjson.dumps([b"hi"])


def test_bytes_decode() -> None:
	for encoding, bom in [
		("utf-8", codecs.BOM_UTF8),
		("utf-16be", codecs.BOM_UTF16_BE),
		("utf-16le", codecs.BOM_UTF16_LE),
		("utf-32be", codecs.BOM_UTF32_BE),
		("utf-32le", codecs.BOM_UTF32_LE),
	]:
		data = ["aµ€𝄠"]
		encoded = sdjson.dumps(data).encode(encoding)
		assert sdjson.loads(bom + encoded) == data
		assert sdjson.loads(encoded) == data
	with pytest.raises(UnicodeDecodeError):
		sdjson.loads(b'["\x80"]')
	# RFC-7159 and ECMA-404 extend JSON to allow documents that
	# consist of only a string, which can present a special case
	# not covered by the encoding detection patterns specified in
	# RFC-4627 for utf-16-le (XX 00 XX 00).
	assert sdjson.loads('"☀"'.encode("utf-16-le")) == '☀'
	# Encoding detection for small (<4) bytes objects
	# is implemented as a special case. RFC-7159 and ECMA-404
	# allow single codepoint JSON documents which are only two
	# bytes in utf-16 encodings w/o BOM.
	assert sdjson.loads(b"5\x00") == 5
	assert sdjson.loads(b"\x007") == 7
	assert sdjson.loads(b"57") == 57


def test_object_pairs_hook_with_unicode() -> None:
	s = '{"xkd":1, "kcw":2, "art":3, "hxm":4, "qrt":5, "pad":6, "hoy":7}'
	p = [("xkd", 1), ("kcw", 2), ("art", 3), ("hxm", 4), ("qrt", 5), ("pad", 6), ("hoy", 7)]
	assert sdjson.loads(s, object_pairs_hook=lambda x: x) == p
	od = sdjson.loads(s, object_pairs_hook=OrderedDict)
	assert od == OrderedDict(p)
	assert type(od) == OrderedDict
	# the object_pairs_hook takes priority over the object_hook
	assert sdjson.loads(s, object_pairs_hook=OrderedDict, object_hook=lambda x: None) == OrderedDict(p)
