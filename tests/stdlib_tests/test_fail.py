# stdlib
import platform
import re
import sys

# 3rd party
import pytest

# this package
import sdjson

# 2007-10-05
JSONDOCS = [
		# http://json.org/JSON_checker/test/fail1.json
		'"A JSON payload should be an object or array, not a string."',
		# http://json.org/JSON_checker/test/fail2.json
		'["Unclosed array"',  # http://json.org/JSON_checker/test/fail3.json
		'{unquoted_key: "keys must be quoted"}',  # http://json.org/JSON_checker/test/fail4.json
		'["extra comma",]',  # http://json.org/JSON_checker/test/fail5.json
		'["double extra comma",,]',  # http://json.org/JSON_checker/test/fail6.json
		'[   , "<-- missing value"]',  # http://json.org/JSON_checker/test/fail7.json
		'["Comma after the close"],',  # http://json.org/JSON_checker/test/fail8.json
		'["Extra close"]]',  # http://json.org/JSON_checker/test/fail9.json
		'{"Extra comma": true,}',  # http://json.org/JSON_checker/test/fail10.json
		'{"Extra value after close": true} "misplaced quoted value"',
		# http://json.org/JSON_checker/test/fail11.json
		'{"Illegal expression": 1 + 2}',  # http://json.org/JSON_checker/test/fail12.json
		'{"Illegal invocation": alert()}',  # http://json.org/JSON_checker/test/fail13.json
		'{"Numbers cannot have leading zeroes": 013}',  # http://json.org/JSON_checker/test/fail14.json
		'{"Numbers cannot be hex": 0x14}',  # http://json.org/JSON_checker/test/fail15.json
		'["Illegal backslash escape: \\x15"]',  # http://json.org/JSON_checker/test/fail16.json
		"[\\naked]",  # http://json.org/JSON_checker/test/fail17.json
		'["Illegal backslash escape: \\017"]',  # http://json.org/JSON_checker/test/fail18.json
		'[[[[[[[[[[[[[[[[[[[["Too deep"]]]]]]]]]]]]]]]]]]]]',  # http://json.org/JSON_checker/test/fail19.json
		'{"Missing colon" null}',  # http://json.org/JSON_checker/test/fail20.json
		'{"Double colon":: null}',  # http://json.org/JSON_checker/test/fail21.json
		'{"Comma instead of colon", null}',  # http://json.org/JSON_checker/test/fail22.json
		'["Colon instead of comma": false]',  # http://json.org/JSON_checker/test/fail23.json
		'["Bad value", truth]',  # http://json.org/JSON_checker/test/fail24.json
		"['single quote']",  # http://json.org/JSON_checker/test/fail25.json
		'["\ttab\tcharacter\tin\tstring\t"]',  # http://json.org/JSON_checker/test/fail26.json
		'["tab\\   character\\   in\\  string\\  "]',  # http://json.org/JSON_checker/test/fail27.json
		'["line\nbreak"]',  # http://json.org/JSON_checker/test/fail28.json
		'["line\\\nbreak"]',  # http://json.org/JSON_checker/test/fail29.json
		"[0e]",  # http://json.org/JSON_checker/test/fail30.json
		"[0e+]",  # http://json.org/JSON_checker/test/fail31.json
		"[0e+-1]",  # http://json.org/JSON_checker/test/fail32.json
		'{"Comma instead if closing brace": true,',  # http://json.org/JSON_checker/test/fail33.json
		'["mismatch"}',  # http://code.google.com/p/simplejson/issues/detail?id=3
		'["A\x1fZ control characters in string"]',
		]

SKIPS = {
		1: "why not have a string payload?",
		18: "spec doesn't specify any nesting limitations",
		}


def test_failures() -> None:
	for idx, doc in enumerate(JSONDOCS):
		idx = idx + 1
		if idx in SKIPS:
			sdjson.loads(doc)
			continue
		try:
			sdjson.loads(doc)
		except sdjson.JSONDecodeError:
			pass
		else:
			pytest.fail(f"Expected failure for fail{idx}.json: {doc!r}")


def test_non_string_keys_dict() -> None:
	data = {'a': 1, (1, 2): 2}

	# TODO:
	if platform.python_implementation() == "PyPy":
		match_string = r"key \(1, 2\) is not a string"
	elif sys.version_info[:2] > (3, 6):
		match_string = "keys must be str, int, float, bool or None, not tuple"
	else:
		match_string = "keys must be a string"

	with pytest.raises(TypeError, match=match_string):
		sdjson.dumps(data)


def test_not_serializable() -> None:
	with pytest.raises(TypeError, match="Object of type [']*module[']* is not JSON serializable"):
		sdjson.dumps(sys)


pypy = platform.python_implementation() == "PyPy"

if pypy:
	unexpected_right_brace = "Unexpected '}'"
	missing_colon = "No ':' found at"
	unexpected_colon = "Unexpected ':' when decoding array"
	property_name_string = "Key name must be string at char"
	empty_string = "Unexpected '\u0000'"
	unterminated_array = "Unterminated array starting at"

