from typing import Optional
from Src.Core.abstract_report import abstract_report
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_model import recipe_model


class xml_report(abstract_report):
    # Отчет в формате XML
    __recipe: Optional[recipe_model] = None

    def __init__(self) -> None:
        # Регистрация обработчиков сущностей для формата XML
        super().__init__()
        self.register(recipe_model, self._build_recipe)
        self.register(nomenclature_model, self._build_nomenclature)
        self.register(range_model, self._build_range)

    @property
    def recipe(self) -> Optional[recipe_model]:
        # Получение текущей технологической карты отчета
        return self.__recipe

    def _build_recipe(self, source: recipe_model) -> report_result_dto:
        # Построение XML-отчета по технологической карте
        self.__recipe = source
        lines = [
            '<?xml version="1.0" encoding="utf-8"?>',
            f'<recipe name="{source.name}" code="{source.unique_code}">',
            "  <items>",
        ]
        for item in self.__recipe.items:
            lines.extend([
                "    <item>",
                f"      <code>{item.unique_code}</code>",
                f"      <name>{item.name}</name>",
                f"      <brutto>{item.brutto}</brutto>",
                f"      <netto>{item.netto}</netto>",
                "    </item>",
            ])
        lines.extend([
            "  </items>",
            "</recipe>",
        ])
        result = report_result_dto()
        result.text = "\n".join(lines)
        return result

    def _build_nomenclature(self, source: nomenclature_model) -> report_result_dto:
        # Построение XML-отчета по номенклатуре
        group = source.group.name if source.group else ""
        range_unit = source.range.name if source.range else ""
        lines = [
            '<?xml version="1.0" encoding="utf-8"?>',
            f'<nomenclature code="{source.unique_code}">',
            f"  <name>{source.name}</name>",
            f"  <full_name>{source.full_name}</full_name>",
            f"  <group>{group}</group>",
            f"  <range>{range_unit}</range>",
            "</nomenclature>",
        ]
        result = report_result_dto()
        result.text = "\n".join(lines)
        return result

    def _build_range(self, source: range_model) -> report_result_dto:
        # Построение XML-отчета по единице измерения
        base = source.base_range.name if source.base_range else ""
        lines = [
            '<?xml version="1.0" encoding="utf-8"?>',
            f'<range code="{source.unique_code}">',
            f"  <name>{source.name}</name>",
            f"  <conversion_factor>{source.conversion_factor}</conversion_factor>",
            f"  <base_range>{base}</base_range>",
            "</range>",
        ]
        result = report_result_dto()
        result.text = "\n".join(lines)
        return result

    @property
    def mimetype(self) -> str:
        # MIME-тип XML отчета
        return "application/xml; charset=utf-8"

    @property
    def file_extension(self) -> str:
        # Расширение файла XML
        return "xml"
