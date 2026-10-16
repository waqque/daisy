from typing import Optional
from Src.Core.abstract_report import abstract_report
from Src.Core.exceptions import argument_exception
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_model import recipe_model


class markdown_report(abstract_report):
    # Отчет в формате Markdown с поддержкой бинарных данных
    __recipe: Optional[recipe_model] = None

    @property
    def recipe(self) -> Optional[recipe_model]:
        # Получение текущей технологической карты отчета
        return self.__recipe

    def build(self, source) -> report_result_dto:
        # Построение отчета в формате Markdown
        if source is None:
            raise argument_exception("source", "Источник данных не может быть None.")

        lines = []

        if isinstance(source, recipe_model):
            self.__recipe = source
            lines.append(f"# {source.name}\n")
            lines.append("| Код | Наименование | Брутто | Нетто |")
            lines.append("| --- | --- | --- | --- |")
            for item in self.__recipe.items:
                lines.append(f"| {item.unique_code} | {item.name} | {item.brutto} | {item.netto} |")

        elif isinstance(source, nomenclature_model):
            lines.append(f"# {source.name}\n")
            lines.append("| Код | Наименование | Полное наименование | Группа | Единица измерения |")
            lines.append("| --- | --- | --- | --- | --- |")
            group = source.group.name if source.group else ""
            range_unit = source.range.name if source.range else ""
            lines.append(f"| {source.unique_code} | {source.name} | {source.full_name} | {group} | {range_unit} |")

        elif isinstance(source, range_model):
            lines.append(f"# {source.name}\n")
            lines.append("| Код | Наименование | Коэффициент | Базовая единица |")
            lines.append("| --- | --- | --- | --- |")
            base = source.base_range.name if source.base_range else ""
            lines.append(f"| {source.unique_code} | {source.name} | {source.conversion_factor} | {base} |")

        else:
            raise argument_exception(
                "source", "Неподдерживаемый тип источника данных."
            )

        text_content = "\n".join(lines)
        result = report_result_dto(text=text_content, data=text_content.encode("utf-8"))
        return result
