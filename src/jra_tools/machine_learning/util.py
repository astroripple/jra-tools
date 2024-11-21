"""ツールのユースケース"""

from jra_tools import InputCreator, PayoutCreator
from jra_tools.machine_learning.training_kaisai_query import TrainingKaisaiQuery
from jra_tools.machine_learning.quarter_kaisai_query import QuarterKaisaiQuery
from jra_tools.machine_learning.converter import Converter


def create_training_dataset(start: int, end: int):
    """指定した期間のデータセットを作成する

    Args:
        start (int): YYYY
        end (int): YYYY

    Raises:
        RuntimeError: データのロードまたは保存中にエラーが発生
    """

    converter = Converter(
        TrainingKaisaiQuery(start, end), [InputCreator, PayoutCreator]
    )
    converter.save()


def create_quarter_dataset(year: int, quarter: int) -> None:
    """指定した四半期のデータセットをファイルに保存する

    Args:
        year (int): YYYY
        quarter (int): 1 - 4
        only_input (bool, optional): 入力データのみを作成するか. Defaults to True.
    """
    converter = Converter(
        QuarterKaisaiQuery(year, quarter), [InputCreator, PayoutCreator]
    )
    converter.save()
