"""converterのユニットテスト"""

from unittest.mock import MagicMock
from jra_tools.machine_learning.usecase.converter import Converter


mock_load = MagicMock()
mock_period = MagicMock()


class MockQuery:
    load = mock_load
    period = mock_period


mock_save = MagicMock()


class MockFactory:
    def __init__(self, kaisais):
        self.kaisais = kaisais

    save = mock_save


def test_save_with_name(sample_kaisais):
    mock_query = MockQuery()
    mock_load.return_value = sample_kaisais

    converter = Converter(mock_query, [MockFactory])
    converter.save("test_file")

    mock_load.assert_called_once_with()
    mock_save.assert_called_once_with("test_file")


def test_save_without_name(sample_kaisais):
    mock_query = MockQuery()
    mock_load.return_value = sample_kaisais

    converter = Converter(mock_query, [MockFactory])
    converter.save()

    mock_load.assert_called_once_with()
    mock_save.assert_called_once_with(mock_period)
