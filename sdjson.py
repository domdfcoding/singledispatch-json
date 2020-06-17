#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  sdjson.py
#  Scroll down for license info
"""
JSON encoder utilising functools.singledispatch to support custom encoders
for both Python's built-in classes and user-created classes, without as much legwork.


Creating and registering a custom encoder is as easy as:

>>> import sdjson
>>>
>>> @sdjson.encoders.register(MyClass)
>>> def encode_myclass(obj):
...     return dict(obj)
>>>

In this case, ``MyClass`` can be made JSON-serializable simply by calling
:class:`dict <python:dict>` on it. If your class requires more complicated logic
to make it JSON-serializable, do that here.

Then, to dump the object to a string:

>>> class_instance = MyClass()
>>> print(sdjson.dumps(class_instance))
'{"menu": ["egg and bacon", "egg sausage and bacon", "egg and spam", "egg bacon and spam"],
"today\'s special": "Lobster Thermidor au Crevette with a Mornay sauce served in a Provencale
manner with shallots and aubergines garnished with truffle pate, brandy and with a fried egg
on top and spam."}'
>>>

Or to dump to a file:

>>> with open("spam.json", "w") as fp:
...     sdjson.dumps(class_instance, fp)
...
>>>

``sdjson`` also provides access to :func:`load <python:json.load>`,
:func:`loads <python:json.loads>`, :class:`~python:json.JSONDecoder`,
:class:`~python:json.JSONDecodeError`, and :class:`~python:json.JSONEncoder`
from the :mod:`~python:json` module, allowing you to use ``sdjson`` as a drop-in replacement
for :mod:`~python:json`.

If you wish to dump an object without using the custom encoders, you can pass
a different :class:`~python:json.JSONEncoder` subclass, or indeed
:class:`~python:json.JSONEncoder` itself to get the stock functionality.

>>> sdjson.dumps(class_instance, cls=sdjson.JSONEncoder)
>>>

|

When you've finished, if you want to unregister the encoder you can call:

>>> sdjson.encoders.unregister(MyClass)
>>>

to remove the encoder for ``MyClass``. If you want to replace the encoder with a
different one it is not necessary to call this function: the
``@sdjson.encoders.register`` decorator will replace any existing decorator for
the given class.


TODO: This module does not currently support custom decoders, but might in the future.
"""
#
#  Copyright © 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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

# stdlib
import json
# TODO: perhaps add a limit on number of decimal places for floats etc, like with pandas' jsons
import sys
from functools import singledispatch
from typing import IO, Any, Callable, Dict, List, Optional, Tuple, Type, Union, overload

# 3rd party
from domdf_python_tools.doctools import append_docstring_from, is_documented_by, make_sphinx_links

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




def allow_unregister(func) -> Callable:
	"""
	Decorator to allow removal of custom encoders with ``<sdjson.encoders.unregister(<type>)``,
	where <type> is the custom type you wish to remove the encoder for.

	From https://stackoverflow.com/a/25951784/3092681
	Copyright © 2014 Martijn Pieters
	https://stackoverflow.com/users/100297/martijn-pieters
	Licensed under CC BY-SA 4.0
	"""

	# build a dictionary mapping names to closure cells
	closure = dict(zip(func.register.__code__.co_freevars, func.register.__closure__))
	registry = closure['registry'].cell_contents
	dispatch_cache = closure['dispatch_cache'].cell_contents

	def unregister(cls):
		del registry[cls]
		dispatch_cache.clear()

	func.unregister = unregister
	return func


def sphinxify_json_docstring():
	"""
	Turn references in the docstring to :class:`~python:json.JSONEncoder` into proper links.
	"""

	def wrapper(target):
		# To save having the `sphinxify_docstring` decorator too
		target.__doc__ = make_sphinx_links(target.__doc__)

		target.__doc__ = target.__doc__.replace("``JSONEncoder``", ":class:`~python:json.JSONEncoder`")
		target.__doc__ = target.__doc__.replace("``.default()``", ":meth:`~python:json.JSONEncoder.default`")

		return target

	return wrapper


@allow_unregister
@singledispatch
class _Encoders:
	register: Callable
	unregister: Callable


encoders = _Encoders
register_encoder = _Encoders.register  # type: ignore
unregister_encoder = _Encoders.unregister  # type: ignore

