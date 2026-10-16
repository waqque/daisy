from typing import Optional
from Src.Core.abstract_report import abstract_report
from Src.Core.exceptions import argument_exception
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_model import recipe_model


class xml_report(abstract_report):
    # Отчет в формате XML
    __recipe: Optional[recipe_model] = None

    @property
    def recipe(self) -> Optional[recipe_model]:
        # Получение текущей технологической карты отчета
        return self.__recipe

    def build(self, source) -> report_result_dto:
        # Построение XML-отчета
        if source is None:
            raise argument_exception("source", "Источник данных не может быть None.")

        lines = ['<?xml version="1.0" encoding="utf-8"?>']

        if isinstance(source, recipe_model):
            self.__recipe = source
            lines.append(f'<recipe name="{source.name}" code="{source.unique_code}">')
            lines.append("  <items>")
            for item in self.__recipe.items:
                lines.append("    <item>")
                lines.append(f"      <code>{item.unique_code}</code>")
                lines.append(f"      <name>{item.name}</name>")
                lines.append(f"      <brutto>{item.brutto}</brutto>")
                lines.append(f"      <netto>{item.netto}</netto>")
                lines.append("    </item>")
            lines.append("  </items>")
            lines.append("</recipe>")

        elif isinstance(source, nomenclature_model):
            group = source.group.name if source.group else ""
            range_unit = source.range.name if source.range else ""
            lines.append(f'<nomenclature code="{source.unique_code}">')
            lines.append(f"  <name>{source.name}</name>")
            lines.append(f"  <full_name>{source.full_name}</full_name>")
            lines.append(f"  <group>{group}</group>")
            lines.append(f"  <range>{range_unit}</range>")
            lines.append("</nomenclature>")

        elif isinstance(source, range_model):
            base = source.base_range.name if source.base_range else ""
            lines.append(f'<range code="{source.unique_code}">')
            lines.append(f"  <name>{source.name}</name>")
            lines.append(f"  <conversion_factor>{source.conversion_factor}</conversion_factor>")
            lines.append(f"  <base_range>{base}</base_range>")
            lines.append("</range>")

        else:
            raise argument_exception(
                "source", "Неподдерживаемый тип источника данных."
            )

        result = report_result_dto()
        result.text = "\n".join(lines)
        return result
