#  !/usr/bin/env python
#
#  __init__.py
#
r"""
JSON encoder utilising functools.singledispatch to support custom encoders
for both Python's built-in classes and user-created classes, without as much legwork.


Creating and registering a custom encoder is as easy as:

.. code-block:: python

	>>> import sdjson
	>>>
	>>> @sdjson.register_encoder(MyClass)
	>>> def encode_myclass(obj):
	...     return dict(obj)
	>>>

In this case, ``MyClass`` can be made JSON-serializable simply by calling
:class:`dict` on it. If your class requires more complicated logic
to make it JSON-serializable, do that here.

Then, to dump the object to a string:

.. code-block:: python

	>>> class_instance = MyClass()
	>>> print(sdjson.dumps(class_instance))
	'{"menu": ["egg and bacon", "egg sausage and bacon", "egg and spam", "egg bacon and spam"],
	"today\'s special": "Lobster Thermidor au Crevette with a Mornay sauce served in a Provencale
	manner with shallots and aubergines garnished with truffle pate, brandy and with a fried egg
	on top and spam."}'
	>>>

Or to dump to a file:

.. code-block:: python

	>>> with open("spam.json", "w") as fp:
	...     sdjson.dumps(class_instance, fp)
	...
	>>>

``sdjson`` also provides access to :func:`~json.load`, :func:`~json.loads`, :class:`~json.JSONDecoder`,
:class:`~json.JSONDecodeError`, and :class:`~json.JSONEncoder` from the :mod:`json` module,
allowing you to use ``sdjson`` as a drop-in replacement for :mod:`json`.

If you wish to dump an object without using the custom encoders, you can pass a different
:class:`~json.JSONEncoder` subclass, or indeed :class:`~json.JSONEncoder`
itself to get the stock functionality.

.. code-block:: python

	>>> sdjson.dumps(class_instance, cls=sdjson.JSONEncoder)
	>>>

-----------

When you've finished, if you want to unregister the encoder you can run:

.. code-block:: python

	>>> sdjson.unregister_encoder(MyClass)
	>>>

to remove the encoder for ``MyClass``. If you want to replace the encoder with a
different one it is not necessary to call this function: the
:func:`@sdjson.register_encoder <sdjson.register_encoder>`
decorator will replace any existing decorator for the given class.


.. TODO:: This module does not currently support custom decoders, but might in the future.
"""  # noqa: D400
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
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
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
__version__ = "0.3.0"
__email__ = "dominic@davis-foster.co.uk"

# this package
from sdjson.core import (
		JSONDecodeError,
		JSONDecoder,
		JSONEncoder,
		dump,
		dumps,
		encoders,
		load,
		loads,
		register_encoder,
		unregister_encoder
		)

JSONEncoder.__module__ = "sdjson"
dump.__module__ = "sdjson"
dumps.__module__ = "sdjson"
load.__module__ = "sdjson"
loads.__module__ = "sdjson"
