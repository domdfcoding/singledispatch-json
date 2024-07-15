"""
Create several custom encoders and test that they work
"""

# stdlib
import collections
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from fractions import Fraction

# 3rd party
import pytest
import pytz  # type: ignore[import]

# this package
import sdjson


@pytest.mark.usefixtures("monkeypatch_sdjson")
def test_decimal_float() -> None:
	# Create and register a custom encoder for Decimal that turns it into a float
	@sdjson.encoders.register(Decimal)
	def encode_decimal_float(obj):
		return float(obj)

	assert sdjson.dumps(Decimal(str(12.3456))) == "12.3456"

	# Cleanup
	sdjson.encoders.unregister(Decimal)


@pytest.mark.usefixtures("monkeypatch_sdjson")
def test_decimal_str() -> None:
	# Create and register a custom encoder for Decimal that turns it into a str
	@sdjson.encoders.register(Decimal)
	def encode_decimal_str(obj):
		return str(obj)

	assert sdjson.dumps(Decimal(str(12.3456))) == '"12.3456"'

	# Cleanup
	sdjson.encoders.unregister(Decimal)


@pytest.mark.usefixtures("monkeypatch_sdjson")
def test_fraction_float() -> None:
	# Create and register a custom encoder for Fraction that turns it into a float
	@sdjson.encoders.register(Fraction)
	def encode_fraction_float(obj):
		return float(obj)

	assert sdjson.dumps(Fraction(13, 10)) == "1.3"
	assert sdjson.dumps(Fraction(3, 4)) == "0.75"
	assert sdjson.dumps(Fraction(9, 11)) == "0.8181818181818182"
	assert sdjson.dumps(Fraction(140, 144)) == "0.9722222222222222"
	assert sdjson.dumps(Fraction(2, 7)) == "0.2857142857142857"

	# Cleanup
	sdjson.encoders.unregister(Fraction)


@pytest.mark.usefixtures("monkeypatch_sdjson")
def test_fraction_str() -> None:
	# Create and register a custom encoder for Fraction that turns it into a str
	@sdjson.encoders.register(Fraction)
	def encode_fraction_str(obj):
		return str(obj)

	assert sdjson.dumps(Fraction(13, 10)) == '"13/10"'
	assert sdjson.dumps(Fraction(3, 4)) == '"3/4"'
	assert sdjson.dumps(Fraction(9, 11)) == '"9/11"'
	assert sdjson.dumps(Fraction(140, 144)) == '"35/36"'
	assert sdjson.dumps(Fraction(2, 7)) == '"2/7"'

	# Cleanup
	sdjson.encoders.unregister(Fraction)


@pytest.mark.usefixtures("monkeypatch_sdjson")
def test_datetime_float() -> None:
	# Create and register a custom encoder for datetime that turns it into a float
	@sdjson.encoders.register(datetime)
	def encode_datetime_float(obj):
		return obj.timestamp()

	assert sdjson.dumps(datetime(1945, 5, 8, 19, 20, tzinfo=pytz.UTC)) == "-777876000.0"

	# Cleanup
	sdjson.encoders.unregister(datetime)


@pytest.mark.usefixtures("monkeypatch_sdjson")
def test_datetime_str() -> None:
	# Create and register a custom encoder for datetime that turns it into a str
	@sdjson.encoders.register(datetime)
	def encode_datetime_str(obj):
		return f"{obj:%Y/%m/%d %H:%M}"

	assert sdjson.dumps(datetime(1945, 5, 8, 19, 20)) == '"1945/05/08 19:20"'

	# Cleanup
	sdjson.encoders.unregister(datetime)


@pytest.mark.usefixtures("monkeypatch_sdjson")
def test_datetime_tuple() -> None:
	# Create and register a custom encoder for datetime that turns it into a timetuple
	@sdjson.encoders.register(datetime)
	def encode_datetime_tuple(obj):
		return obj.timetuple()

	assert sdjson.dumps(datetime(1945, 5, 8, 19, 20)) == "[1945, 5, 8, 19, 20, 0, 1, 128, -1]"

	# Cleanup
	sdjson.encoders.unregister(datetime)


