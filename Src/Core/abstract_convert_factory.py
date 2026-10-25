from abc import ABC, abstractmethod
from Src.Core.abstract_convertor import abstract_convertor


class abstract_convert_factory(ABC):
    # Абстрактная фабрика для создания конверторов и сериализации объектов

    @abstractmethod
    def create(self, item_or_type: any) -> abstract_convertor:
        # Абстрактный метод получения подходящего конвертора по типу данных или объекту
        pass

    @abstractmethod
    def convert(self, item: any = None) -> any:
        # Абстрактный метод сериализации объекта в словарь или набор словарей
        pass
