"""
Test custom encoder for a custom class
"""

# stdlib
from abc import ABC

# 3rd party
import pytest
from domdf_python_tools.paths import TemporaryPathPlus

# this package
import sdjson


class CustomClassBase(ABC):

	def __str__(self) -> str:
		return self.__repr__()

	def __iter__(self):
		yield from self.__dict__.items()

	def __getstate__(self):
		return self.__dict__

	def __setstate__(self, state):
		self.__init__(**state)  # type: ignore[misc]

	def __copy__(self):
		return self.__class__(**self.__dict__)

	def __deepcopy__(self, memodict={}):
		return self.__copy__()


class Character(CustomClassBase):

	def __init__(self, name, actor, armed=False):
		self.name = str(name)
		self.actor = str(actor)
		self.armed = bool(armed)

	def __repr__(self) -> str:
		return f"Character: {self.name} ({self.actor})"

	@property
	def __dict__(self):  # type: ignore[override]
		return dict(name=self.name, actor=self.actor, armed=self.armed)


class Cheese(CustomClassBase):

	def __init__(self, name, properties=None):
		self.name = name

		if properties:
			self.properties = properties
		else:
			self.properties = []

	def __repr__(self) -> str:
		return f"Cheese({self.name})"

	@property
	def __dict__(self):  # type: ignore[override]
		return dict(
				name=self.name,
				properties=self.properties,
				)


class Shop(CustomClassBase):
	"""
	Custom class to encode to JSON
	"""

	def __init__(
			self,
			name,
			address,
			is_open=True,
			staff=None,
			customers=None,
			current_stock=None,
			music=False,
			dancing=False,
			):

		self.name = str(name)
		self.address = str(address)
		self.is_open = bool(is_open)
		self.music = bool(music)
		self.dancing = bool(dancing)

		if staff:
			self.staff = staff
		else:
			self.staff = []

		if customers:
			self.customers = customers
		else:
			self.customers = []

		if current_stock:
			self.current_stock = current_stock
		else:
			self.current_stock = []

	def __repr__(self) -> str:
		return f"{self.name} ({'Open' if self.is_open else 'closed'})"

	@property
	def __dict__(self):  # type: ignore[override]
		return dict(
				name=self.name,
				address=self.address,
				is_open=self.is_open,
				music=self.music,
				dancing=self.dancing,
				staff=self.staff,
				customers=self.customers,
				current_stock=self.current_stock,
				)


@pytest.mark.usefixtures("monkeypatch_sdjson")
def test_custom_class() -> None:
	# Create and register the custom encoders
	# In this example we create three separate encoders even though all three classes
	#  actually share a common subclass. In real usage they might not be.
	@sdjson.encoders.register(Character)
	def encode_character(obj):
		return dict(obj)

	@sdjson.encoders.register(Cheese)
	def encode_cheese(obj):
		return dict(obj)

	@sdjson.encoders.register(Shop)
	def encode_shop(obj):
		return dict(obj)

	# Create instances of classes
	runny_camembert = Cheese("Camembert", ["Very runny"])
	shopkeeper = Character("Mr Wensleydale", "Michael Palin")
	customer = Character("The Customer", "John Cleese")
	cheese_shop = Shop(
			"The National Cheese Emporium",
			address="""12 Some Street
Some Town
England""",
			staff=[shopkeeper],
			customers=[customer],
			current_stock=[runny_camembert],
			music=False,
			dancing=False,
			)

	expected_json = (
			'{"name": "The National Cheese Emporium", "address": "12 Some Street\\n'
			'Some Town\\nEngland", "is_open": true, "music": false, "dancing": false, '
			'"staff": [{"name": "Mr Wensleydale", "actor": "Michael Palin", "armed": false}], '
			'"customers": [{"name": "The Customer", "actor": "John Cleese", "armed": false}], '
			'"current_stock": [{"name": "Camembert", "properties": ["Very runny"]}]}'
			)

	with TemporaryPathPlus() as tmpdir:
		tmpfile = tmpdir / "output.json"

		with open(tmpfile, 'w', encoding="UTF-8") as fp:
			sdjson.dump(cheese_shop, fp)

		with open(tmpfile, encoding="UTF-8") as fp:
			assert fp.read() == expected_json

	assert sdjson.dumps(cheese_shop) == expected_json

	# Cleanup
	sdjson.unregister_encoder(Character)
	sdjson.unregister_encoder(Cheese)
	sdjson.unregister_encoder(Shop)