@pytest.mark.usefixtures("monkeypatch_sdjson")
def test_timedelta_float() -> None:
	# Create and register a custom encoder for timedelta that turns it into a float
	@sdjson.encoders.register(timedelta)
	def encode_timedelta_float(obj):
		return obj.total_seconds()

	start_date = datetime(1945, 5, 8, 19, 20).replace(tzinfo=pytz.utc)
	end_date = datetime(2020, 5, 8, 9, 0).replace(tzinfo=pytz.utc)
	delta = end_date - start_date
	assert sdjson.dumps(delta) == "2366804400.0"

	# Cleanup
	sdjson.encoders.unregister(timedelta)


# def test_date_float() -> None:
# 	# Create and register a custom encoder for date that turns it into a float
# 	@sdjson.encoders.register(date)
# 	def encode_date_float(obj):
# 		return obj.timestamp()
#
# 	assert sdjson.dumps(date(1945, 5, 8)) == "-777952800.0"
#
# 	# Cleanup
# 	sdjson.encoders.unregister(date)


@pytest.mark.usefixtures("monkeypatch_sdjson")
def test_date_str() -> None:
	# Create and register a custom encoder for date that turns it into a str
	@sdjson.encoders.register(date)
	def encode_date_str(obj):
		return f"{obj:%Y/%m/%d}"

	assert sdjson.dumps(date(1945, 5, 8)) == '"1945/05/08"'

	# Cleanup
	sdjson.encoders.unregister(date)


@pytest.mark.usefixtures("monkeypatch_sdjson")
def test_date_tuple() -> None:
	# Create and register a custom encoder for date that turns it into a timetuple
	@sdjson.encoders.register(date)
	def encode_date_tuple(obj):
		return obj.timetuple()

	assert sdjson.dumps(date(1945, 5, 8)) == "[1945, 5, 8, 0, 0, 0, 1, 128, -1]"

	# Cleanup
	sdjson.encoders.unregister(date)


@pytest.mark.usefixtures("monkeypatch_sdjson")
def test_time_float() -> None:
	# Create and register a custom encoder for time that turns it into a float
	@sdjson.encoders.register(time)
	def encode_date_float(obj):
		return int(timedelta(hours=obj.hour, minutes=obj.minute, seconds=obj.second).total_seconds())

	assert sdjson.dumps(time(9, 10, 11)) == "33011"

	# Cleanup
	sdjson.encoders.unregister(time)


# Create and register a custom encoder for date that turns it into a float


@pytest.mark.usefixtures("monkeypatch_sdjson")
def test_time_str() -> None:
	# Create and register a custom encoder for time that turns it into a str
	@sdjson.encoders.register(time)
	def encode_time_str(obj):
		return f"{obj:%H:%M:%S}"

	assert sdjson.dumps(time(9, 10, 11)) == '"09:10:11"'

	# Cleanup
	sdjson.encoders.unregister(time)


@pytest.mark.usefixtures("monkeypatch_sdjson")
def test_time_tuple() -> None:
	# Create and register a custom encoder for time that turns it into a timetuple
	@sdjson.encoders.register(time)
	def encode_time_tuple(obj):
		return obj.hour, obj.minute, obj.second

	assert sdjson.dumps(time(9, 10, 11)) == "[9, 10, 11]"

	# Cleanup
	sdjson.encoders.unregister(time)


@pytest.mark.xfail(reason="Not implemented in CPython yet.")
@pytest.mark.usefixtures("monkeypatch_sdjson")
def test_named_tuple() -> None:
	# Ref: https://bugs.python.org/issue30343
	#      https://github.com/python/cpython/pull/1558

	Student = collections.namedtuple("Student", "name, age, teacher")

	try:

		@sdjson.encoders.register(Student)
		def encode_student(obj):
			return {
					"name": obj.name,
					"age": obj.age,
					"teacher": obj.teacher,
					}

		assert sdjson.dumps(Student("Alice", 12, "Sue")) == '{"name": "Alice", "age": 12, "teacher": "Sue"}'

	finally:
		# Cleanup
		sdjson.encoders.unregister(Student, True)
