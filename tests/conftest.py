# stdlib
from functools import singledispatch
from typing import Callable, Dict, Type

# 3rd party
import pytest

# this package
import sdjson
from sdjson import allow_unregister

pytest_plugins = ("coincidence", )


@pytest.fixture()
def monkeypatch_sdjson(monkeypatch):
	_registry = allow_unregister(singledispatch(lambda x: None))  # type: ignore[arg-type]
	_protocol_registry: Dict[Type, Callable] = {}
	registry = _registry.registry
	monkeypatch.setattr(sdjson.encoders, "_registry", _registry)
	monkeypatch.setattr(sdjson.encoders, "_protocol_registry", _protocol_registry)
	monkeypatch.setattr(sdjson.encoders, "registry", registry)
	assert sdjson.encoders._registry is _registry
	assert sdjson.encoders._protocol_registry is _protocol_registry
	assert sdjson.encoders.registry is registry
