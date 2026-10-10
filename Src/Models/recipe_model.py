from typing import Optional
from Src.Core.abstract_model import base_model
from Src.Core.exceptions import argument_exception
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.recipe_row_model import recipe_row_model


class recipe_model(base_model):
    # Технологическая карта (рецепт приготовления блюда / полуфабриката)
    __dish: nomenclature_model
    __rows: list

    def __init__(
        self,
        name: str,
        dish: nomenclature_model,
        rows: Optional[list] = None,
    ) -> None:
        super().__init__()
        self.name = name
        self.dish = dish
        self.__rows = []
        if rows is not None:
            if not isinstance(rows, list):
                raise argument_exception(
                    "rows", "Список строк рецепта должен быть списком (list)."
                )
            for row in rows:
                self.add_row(row)

    @property
    def dish(self) -> nomenclature_model:
        # Готовое блюдо или полуфабрикат, к которому относится рецепт (1 блюдо - 1 техкарта)
        return self.__dish

    @dish.setter
    def dish(self, value: nomenclature_model) -> None:
        # Проверка принадлежности к типу nomenclature_model
        if not isinstance(value, nomenclature_model):
            raise argument_exception(
                "dish", "Блюдо должно быть объектом nomenclature_model."
            )
        self.__dish = value

    @property
    def rows(self) -> list:
        # Инкапсулированная копия списка строк рецепта
        return list(self.__rows)

    def add_row(self, row: recipe_row_model) -> None:
        # Добавление строки ингредиента в рецепт с валидацией типа
        if not isinstance(row, recipe_row_model):
            raise argument_exception(
                "row", "Строка рецепта должна быть объектом recipe_row_model."
            )
        self.__rows.append(row)

    def delete_row(self, row: recipe_row_model) -> None:
        # Исключение строки ингредиента из рецепта
        if not isinstance(row, recipe_row_model):
            raise argument_exception(
                "row", "Исключаемая строка должна быть объектом recipe_row_model."
            )
        if row not in self.__rows:
            raise argument_exception(
                "row", "Указанная строка ингредиента отсутствует в рецепте."
            )
        self.__rows.remove(row)

    @property
    def gross_weight(self) -> float:
        # Расчет суммарного веса брутто всех ингредиентов рецепта
        return sum(row.gross_weight for row in self.__rows)

    @property
    def net_weight(self) -> float:
        # Расчет суммарного веса нетто всех ингредиентов рецепта
        return sum(row.net_weight for row in self.__rows)

    @staticmethod
    def create(
        name: str,
        dish: nomenclature_model,
        rows: Optional[list] = None,
    ) -> "recipe_model":
        # Фабричный метод создания технологической карты
        return recipe_model(name, dish, rows)
