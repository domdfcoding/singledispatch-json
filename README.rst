=======
sdjson
=======

.. start short_desc

**Custom JSON Encoder for Python utilising functools.singledispatch to support custom encoders for both Python's built-in classes and user-created classes, without as much legwork.**

.. end short_desc

.. start shields

.. list-table::
	:stub-columns: 1
	:widths: 10 90

	* - Docs
	  - |docs| |docs_check|
	* - Tests
	  - |travis| |actions_windows| |actions_macos| |coveralls| |codefactor| |pre_commit_ci|
	* - PyPI
	  - |pypi-version| |supported-versions| |supported-implementations| |wheel|
	* - Anaconda
	  - |conda-version| |conda-platform|
	* - Activity
	  - |commits-latest| |commits-since| |maintained|
	* - Other
	  - |license| |language| |requires| |pre_commit|

.. |docs| image:: https://img.shields.io/readthedocs/singledispatch-json/latest?logo=read-the-docs
	:target: https://singledispatch-json.readthedocs.io/en/latest/?badge=latest
	:alt: Documentation Build Status

.. |docs_check| image:: https://github.com/domdfcoding/singledispatch-json/workflows/Docs%20Check/badge.svg
	:target: https://github.com/domdfcoding/singledispatch-json/actions?query=workflow%3A%22Docs+Check%22
	:alt: Docs Check Status

.. |travis| image:: https://github.com/domdfcoding/singledispatch-json/workflows/Linux%20Tests/badge.svg
	:target: https://github.com/domdfcoding/singledispatch-json/actions?query=workflow%3A%22Linux+Tests%22
	:alt: Linux Test Status

.. |actions_windows| image:: https://github.com/domdfcoding/singledispatch-json/workflows/Windows%20Tests/badge.svg
	:target: https://github.com/domdfcoding/singledispatch-json/actions?query=workflow%3A%22Windows+Tests%22
	:alt: Windows Test Status

.. |actions_macos| image:: https://github.com/domdfcoding/singledispatch-json/workflows/macOS%20Tests/badge.svg
	:target: https://github.com/domdfcoding/singledispatch-json/actions?query=workflow%3A%22macOS+Tests%22
	:alt: macOS Test Status

.. |requires| image:: https://requires.io/github/domdfcoding/singledispatch-json/requirements.svg?branch=master
	:target: https://requires.io/github/domdfcoding/singledispatch-json/requirements/?branch=master
	:alt: Requirements Status

.. |coveralls| image:: https://img.shields.io/coveralls/github/domdfcoding/singledispatch-json/master?logo=coveralls
	:target: https://coveralls.io/github/domdfcoding/singledispatch-json?branch=master
	:alt: Coverage

.. |codefactor| image:: https://img.shields.io/codefactor/grade/github/domdfcoding/singledispatch-json?logo=codefactor
	:target: https://www.codefactor.io/repository/github/domdfcoding/singledispatch-json
	:alt: CodeFactor Grade

.. |pypi-version| image:: https://img.shields.io/pypi/v/sdjson
	:target: https://pypi.org/project/sdjson/
	:alt: PyPI - Package Version

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/sdjson?logo=python&logoColor=white
	:target: https://pypi.org/project/sdjson/
	:alt: PyPI - Supported Python Versions

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/sdjson
	:target: https://pypi.org/project/sdjson/
	:alt: PyPI - Supported Implementations

.. |wheel| image:: https://img.shields.io/pypi/wheel/sdjson
	:target: https://pypi.org/project/sdjson/
	:alt: PyPI - Wheel

.. |conda-version| image:: https://img.shields.io/conda/v/domdfcoding/sdjson?logo=anaconda
	:target: https://anaconda.org/domdfcoding/sdjson
	:alt: Conda - Package Version

.. |conda-platform| image:: https://img.shields.io/conda/pn/domdfcoding/sdjson?label=conda%7Cplatform
	:target: https://anaconda.org/domdfcoding/sdjson
	:alt: Conda - Platform

.. |license| image:: https://img.shields.io/github/license/domdfcoding/singledispatch-json
	:target: https://github.com/domdfcoding/singledispatch-json/blob/master/LICENSE
	:alt: License

.. |language| image:: https://img.shields.io/github/languages/top/domdfcoding/singledispatch-json
	:alt: GitHub top language

.. |commits-since| image:: https://img.shields.io/github/commits-since/domdfcoding/singledispatch-json/v0.3.0
	:target: https://github.com/domdfcoding/singledispatch-json/pulse
	:alt: GitHub commits since tagged version

.. |commits-latest| image:: https://img.shields.io/github/last-commit/domdfcoding/singledispatch-json
	:target: https://github.com/domdfcoding/singledispatch-json/commit/master
	:alt: GitHub last commit

.. |maintained| image:: https://img.shields.io/maintenance/yes/2020
	:alt: Maintenance

.. |pre_commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
	:target: https://github.com/pre-commit/pre-commit
	:alt: pre-commit

.. |pre_commit_ci| image:: https://results.pre-commit.ci/badge/github/domdfcoding/singledispatch-json/master.svg
	:target: https://results.pre-commit.ci/latest/github/domdfcoding/singledispatch-json/master
	:alt: pre-commit.ci status

.. end shields

|

Usage
#########
Creating and registering a custom encoder is as easy as:

>>> import sdjson
>>>
>>> @sdjson.dump.register(MyClass)
>>> def encode_myclass(obj):
...     return dict(obj)
>>>

In this case, ``MyClass`` can be made JSON-serializable simply by calling
``dict()`` on it. If your class requires more complicated logic
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

``sdjson`` also provides access to ``load``, ``loads``, ``JSONDecoder``,
``JSONDecodeError``, and ``JSONEncoder`` from the ``json`` module,
allowing you to use ``sdjson`` as a drop-in replacement
for ``json``.

If you wish to dump an object without using the custom encoders, you
can pass a different ``JSONEncoder`` subclass, or indeed ``JSONEncoder``
itself to get the stock functionality.

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


Note that this module cannot be used to create custom encoders for any object
``json`` already knows about; that is: ``dict``, ``list``, ``tuple``, ``str``,
``int``, ``float``, ``bool``, and ``None``.

TODO
######

1. Add support for custom decoders.
