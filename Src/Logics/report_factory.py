from typing import Dict, Optional, Type
from Src.Core.abstract_report import abstract_report
from Src.Core.abstract_report_factory import abstract_report_factory
from Src.Core.exceptions import argument_exception
from Src.Dtos.report_type_dto import report_type_enum
from Src.Logics.csv_report import csv_report
from Src.Logics.html_report import html_report
from Src.Logics.markdown_report import markdown_report
from Src.Logics.settings_manager import settings_manager
from Src.Logics.text_report import text_report
from Src.Logics.xml_report import xml_report
from Src.Models.settings_model import settings_model


class report_factory(abstract_report_factory):
    # Фабрика формирования отчетов с инкапсуляцией настроек
    __settings: Optional[settings_model] = None
    __mapping: Dict[report_type_enum, Type[abstract_report]]

    def __init__(self, settings: Optional[settings_model] = None) -> None:
        # Инициализация фабрики с инкапсуляцией настроек
        if settings is not None:
            self.settings = settings
        else:
            manager = settings_manager()
            if not manager.is_loaded:
                manager.load()
            self.__settings = manager.settings

        # Маппинг типов отчетов и соответствующих классов
        self.__mapping = {
            report_type_enum.TXT: text_report,
            report_type_enum.CSV: csv_report,
            report_type_enum.MARKDOWN: markdown_report,
            report_type_enum.XML: xml_report,
            report_type_enum.HTML: html_report,
        }

    @property
    def settings(self) -> Optional[settings_model]:
        # Получение инкапсулированных настроек
        return self.__settings

    @settings.setter
    def settings(self, value: settings_model) -> None:
        # Установка настроек с проверкой типа
        if not isinstance(value, settings_model):
            raise argument_exception(
                "settings", "Настройки должны быть объектом settings_model."
            )
        self.__settings = value

    def register(
        self, report_type: report_type_enum, report_class: Type[abstract_report]
    ) -> None:
        # Регистрация нового типа отчета в фабрике (Open/Closed Principle)
        if not isinstance(report_type, report_type_enum):
            raise argument_exception(
                "report_type", "Тип отчета должен быть элементом report_type_enum."
            )
        if not (isinstance(report_class, type) and issubclass(report_class, abstract_report)):
            raise argument_exception(
                "report_class", "Класс отчета должен наследоваться от abstract_report."
            )
        self.__mapping[report_type] = report_class

    def create(self, report_type: report_type_enum) -> abstract_report:
        # Создание экземпляра отчета по переданному типу
        if not isinstance(report_type, report_type_enum):
            raise argument_exception(
                "report_type", "Тип отчета должен быть элементом report_type_enum."
            )

        if report_type not in self.__mapping:
            raise argument_exception(
                "report_type", f"Указанный тип отчета {report_type} не реализован!"
            )

        report_class = self.__mapping[report_type]
        return report_class()

    def create_default(self, source=None) -> object:
        # Создание экземпляра отчета по умолчанию на основе настроек
        settings = self.__settings or settings_manager().settings
        format_type = settings.response_format if settings and settings.response_format else report_type_enum.TXT
        report = self.create(format_type)
        if source is not None:
            return report.build(source)
        return report


    @classmethod
    def create_report(cls, report_type: report_type_enum, source) -> object:
        # Вспомогательный метод создания и построения отчета
        factory = cls()
        report = factory.create(report_type)
        return report.build(source)