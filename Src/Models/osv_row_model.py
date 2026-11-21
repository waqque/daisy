from typing import Any, Dict
from Src.Core.abstract_model import base_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.storage_model import storage_model


class osv_row_model(base_model):
    # Итоговая строка оборотно-сальдовой ведомости по номенклатуре на складе
    __storage: storage_model
    __nomenclature: nomenclature_model
    __range: range_model
    __opening_balance: float = 0.0
    __income: float = 0.0
    __outcome: float = 0.0
    __closing_balance: float = 0.0

    def __init__(
        self,
        storage: storage_model,
        nomenclature: nomenclature_model,
        range_unit: range_model,
        opening_balance: float = 0.0,
        income: float = 0.0,
        outcome: float = 0.0,
        closing_balance: float = 0.0,
    ) -> None:
        super().__init__()
        self.__storage = storage
        self.__nomenclature = nomenclature
        self.__range = range_unit
        self.__opening_balance = round(float(opening_balance), 4)
        self.__income = round(float(income), 4)
        self.__outcome = round(float(outcome), 4)
        self.__closing_balance = round(float(closing_balance), 4)
        self.name = f"{nomenclature.name} ({storage.name})"

    @property
    def storage(self) -> storage_model:
        # Склад
        return self.__storage

    @property
    def nomenclature(self) -> nomenclature_model:
        # Номенклатура
        return self.__nomenclature

    @property
    def range(self) -> range_model:
        # Единица измерения
        return self.__range

    @property
    def opening_balance(self) -> float:
        # Начальный остаток на дату старта периода
        return self.__opening_balance

    @property
    def income(self) -> float:
        # Суммарный приход за период
        return self.__income

    @property
    def outcome(self) -> float:
        # Суммарный расход за период
        return self.__outcome

    @property
    def closing_balance(self) -> float:
        # Конечный остаток (начальный + приход - расход)
        return self.__closing_balance

    def to_dict(self) -> Dict[str, Any]:
        # Переводим строку в словарь через общую фабрику конверторов
        from Src.Logics.convert_factory import convert_factory
        return convert_factory().convert(self)
