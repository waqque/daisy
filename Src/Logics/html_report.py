from typing import Optional
from Src.Core.abstract_report import abstract_report
from Src.Core.exceptions import argument_exception
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_model import recipe_model


class html_report(abstract_report):
    # Отчет в формате HTML
    __recipe: Optional[recipe_model] = None

    @property
    def recipe(self) -> Optional[recipe_model]:
        # Получение текущей технологической карты отчета
        return self.__recipe

    def build(self, source) -> report_result_dto:
        # Построение HTML-отчета
        if source is None:
            raise argument_exception("source", "Источник данных не может быть None.")

        lines = [
            "<!DOCTYPE html>",
            "<html>",
            "<head><meta charset='utf-8'><title>Отчет</title></head>",
            "<body>",
        ]

        if isinstance(source, recipe_model):
            self.__recipe = source
            lines.append(f"  <h1>{source.name}</h1>")
            lines.append("  <table border='1'>")
            lines.append("    <tr><th>Код</th><th>Наименование</th><th>Брутто</th><th>Нетто</th></tr>")
            for item in self.__recipe.items:
                lines.append(f"    <tr><td>{item.unique_code}</td><td>{item.name}</td><td>{item.brutto}</td><td>{item.netto}</td></tr>")
            lines.append("  </table>")

        elif isinstance(source, nomenclature_model):
            group = source.group.name if source.group else ""
            range_unit = source.range.name if source.range else ""
            lines.append(f"  <h1>{source.name}</h1>")
            lines.append("  <table border='1'>")
            lines.append("    <tr><th>Код</th><th>Наименование</th><th>Полное наименование</th><th>Группа</th><th>Единица измерения</th></tr>")
            lines.append(f"    <tr><td>{source.unique_code}</td><td>{source.name}</td><td>{source.full_name}</td><td>{group}</td><td>{range_unit}</td></tr>")
            lines.append("  </table>")

        elif isinstance(source, range_model):
            base = source.base_range.name if source.base_range else ""
            lines.append(f"  <h1>{source.name}</h1>")
            lines.append("  <table border='1'>")
            lines.append("    <tr><th>Код</th><th>Наименование</th><th>Коэффициент</th><th>Базовая единица</th></tr>")
            lines.append(f"    <tr><td>{source.unique_code}</td><td>{source.name}</td><td>{source.conversion_factor}</td><td>{base}</td></tr>")
            lines.append("  </table>")

        else:
            raise argument_exception(
                "source", "Неподдерживаемый тип источника данных."
            )

        lines.append("</body>")
        lines.append("</html>")

        result = report_result_dto()
        result.text = "\n".join(lines)
        return result
