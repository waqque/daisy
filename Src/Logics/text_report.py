from typing import Optional
from Src.Core.abstract_report import abstract_report
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_model import recipe_model


class text_report(abstract_report):
    # Текстовый отчет по сущностям (рецепт, номенклатура, единица измерения)
    __recipe: Optional[recipe_model] = None

    def __init__(self) -> None:
        # Регистрация обработчиков сущностей для текстового формата
        super().__init__()
        self.register(recipe_model, self._build_recipe)
        self.register(nomenclature_model, self._build_nomenclature)
        self.register(range_model, self._build_range)

    @property
    def recipe(self) -> Optional[recipe_model]:
        # Получение текущей технологической карты отчета
        return self.__recipe

    def _build_recipe(self, source: recipe_model) -> report_result_dto:
        # Построение текстового отчета по технологической карте
        self.__recipe = source
        header = "Код|Наименование|Брутто|Нетто"
        lines = [header]
        for item in self.__recipe.items:
            lines.append(f"{item.unique_code}|{item.name}|{item.brutto}|{item.netto}")
        result = report_result_dto()
        result.text = "\n".join(lines)
        return result

    def _build_nomenclature(self, source: nomenclature_model) -> report_result_dto:
        # Построение текстового отчета по номенклатуре
        header = "Код|Наименование|Полное наименование|Группа|Единица измерения"
        group = source.group.name if source.group else ""
        range_unit = source.range.name if source.range else ""
        line = f"{source.unique_code}|{source.name}|{source.full_name}|{group}|{range_unit}"
        result = report_result_dto()
        result.text = f"{header}\n{line}"
        return result

    def _build_range(self, source: range_model) -> report_result_dto:
        # Построение текстового отчета по единице измерения
        header = "Код|Наименование|Коэффициент|Базовая единица"
        base = source.base_range.name if source.base_range else ""
        line = f"{source.unique_code}|{source.name}|{source.conversion_factor}|{base}"
        result = report_result_dto()
        result.text = f"{header}\n{line}"
        return result