@overload
def dump(obj: Any,
		 fp: IO[str],
		 *,
		 skipkeys: bool = ...,
		 ensure_ascii: bool = ...,
		 check_circular: bool = ...,
		 allow_nan: bool = ...,
		 cls: Optional[Type[json.JSONEncoder]] = ...,
		 indent: Union[None, int, str] = ...,
		 separators: Optional[Tuple[str, str]] = ...,
		 default: Optional[Callable[[Any], Any]] = ...,
		 sort_keys: bool = ...,
		 **kwds: Any) -> None: ...

@sphinxify_json_docstring()
@append_docstring_from(json.dump)
def dump(obj, fp, **kwargs):
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
		obj,
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
		**kw,
		):
	"""
	Serialize custom Python classes to JSON.
	Custom classes can be registered using the ``@encoders.register(<type>)`` decorator.
	"""

	if (
			not skipkeys and ensure_ascii and check_circular and allow_nan and cls is None and indent is None
			and separators is None and default is None and not sort_keys and not kw
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
			**kw
			).encode(obj)


if sys.version_info >= (3, 6):
	_LoadsString = Union[str, bytes]
else:
	_LoadsString = str
@overload
def loads(s: _LoadsString,
		  *,
		  cls: Optional[Type[json.JSONDecoder]] = ...,
		  object_hook: Optional[Callable[[Dict[Any, Any]], Any]] = ...,
		  parse_float: Optional[Callable[[str], Any]] = ...,
		  parse_int: Optional[Callable[[str], Any]] = ...,
		  parse_constant: Optional[Callable[[str], Any]] = ...,
		  object_pairs_hook: Optional[Callable[[List[Tuple[Any, Any]]], Any]] = ...,
		  **kwds: Any) -> Any: ...

@overload
def load(fp,
		 *,
		 cls: Optional[Type[json.JSONDecoder]] = ...,
		 object_hook: Optional[Callable[[Dict[Any, Any]], Any]] = ...,
		 parse_float: Optional[Callable[[str], Any]] = ...,
		 parse_int: Optional[Callable[[str], Any]] = ...,
		 parse_constant: Optional[Callable[[str], Any]] = ...,
		 object_pairs_hook: Optional[Callable[[List[Tuple[Any, Any]]], Any]] = ...,
		 **kwds: Any) -> Any: ...
# Provide access to remaining objects from json module.
# We have to do it this way to sort out the docstrings for sphinx without
#  modifying the original docstrings.
@sphinxify_json_docstring()
@append_docstring_from(json.load)
def load(*args, **kwargs):
	"""
	This is just the :func:`load <python:json.load>` function from Python's :mod:`~python:json` module.
	"""
	return json.load(*args, **kwargs)


@sphinxify_json_docstring()
@append_docstring_from(json.loads)
def loads(*args, **kwargs):
	"""
	This is just the :func:`loads <python:json.loads>` function from Python's :mod:`~python:json` module.
	"""
	return json.loads(*args, **kwargs)


@sphinxify_json_docstring()
@append_docstring_from(json.JSONEncoder)
class JSONEncoder(json.JSONEncoder):
	"""
	This is just the :class:`~python:json.JSONEncoder` class from Python's :mod:`~python:json` module.
	"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	@sphinxify_json_docstring()
	@is_documented_by(json.JSONEncoder.default)
	def default(self, o):
		return super().default(o)

	@sphinxify_json_docstring()
	@is_documented_by(json.JSONEncoder.encode)
	def encode(self, o):
		return super().encode(o)

	@sphinxify_json_docstring()
	@is_documented_by(json.JSONEncoder.iterencode)
	def iterencode(self, o, _one_shot=False):
		return super().iterencode(o, _one_shot)


@sphinxify_json_docstring()
@append_docstring_from(json.JSONDecoder)
class JSONDecoder(json.JSONDecoder):
	"""
	This is just the :class:`~python:json.JSONEncoder` class from Python's :mod:`~python:json` module.
	"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	@sphinxify_json_docstring()
	@is_documented_by(json.JSONDecoder.decode)
	def decode(self, *args, **kwargs):
		return super().decode(*args, **kwargs)

	@sphinxify_json_docstring()
	@is_documented_by(json.JSONDecoder.raw_decode)
	def raw_decode(self, *args, **kwargs):
		return super().raw_decode(*args, **kwargs)


JSONDecodeError = json.JSONDecodeError


# Custom encoder for sdjson
class _CustomEncoder(JSONEncoder):

	def default(self, obj):
		for type_, handler in encoders.registry.items():
			if isinstance(obj, type_) and type_ is not object:
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
