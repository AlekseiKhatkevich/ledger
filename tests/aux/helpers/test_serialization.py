from typing import Any

import pytest

from aux.helpers.serialization import dict_keys_converter


@pytest.fixture
def test_dict() -> dict[str, Any]:
    return {
        'some-key': True,
        'anotherkey': True,
    }


def test_dict_keys_converter(test_dict):
    result_dict = dict_keys_converter(
        test_dict,
        keys=('some-key', 'nonexists',),
        from_symbol='-',
        to_symbol='_',
    )

    assert result_dict['some_key']
    assert result_dict['anotherkey']
