from typing import Optional
from Src.Core.abstract_report import abstract_report
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_model import recipe_model


class markdown_report(abstract_report):
    # Отчет в формате Markdown с поддержкой бинарных данных
    __recipe: Optional[recipe_model] = None

    def __init__(self) -> None:
        # Регистрация обработчиков сущностей для формата Markdown
        super().__init__()
        self.register(recipe_model, self._build_recipe)
        self.register(nomenclature_model, self._build_nomenclature)
        self.register(range_model, self._build_range)

    @property
    def recipe(self) -> Optional[recipe_model]:
        # Получение текущей технологической карты отчета
        return self.__recipe

    def _build_recipe(self, source: recipe_model) -> report_result_dto:
        # Построение Markdown-отчета по технологической карте
        self.__recipe = source
        lines = [
            f"# {source.name}\n",
            "| Код | Наименование | Брутто | Нетто |",
            "| --- | --- | --- | --- |",
        ]
        for item in self.__recipe.items:
            lines.append(f"| {item.unique_code} | {item.name} | {item.brutto} | {item.netto} |")
        text_content = "\n".join(lines)
        return report_result_dto(text=text_content, data=text_content.encode("utf-8"))

    def _build_nomenclature(self, source: nomenclature_model) -> report_result_dto:
        # Построение Markdown-отчета по номенклатуре
        group = source.group.name if source.group else ""
        range_unit = source.range.name if source.range else ""
        lines = [
            f"# {source.name}\n",
            "| Код | Наименование | Полное наименование | Группа | Единица измерения |",
            "| --- | --- | --- | --- | --- |",
            f"| {source.unique_code} | {source.name} | {source.full_name} | {group} | {range_unit} |",
        ]
        text_content = "\n".join(lines)
        return report_result_dto(text=text_content, data=text_content.encode("utf-8"))

    def _build_range(self, source: range_model) -> report_result_dto:
        # Построение Markdown-отчета по единице измерения
        base = source.base_range.name if source.base_range else ""
        lines = [
            f"# {source.name}\n",
            "| Код | Наименование | Коэффициент | Базовая единица |",
            "| --- | --- | --- | --- |",
            f"| {source.unique_code} | {source.name} | {source.conversion_factor} | {base} |",
        ]
        text_content = "\n".join(lines)
        return report_result_dto(text=text_content, data=text_content.encode("utf-8"))
