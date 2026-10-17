from abc import ABC, abstractmethod
from typing import Type
from Src.Core.abstract_report import abstract_report
from Src.Dtos.report_type_dto import report_type_enum


class abstract_report_factory(ABC):
    # Абстрактная фабрика для создания отчетов

    @abstractmethod
    def create(self, report_type: report_type_enum) -> abstract_report:
        # Создание экземпляра отчета по переданному типу
        pass

    @abstractmethod
    def create_default(self, source=None) -> object:
        # Создание экземпляра отчета по умолчанию на основе настроек
        pass


    @abstractmethod
    def register(
        self, report_type: report_type_enum, report_class: Type[abstract_report]
    ) -> None:
        # Регистрация нового типа отчета в фабрике (Open/Closed Principle)
        pass


# Синоним для совместимости
abstract_factory = abstract_report_factory