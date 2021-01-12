#!/usr/bin/env python
#
#  core.py
#
"""
The actual functionality.
"""
#
#  Copyright © 2020-2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#  Based on https://treyhunner.com/2013/09/singledispatch-json-serializer/
#  Copyright © 2013 Trey Hunner
#  He said "Feel free to use it however you like." So I have.
#
#  Also based on the `json` module (version 2.0.9) by Bob Ippolito from Python 3.7
#  Licensed under the Python Software Foundation License Version 2.
#  Copyright © 2001-2020 Python Software Foundation. All rights reserved.
#  Copyright © 2000 BeOpen.com . All rights reserved.
#  Copyright © 1995-2000 Corporation for National Research Initiatives . All rights reserved.
#  Copyright © 1991-1995 Stichting Mathematisch Centrum . All rights reserved.
#
#  Type annotations from Typeshed
#  https://github.com/python/typeshed
#  Apache 2.0 Licensed
#

# stdlib
import json
import sys
from functools import singledispatch
from typing import IO, Any, Callable, Iterator, Optional, Tuple, Type, TypeVar, Union

# 3rd party
from domdf_python_tools.doctools import append_docstring_from, is_documented_by, make_sphinx_links

if sys.version_info < (3, 8):  # pragma: no cover (>=py38)
	# 3rd party
	from typing_extensions import _ProtocolMeta  # type: ignore
else:  # pragma: no cover (<py38)
	# stdlib
	from typing import _ProtocolMeta  # type: ignore

__all__ = [
		"load",
		"loads",
		"JSONDecoder",
		"JSONDecodeError",
		"dump",
		"dumps",
		"JSONEncoder",
		"encoders",
		"register_encoder",
		"unregister_encoder",
		]

__author__ = "Dominic Davis-Foster"
__copyright__ = "2020 Dominic Davis-Foster"

__license__ = "LGPLv3+"
__version__ = "0.2.5"
__email__ = "dominic@davis-foster.co.uk"

# TODO: perhaps add a limit on number of decimal places for floats etc, like with pandas' jsons


def allow_unregister(func) -> Callable:
	"""
	Decorator to allow removal of custom encoders with ``<sdjson.encoders.unregister(<type>)``,
	where <type> is the custom type you wish to remove the encoder for.
	"""  # noqa: D400

	# From https://stackoverflow.com/a/25951784/3092681
	# Copyright © 2014 Martijn Pieters
	# https://stackoverflow.com/users/100297/martijn-pieters
	# Licensed under CC BY-SA 4.0

	# build a dictionary mapping names to closure cells
	closure = dict(zip(func.register.__code__.co_freevars, func.register.__closure__))
	registry = closure["registry"].cell_contents
	dispatch_cache = closure["dispatch_cache"].cell_contents

	def unregister(cls):
		del registry[cls]
		dispatch_cache.clear()

	func.unregister = unregister
	return func


def sphinxify_json_docstring() -> Callable:
	"""
	Turn references in the docstring to :class:`~json.JSONEncoder` into proper links.
	"""

	def wrapper(target):
		# To save having the `sphinxify_docstring` decorator too
		target.__doc__ = make_sphinx_links(target.__doc__)

		target.__doc__ = target.__doc__.replace("``JSONEncoder``", ":class:`~json.JSONEncoder`")
		target.__doc__ = target.__doc__.replace("``.default()``", ":meth:`~json.JSONEncoder.default`")

		return target

	return wrapper


class _Encoders:

	def __init__(self):
		self._registry = allow_unregister(singledispatch(lambda x: None))
		self._protocol_registry = {}
		self.registry = self._registry.registry

	def register(self, cls: Type, func: Optional[Callable] = None) -> Callable:
		"""
		Registers a new handler for the given type.

		Can be used as a decorator or a regular function:

		.. code-block:: python

			@register_encoder(bytes)
			def bytes_encoder(obj):
				return obj.decode("UTF-8")

			def int_encoder(obj):
				return int(obj)

			register_encoder(int, int_encoder)


		:param cls:
		:param func:
		"""

		if func is None:
			return lambda f: self.register(cls, f)

		if isinstance(cls, _ProtocolMeta):
			if getattr(cls, "_is_runtime_protocol", False):
				self._protocol_registry[cls] = func
			else:
				raise TypeError("Protocols must be @runtime_checkable")
			return func
		else:
			return self._registry.register(cls, func)

	def dispatch(self, cls: object) -> Optional[Callable]:
		"""
		Returns the best available implementation for the given object.

		:param cls:
		"""

		if object in self.registry:
			self.unregister(object)

		handler = self._registry.dispatch(type(cls))
		if handler is not None:
			return handler
		else:
			for protocol, handler in self._protocol_registry.items():
				if isinstance(cls, protocol):
					return handler

		return None

	def unregister(self, cls: Type):
		"""
		Unregister the handler for the given type.

		.. code-block:: python

			unregister_encoder(int)

		:param cls:

		:raise KeyError: if no handler is found.
		"""

		if cls in self.registry:
			self._registry.unregister(cls)
		elif cls in self._protocol_registry:
			del self._protocol_registry[cls]
		else:
			raise KeyError


