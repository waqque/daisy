import datetime
from typing import Optional, Union
from Src.Core.abstract_model import base_model
from Src.Core.exceptions import argument_exception
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.storage_model import storage_model


class transaction_model(base_model):
    # Складская транзакция: положительное значение - приход, отрицательное - расход
    __storage: storage_model
    __nomenclature: nomenclature_model
    __range: range_model
    __value: float = 0.0
    __period: datetime.datetime

    def __init__(
        self,
        storage: storage_model,
        nomenclature: nomenclature_model,
        range_unit: range_model,
        value: float,
        period: Optional[Union[datetime.datetime, str]] = None,
    ) -> None:
        super().__init__()
        self.storage = storage
        self.nomenclature = nomenclature
        self.range = range_unit
        self.value = value
        self.period = period if period is not None else datetime.datetime.now()
        self.name = f"Транзакция {self.__nomenclature.name} ({self.__value})"

    @property
    def storage(self) -> storage_model:
        # Склад, по которому прошла операция
        return self.__storage

    @storage.setter
    def storage(self, value: storage_model) -> None:
        if not isinstance(value, storage_model):
            raise argument_exception("storage", "Склад должен быть объектом storage_model.")
        self.__storage = value

    @property
    def nomenclature(self) -> nomenclature_model:
        # Номенклатура, по которой зафиксировано движение
        return self.__nomenclature

    @nomenclature.setter
    def nomenclature(self, value: nomenclature_model) -> None:
        if not isinstance(value, nomenclature_model):
            raise argument_exception(
                "nomenclature", "Номенклатура должна быть объектом nomenclature_model."
            )
        self.__nomenclature = value

    @property
    def range(self) -> range_model:
        # Единица измерения операции
        return self.__range

    @range.setter
    def range(self, value: range_model) -> None:
        if not isinstance(value, range_model):
            raise argument_exception("range", "Единица измерения должна быть объектом range_model.")
        self.__range = value

    @property
    def value(self) -> float:
        # Количество товара (не может быть нулем)
        return self.__value

    @value.setter
    def value(self, source: float) -> None:
        if not isinstance(source, (int, float)):
            raise argument_exception("value", "Количество должно быть числом.")
        if source == 0:
            raise argument_exception("value", "Значение количества не может быть равно 0!")
        self.__value = float(source)

    @property
    def period(self) -> datetime.datetime:
        # Дата и время операции
        return self.__period

    @period.setter
    def period(self, value: Union[datetime.datetime, str]) -> None:
        if isinstance(value, str):
            try:
                parsed = datetime.datetime.fromisoformat(value)
            except Exception:
                raise argument_exception("period", "Некорректный формат даты периода.")
            self.__period = parsed
        elif isinstance(value, datetime.datetime):
            self.__period = value
        else:
            raise argument_exception("period", "Период должен быть объектом datetime.datetime.")

    @staticmethod
    def create(
        storage: storage_model,
        nomenclature: nomenclature_model,
        range_unit: range_model,
        value: float,
        period: Optional[Union[datetime.datetime, str]] = None,
    ) -> "transaction_model":
        # Фабричный метод создания транзакции
        return transaction_model(storage, nomenclature, range_unit, value, period)
