from typing import Optional
from Src.Core.abstract_model import base_model
from Src.Core.exceptions import argument_exception
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model


class recipe_row_model(base_model):
    # Строка технологической карты (рецепта): расход сырья/материала, вес брутто и нетто
    __nomenclature: nomenclature_model
    __gross_weight: float = 0.0
    __net_weight: float = 0.0

    def __init__(
        self,
        nomenclature: nomenclature_model,
        gross_weight: float,
        net_weight: float,
    ) -> None:
        super().__init__()
        self.nomenclature = nomenclature
        self.name = nomenclature.name
        self.gross_weight = gross_weight
        self.net_weight = net_weight

    @property
    def nomenclature(self) -> nomenclature_model:
        # Расходуемая позиция номенклатуры (сырье, полуфабрикат, упаковка)
        return self.__nomenclature

    @nomenclature.setter
    def nomenclature(self, value: nomenclature_model) -> None:
        # Проверка принадлежности к типу nomenclature_model
        if not isinstance(value, nomenclature_model):
            raise argument_exception(
                "nomenclature", "Номенклатура должна быть объектом nomenclature_model."
            )
        self.__nomenclature = value

    @property
    def gross_weight(self) -> float:
        # Вес брутто (масса сырья до кулинарной обработки / с упаковкой)
        return self.__gross_weight

    @gross_weight.setter
    def gross_weight(self, value: float) -> None:
        # Вес брутто должен быть неотрицательным числом
        if not isinstance(value, (int, float)):
            raise argument_exception(
                "gross_weight", "Вес брутто должен быть числовым значением."
            )
        if value < 0:
            raise argument_exception(
                "gross_weight", "Вес брутто не может быть отрицательным."
            )
        self.__gross_weight = float(value)

    @property
    def net_weight(self) -> float:
        # Вес нетто (масса сырья после чистки / чистый выход ингредиента)
        return self.__net_weight

    @net_weight.setter
    def net_weight(self, value: float) -> None:
        # Вес нетто должен быть неотрицательным числом и не превышать брутто
        if not isinstance(value, (int, float)):
            raise argument_exception(
                "net_weight", "Вес нетто должен быть числовым значением."
            )
        if value < 0:
            raise argument_exception(
                "net_weight", "Вес нетто не может быть отрицательным."
            )
        if value > self.__gross_weight:
            raise argument_exception(
                "net_weight", "Вес нетто не может превышать вес брутто."
            )
        self.__net_weight = float(value)

    @property
    def range(self) -> range_model:
        # Единица измерения строки (делегируется из номенклатуры)
        return self.__nomenclature.range

    @staticmethod
    def create(
        nomenclature: nomenclature_model,
        gross_weight: float,
        net_weight: float,
    ) -> "recipe_row_model":
        # Фабричный метод создания строки рецепта
        return recipe_row_model(nomenclature, gross_weight, net_weight)
