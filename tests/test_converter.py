"""converterのユニットテスト"""

from unittest.mock import MagicMock
from jra_tools.machine_learning.converter import Converter


mock_load = MagicMock()


class MockQuery:
    load = mock_load
    period = MagicMock()


mock_save = MagicMock()


class MockFactory:
    def __init__(self, kaisais):
        self.kaisais = kaisais

    save = mock_save


def test_converter(sample_kaisais):
    mock_query = MockQuery()
    mock_load.return_value = sample_kaisais

    converter = Converter(mock_query, [MockFactory])
    converter.save("test_file")

    mock_query.load.assert_called_once_with()
    mock_save.assert_called_once_with("test_file")
