# stdlib
from abc import abstractmethod
from typing import TypeVar

# 3rd party
import pytest
from typing_extensions import Protocol, runtime_checkable

# this package
import sdjson

T_co = TypeVar("T_co", covariant=True)  # Any type covariant containers.


@runtime_checkable
class SupportsInt(Protocol):
	"""
	An ABC with one abstract method __int__.
	"""

	@abstractmethod
	def __int__(self) -> int:
		pass


@runtime_checkable
class SupportsFloat(Protocol):
	"""
	An ABC with one abstract method __float__.
	"""

	@abstractmethod
	def __float__(self) -> float:
		pass


@runtime_checkable
class SupportsBytes(Protocol):
	"""
	An ABC with one abstract method __bytes__.
	"""

	@abstractmethod
	def __bytes__(self) -> bytes:
		pass


class SupportsBizBaz(Protocol):

	@abstractmethod
	def bizbaz(self):
		pass


@pytest.mark.usefixtures("monkeypatch_sdjson")
def test_protocols() -> None:

	class Integer:

		def __int__(self) -> int:
			return 42

	class Float:

		def __float__(self) -> float:
			return 42.0

	class Bytes:

		def __bytes__(self) -> bytes:
			return b"42"

	with pytest.raises(TypeError, match="Object of type '?Integer'? is not JSON serializable"):
		sdjson.dumps(Integer())

	with pytest.raises(TypeError, match="Object of type '?Float'? is not JSON serializable"):
		sdjson.dumps(Float())

	with pytest.raises(TypeError, match="Object of type '?Bytes'? is not JSON serializable"):
		sdjson.dumps(Bytes())

	@sdjson.encoders.register(SupportsInt)
	def supports_int_encoder(obj):
		return int(obj)

	@sdjson.encoders.register(SupportsFloat)
	def supports_float_encoder(obj):
		return float(obj)

	@sdjson.encoders.register(SupportsBytes)
	def supports_bytes_encoder(obj):
		return bytes(obj)

	assert sdjson.dumps(Integer()) == "42"
	assert sdjson.dumps(Float()) == "42.0"

	# To prove the protocols don't take precedence
	assert sdjson.dumps(123) == "123"

	with pytest.raises(TypeError, match="Object of type '?bytes'? is not JSON serializable"):
		sdjson.dumps(Bytes())

	@sdjson.encoders.register(bytes)
	def bytes_encoder(obj):
		return obj.decode("UTF-8")

	assert sdjson.dumps(Bytes()) == '"42"'

	sdjson.unregister_encoder(SupportsInt)
	sdjson.unregister_encoder(SupportsFloat)
	sdjson.unregister_encoder(SupportsBytes)
	sdjson.unregister_encoder(bytes)

	with pytest.raises(KeyError):
		sdjson.unregister_encoder(bytes)

	with pytest.raises(TypeError, match="Protocols must be @runtime_checkable"):
		sdjson.register_encoder(SupportsBizBaz, supports_bytes_encoder)
