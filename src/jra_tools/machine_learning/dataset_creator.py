"""トレーニングデータセットをローカルに作成する"""

from typing import Callable, List
from jrdb_model import KaisaiData
from jra_tools.machine_learning.icreator import ICreator


def create_dataset_from(
    kaisais: List[KaisaiData],
    period: str,
    only_input: bool,
    input_factory: Callable[..., ICreator],
    payout_factory: Callable[..., ICreator],
):
    """開催一覧をndarrayに変換して、トレーニングデータセットを保存する

    Args:
        kaisais (List[KaisaiData]): 開催一覧
        period (str): 保存するファイル名(拡張子を除く)
        only_input (bool): 入力データのみを保存する
        input_factory (Callable[..., ICreator]): インプットデータを作成するクラス
        payout_factory (Callable[..., ICreator]): 払戻データを作成するクラス
    """
    ic = input_factory(kaisais)
    ic.save(period)
    if not only_input:
        pc = payout_factory(kaisais)
        pc.save(period)