encoders = _Encoders()
register_encoder = encoders.register  # type: ignore
unregister_encoder = encoders.unregister  # type: ignore


@sphinxify_json_docstring()
@append_docstring_from(json.dump)
def dump(obj: Any, fp: IO, **kwargs: Any):  # TODO
	"""
	Serialize custom Python classes to JSON.
	Custom classes can be registered using the ``@encoders.register(<type>)`` decorator.
	"""

	iterable = dumps(obj, **kwargs)

	for chunk in iterable:
		fp.write(chunk)


@sphinxify_json_docstring()
@append_docstring_from(json.dumps)
def dumps(
		obj: Any,
		*,
		skipkeys: bool = False,
		ensure_ascii: bool = True,
		check_circular: bool = True,
		allow_nan: bool = True,
		cls: Optional[Type[json.JSONEncoder]] = None,
		indent: Union[None, int, str] = None,
		separators: Optional[Tuple[str, str]] = None,
		default: Optional[Callable[[Any], Any]] = None,
		sort_keys: bool = False,
		**kwargs: Any,
		):
	"""
	Serialize custom Python classes to JSON.
	Custom classes can be registered using the ``@encoders.register(<type>)`` decorator.
	"""

	if (
			not skipkeys and ensure_ascii and check_circular and allow_nan and cls is None and indent is None
			and separators is None and default is None and not sort_keys and not kwargs
			):
		return _default_encoder.encode(obj)
	if cls is None:
		cls = _CustomEncoder
	return cls(
			skipkeys=skipkeys,
			ensure_ascii=ensure_ascii,
			check_circular=check_circular,
			allow_nan=allow_nan,
			indent=indent,
			separators=separators,
			default=default,
			sort_keys=sort_keys,
			**kwargs
			).encode(obj)


# Provide access to remaining objects from json module.
# We have to do it this way to sort out the docstrings for sphinx without
#  modifying the original docstrings.
@sphinxify_json_docstring()
@append_docstring_from(json.load)
def load(*args, **kwargs):
	"""
	This is just the :func:`~json.load` function from Python's :mod:`json` module.
	"""
	return json.load(*args, **kwargs)


@sphinxify_json_docstring()
@append_docstring_from(json.loads)
def loads(*args, **kwargs):
	"""
	This is just the :func:`~json.loads` function from Python's :mod:`json` module.
	"""
	return json.loads(*args, **kwargs)


@sphinxify_json_docstring()
@append_docstring_from(json.JSONEncoder)
class JSONEncoder(json.JSONEncoder):
	"""
	This is just the :class:`~json.JSONEncoder` class from Python's :mod:`json` module.
	"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	@sphinxify_json_docstring()
	@is_documented_by(json.JSONEncoder.default)
	def default(self, o: Any) -> Any:  # noqa: D102
		return super().default(o)

	@sphinxify_json_docstring()
	@is_documented_by(json.JSONEncoder.encode)
	def encode(self, o: Any) -> Any:  # noqa: D102
		return super().encode(o)

	@sphinxify_json_docstring()
	@is_documented_by(json.JSONEncoder.iterencode)
	def iterencode(self, o: Any, _one_shot: bool = False) -> Iterator[str]:  # noqa: D102
		return super().iterencode(o, _one_shot)


@sphinxify_json_docstring()
@append_docstring_from(json.JSONDecoder)
class JSONDecoder(json.JSONDecoder):
	"""
	This is just the :class:`~json.JSONEncoder` class from Python's :mod:`json` module.
	"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	@sphinxify_json_docstring()
	@is_documented_by(json.JSONDecoder.decode)
	def decode(self, *args, **kwargs):  # noqa: D102
		return super().decode(*args, **kwargs)

	@sphinxify_json_docstring()
	@is_documented_by(json.JSONDecoder.raw_decode)
	def raw_decode(self, *args, **kwargs):  # noqa: D102
		return super().raw_decode(*args, **kwargs)


JSONDecodeError = json.JSONDecodeError


# Custom encoder for sdjson
class _CustomEncoder(JSONEncoder):

	def default(self, obj):
		handler = encoders.dispatch(obj)
		if handler is not None:
			return handler(obj)

		return super().default(obj)


_default_encoder = _CustomEncoder(
		skipkeys=False,
		ensure_ascii=True,
		check_circular=True,
		allow_nan=True,
		indent=None,
		separators=None,
		default=None,
		)