else:
	unexpected_right_brace = "Expecting value"
	missing_colon = "Expecting ':' delimiter"
	unexpected_colon = "Expecting ',' delimiter"
	property_name_string = "Expecting property name enclosed in double quotes"
	empty_string = "Expecting value"
	unterminated_array = "Expecting ',' delimiter"


def __test_invalid_input(data, msg, idx):
	with pytest.raises(sdjson.JSONDecodeError) as err:
		sdjson.loads(data)
	if pypy:
		assert err.value.msg.startswith(msg)  # Fix for varying messages between PyPy versions
	else:
		assert err.value.msg == msg
	assert err.value.pos == idx
	assert err.value.lineno == 1
	assert err.value.colno == idx + 1
	if pypy:
		assert re.match(rf"{msg}.*: line 1 column {idx + 1:d} \(char {idx:d}\)", str(err.value))
	else:
		assert re.match(rf"{msg}: line 1 column {idx + 1:d} \(char {idx:d}\)", str(err.value))


@pytest.mark.parametrize(
		"data, msg, idx",
		[
				('', empty_string, 0),
				('[', empty_string, 1),
				("[42", unterminated_array, 1 if pypy else 3),
				("[42,", empty_string, 4),
				('["', "Unterminated string starting at", 1),
				('["spam', "Unterminated string starting at", 1),
				('["spam"', unterminated_array, 1 if pypy else 7),
				('["spam",', empty_string, 8),
				('{', property_name_string, 1),
				('{"', "Unterminated string starting at", 1),
				('{"spam', "Unterminated string starting at", 1),
				('{"spam"', missing_colon, 7),
				('{"spam":', empty_string, 8),
				(
						'{"spam":42',
						"Unterminated object starting at" if pypy else "Expecting ',' delimiter",
						1 if pypy else 10
						),
				('{"spam":42,', property_name_string, 11),
				('"', "Unterminated string starting at", 0),
				('"spam', "Unterminated string starting at", 0),
				]
		)
def test_truncated_input(data, msg, idx):
	__test_invalid_input(data, msg, idx)


@pytest.mark.parametrize(
		"data, msg, idx",
		[
				("[,", "Unexpected ','" if pypy else "Expecting value", 1),
				('{"spam":[}', unexpected_right_brace, 9),
				("[42:", unexpected_colon, 3),
				('[42 "spam"', "Unexpected '\"' when decoding array" if pypy else "Expecting ',' delimiter", 4),
				("[42,]", "Unexpected ']'" if pypy else "Expecting value", 4),
				('{"spam":[42}', "Unexpected '}' when decoding array" if pypy else "Expecting ',' delimiter", 11),
				('["]', "Unterminated string starting at", 1),
				('["spam":', unexpected_colon, 7),
				('["spam",]', "Unexpected ']'" if pypy else "Expecting value", 8),
				("{:", property_name_string, 1),
				("{,", property_name_string, 1),
				("{42", property_name_string, 1),
				("[{]", property_name_string, 2),
				('{"spam",', missing_colon, 7),
				('{"spam"}', missing_colon, 7),
				('[{"spam"]', missing_colon, 8),
				('{"spam":}', unexpected_right_brace, 8),
				('[{"spam":]', "Unexpected ']'" if pypy else "Expecting value", 9),
				(
						'{"spam":42 "ham"',
						"Unexpected '\"' when decoding object" if pypy else "Expecting ',' delimiter",
						11
						),
				('[{"spam":42]', "Unexpected ']' when decoding object" if pypy else "Expecting ',' delimiter", 11),
				('{"spam":42,}', property_name_string, 11),
				]
		)
def test_unexpected_data(data, msg, idx):
	__test_invalid_input(data, msg, idx)


@pytest.mark.parametrize(
		"data, msg, idx",
		[
				("[]]", "Extra data", 2),
				("{}}", "Extra data", 2),
				("[],[]", "Extra data", 2),
				("{},{}", "Extra data", 2),
				('42,"spam"', "Extra data", 2),
				('"spam",42', "Extra data", 6),
				]
		)
def test_extra_data(data, msg, idx):
	__test_invalid_input(data, msg, idx)


@pytest.mark.parametrize(
		"data, line, col, idx", [
				('!', 1, 1, 0),
				(" !", 1, 2, 1),
				("\n!", 2, 1, 1),
				("\n  \n\n     !", 4, 6, 10),
				]
		)
def test_linecol(data, line, col, idx):

	with pytest.raises(sdjson.JSONDecodeError) as err:
		sdjson.loads(data)

	if platform.python_implementation() == "PyPy":
		match = "Unexpected '!'"
	else:
		match = "Expecting value"

	if pypy:
		assert err.value.msg.startswith(match)  # Fix for varying messages between PyPy versions
	else:
		assert err.value.msg == match
	assert err.value.pos == idx
	assert err.value.lineno == line
	assert err.value.colno == col
	if pypy:
		assert re.match(rf"{match}.*: line {line} column {col:d} \(char {idx:d}\)", str(err.value))
	else:
		assert re.match(rf"{match}: line {line} column {col:d} \(char {idx:d}\)", str(err.value))
