from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from textual.containers import Container

from src.lib.interface import interface

# Configure pytest-asyncio
pytest_asyncio.MODE = "auto"
pytest.asyncio_fixture_loop_scope = "module"


@pytest.fixture
def container():
    return MagicMock(spec=Container)


class TestInterface:
    pytestmark = pytest.mark.asyncio(loop_scope="module")

    async def test_interface_with_static_true(self, container):
        @interface(name="test_interface", activate=True)
        async def test_func(container):
            return "success"

        assert test_func._NAME == "test_interface"
        assert test_func._IS_INTERFACE is True
        assert test_func._ACTIVATE() is True
        assert await test_func(container) == "success"

    async def test_interface_with_static_false(self, container):
        @interface(name="test_interface", activate=False)
        async def test_func(container):
            return "success"

        assert test_func._ACTIVATE() is False

    async def test_interface_with_callable_activation(self, container):
        activation_state = True

        def activate_func():
            return activation_state

        @interface(name="test_interface", activate=activate_func)
        async def test_func(container):
            return "success"

        assert test_func._ACTIVATE() is True
        activation_state = False
        assert test_func._ACTIVATE() is False

    async def test_interface_preserves_function_metadata(self, container):
        @interface(name="test_interface")
        async def test_func(container):
            """Test docstring"""
            return "success"

        assert test_func.__doc__ == "Test docstring"
        assert test_func.__name__ == "test_func"

    async def test_interface_with_default_activation(self, container):
        @interface(name="test_interface")
        async def test_func(container):
            return "success"

        assert test_func._ACTIVATE() is True
