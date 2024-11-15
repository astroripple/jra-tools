"""InputCreatorのユニットテスト"""

from jra_tools.machine_learning.icreator import ICreator
from jra_tools import InputCreator


def test_save(sample_kaisais):
    """saveメソッドのユニットテスト

    Args:
        sample_kaisais (_type_): kaisaisフィクスチャ
    """
    ic = InputCreator(sample_kaisais)
    assert isinstance(ic, ICreator)
