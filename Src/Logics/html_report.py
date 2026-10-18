from typing import Optional
from Src.Core.abstract_report import abstract_report
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_model import recipe_model


class html_report(abstract_report):
    # Отчет в формате HTML
    __recipe: Optional[recipe_model] = None

    def __init__(self) -> None:
        # Регистрация обработчиков сущностей для формата HTML
        super().__init__()
        self.register(recipe_model, self._build_recipe)
        self.register(nomenclature_model, self._build_nomenclature)
        self.register(range_model, self._build_range)

    @property
    def recipe(self) -> Optional[recipe_model]:
        # Получение текущей технологической карты отчета
        return self.__recipe

    def _build_recipe(self, source: recipe_model) -> report_result_dto:
        # Построение HTML-отчета по технологической карте
        self.__recipe = source
        lines = [
            "<!DOCTYPE html>",
            "<html>",
            "<head><meta charset='utf-8'><title>Отчет</title></head>",
            "<body>",
            f"  <h1>{source.name}</h1>",
            "  <table border='1'>",
            "    <tr><th>Код</th><th>Наименование</th><th>Брутто</th><th>Нетто</th></tr>",
        ]
        for item in self.__recipe.items:
            lines.append(f"    <tr><td>{item.unique_code}</td><td>{item.name}</td><td>{item.brutto}</td><td>{item.netto}</td></tr>")
        lines.extend([
            "  </table>",
            "</body>",
            "</html>",
        ])
        result = report_result_dto()
        result.text = "\n".join(lines)
        return result

    def _build_nomenclature(self, source: nomenclature_model) -> report_result_dto:
        # Построение HTML-отчета по номенклатуре
        group = source.group.name if source.group else ""
        range_unit = source.range.name if source.range else ""
        lines = [
            "<!DOCTYPE html>",
            "<html>",
            "<head><meta charset='utf-8'><title>Отчет</title></head>",
            "<body>",
            f"  <h1>{source.name}</h1>",
            "  <table border='1'>",
            "    <tr><th>Код</th><th>Наименование</th><th>Полное наименование</th><th>Группа</th><th>Единица измерения</th></tr>",
            f"    <tr><td>{source.unique_code}</td><td>{source.name}</td><td>{source.full_name}</td><td>{group}</td><td>{range_unit}</td></tr>",
            "  </table>",
            "</body>",
            "</html>",
        ]
        result = report_result_dto()
        result.text = "\n".join(lines)
        return result

    def _build_range(self, source: range_model) -> report_result_dto:
        # Построение HTML-отчета по единице измерения
        base = source.base_range.name if source.base_range else ""
        lines = [
            "<!DOCTYPE html>",
            "<html>",
            "<head><meta charset='utf-8'><title>Отчет</title></head>",
            "<body>",
            f"  <h1>{source.name}</h1>",
            "  <table border='1'>",
            "    <tr><th>Код</th><th>Наименование</th><th>Коэффициент</th><th>Базовая единица</th></tr>",
            f"    <tr><td>{source.unique_code}</td><td>{source.name}</td><td>{source.conversion_factor}</td><td>{base}</td></tr>",
            "  </table>",
            "</body>",
            "</html>",
        ]
        result = report_result_dto()
        result.text = "\n".join(lines)
        return result

    @property
    def mimetype(self) -> str:
        # MIME-тип HTML отчета
        return "text/html; charset=utf-8"

    @property
    def file_extension(self) -> str:
        # Расширение файла HTML
        return "html"
