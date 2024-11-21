"""ツールのユースケース"""

from jra_tools import InputCreator, PayoutCreator
from jra_tools.machine_learning.training_kaisai_query import TrainingKaisaiQuery
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
    _start, _end, period = _quarter_period(year, quarter)
    _create_dataset(_start, _end, period)


def _quarter_period(year: int, quarter: int):
    start_month = int(12 / 4 * (quarter - 1) + 1)
    end_month = start_month + 2
    return (
        int(f"{year}{start_month:02}01"),
        int(f"{year}{end_month:02}{30 if end_month in [2,4,6,9,11] else 31}"),
        f"{year}_{start_month:02}_{end_month:02}",
    )


def _create_dataset(query: IQuery, period: str):
    from jra_tools import InputCreator, PayoutCreator

    converter = Converter(query, [InputCreator, PayoutCreator])
    converter.save(period)
