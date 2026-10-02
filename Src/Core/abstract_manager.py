from abc import ABC, abstractmethod


class abstract_manager(ABC):
    # Базовый абстрактный класс для менеджеров данных

    def __init__(self) -> None:
        # Флаг успешной загрузки данных на уровне экземпляра
        self._is_loaded: bool = False

    @abstractmethod
    def convert(self, data: dict) -> None:
        # Абстрактный метод обработки и конвертации загруженных данных
        pass

    def load(self, file_name: str = "") -> bool:
        # Базовый метод загрузки данных
        return False

    @property
    def is_loaded(self) -> bool:
        # Проверка факта успешной загрузки данных
        return self._is_loaded