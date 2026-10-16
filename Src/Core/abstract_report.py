from abc import ABC, abstractmethod


class abstract_report(ABC):
    # Базовый абстрактный класс для формирования отчетов

    @abstractmethod
    def build(self, source) -> object:
        # Построение отчета на основе переданного источника данных
        pass
