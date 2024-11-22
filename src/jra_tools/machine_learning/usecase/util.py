"""ツールのユースケース"""

from functools import partial
from jra_tools import InputCreator, PayoutCreator
from jra_tools.machine_learning.training_kaisai_query import TrainingKaisaiQuery
from jra_tools.machine_learning.quarter_kaisai_query import QuarterKaisaiQuery
from jra_tools.machine_learning.converter import Converter


def _create_training(start: int, end: int, only_input: bool):
    """指定した期間のトレーニングデータを作成する

    Args:
        start (int): YYYY
        end (int): YYYY

    Raises:
        RuntimeError: データのロードまたは保存中にエラーが発生
    """

    converter = Converter(
        TrainingKaisaiQuery(start, end),
        [InputCreator] if only_input else [InputCreator, PayoutCreator],
    )
    converter.save()


create_training_dataset = partial(_create_training, only_input=False)
create_training_input = partial(_create_training, only_input=True)


def _create_quarter(year: int, quarter: int, only_input: bool) -> None:
    """指定した四半期のデータセットをファイルに保存する

    Args:
        year (int): YYYY
        quarter (int): 1 - 4
        only_input (bool, optional): 入力データのみを作成するか. Defaults to True.
    """
    converter = Converter(
        QuarterKaisaiQuery(year, quarter),
        [InputCreator] if only_input else [InputCreator, PayoutCreator],
    )
    converter.save()


create_quarter_dataset = partial(_create_quarter, only_input=False)
create_quarter_input = partial(_create_quarter, only_input=True)