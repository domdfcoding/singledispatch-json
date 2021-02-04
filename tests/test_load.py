"""
Test dumping and loading some objects
"""

# stdlib
from typing import Dict

# 3rd party
import pytest
from domdf_python_tools.paths import PathPlus

# this package
import sdjson


def write_then_read(obj, tmpdir: PathPlus):
	tmpfile = tmpdir / "output.json"

	with open(tmpfile, 'w') as fp:
		sdjson.dump(obj, fp)

	with open(tmpfile) as fp:
		return sdjson.load(fp)


def test_bools(tmp_pathplus: PathPlus) -> None:
	assert write_then_read(True, tmp_pathplus) is True
	assert str(write_then_read(True, tmp_pathplus)) == "True"  # Double check with string

	assert write_then_read(False, tmp_pathplus) is False
	assert str(write_then_read(False, tmp_pathplus)) == "False"  # Double check with string


def test_none(tmp_pathplus: PathPlus) -> None:
	assert write_then_read(None, tmp_pathplus) is None
	assert str(write_then_read(None, tmp_pathplus)) == "None"  # Double check with string


@pytest.mark.parametrize("value", [
		1,
		1234,
		12340000000,
		-1,
		-1234,
		-12340000000,
		])
def test_int(value: int, tmp_pathplus: PathPlus) -> None:
	assert write_then_read(value, tmp_pathplus) == value


@pytest.mark.parametrize(
		"value",
		[
				1.0,
				1234.0,
				12340000000.0,
				-1.0,
				-1234.0,
				-12340000000.0,
				1.005,
				1234.005,
				12340000000.005,
				-1.005,
				-1234.005,
				-12340000000.005,
				]
		)
def test_float(value: float, tmp_pathplus: PathPlus) -> None:
	assert write_then_read(value, tmp_pathplus) == value


example_dict = {"True": True, "False": False, "String": "spam", "Integer": 1, "Float": 2.5}


@pytest.mark.parametrize(
		"data, expected",
		[
				pytest.param((True, False, 1, 2.5, "spam"), [True, False, 1, 2.5, "spam"], id="tuple"),
				pytest.param([True, False, 1, 2.5, "spam"], [True, False, 1, 2.5, "spam"], id="list"),
				pytest.param(example_dict, example_dict, id="dict"),
				("egg and bacon", "egg and bacon"),
				("egg sausage and bacon", "egg sausage and bacon"),
				("egg and spam", "egg and spam"),
				("egg bacon and spam", "egg bacon and spam"),
				]
		)
def test_write_then_read(data, expected, tmp_pathplus: PathPlus):
	assert write_then_read(data, tmp_pathplus) == expected


@pytest.mark.xfail
@pytest.mark.parametrize("dictionary", [
		{True: False, False: True},
		{2: 3.0, 4.0: 5, False: 1, 6: True},
		])
def test_dict_failure(tmp_pathplus: PathPlus, dictionary: Dict) -> None:
	"""
	This test will fail because the boolean dictionary keys get read back in a lowercase strings
	"""

	assert write_then_read(dictionary, tmp_pathplus) == dictionary


@pytest.mark.xfail
def test_tuple_failure(tmp_pathplus: PathPlus) -> None:
	"""
	This test will fail because the tuple gets loaded back in as a list
	"""

	assert write_then_read((True, False, 1, 2.5, "spam"), tmp_pathplus) == (True, False, 1, 2.5, "spam")
