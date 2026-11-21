from abc import ABC, abstractmethod
from Src.Dtos.filter_dto import filter_dto


class abstract_prototype(ABC):
    # Базовый класс для шаблона Прототип

    @abstractmethod
    def clone(self, filter: filter_dto) -> "abstract_prototype":
        # Вернуть новый прототип с отфильтрованными данными
        pass
