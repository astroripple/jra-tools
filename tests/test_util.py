"""utilのユニットテスト"""

from jra_tools.machine_learning import util


def test_create_payout(sample_kaisais):
    """KaisaiListから払戻金のndarrayが作成されていることを確認する

    Args:
        sample_kaisais (KaisaiList): 開催一覧
    """
    data = util.create_payout(sample_kaisais)
    assert len(data) == 24
