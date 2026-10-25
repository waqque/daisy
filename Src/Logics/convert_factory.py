import datetime
from typing import Dict, Optional, Type
from Src.Core.abstract_convert_factory import abstract_convert_factory
from Src.Core.abstract_convertor import abstract_convertor
from Src.Logics.basic_convertor import basic_convertor
from Src.Logics.datetime_convertor import datetime_convertor
from Src.Logics.reference_convertor import reference_convertor


class convert_factory(abstract_convert_factory):
    # Фабрика конверторов, реализующая абстрактную фабрику abstract_convert_factory
    _basic_convertor: basic_convertor
    _datetime_convertor: datetime_convertor
    _reference_convertor: reference_convertor
    _mapping: Dict[Type, abstract_convertor]

    def __init__(self) -> None:
        # Инициализация экземпляров конверторов
        self._basic_convertor = basic_convertor()
        self._datetime_convertor = datetime_convertor()
        self._reference_convertor = reference_convertor(factory=self)

        # Маппинг типов данных на соответствующие конверторы (по аналогии с report_factory)
        self._mapping = {
            int: self._basic_convertor,
            float: self._basic_convertor,
            str: self._basic_convertor,
            bool: self._basic_convertor,
            datetime.datetime: self._datetime_convertor,
            datetime.date: self._datetime_convertor,
            datetime.time: self._datetime_convertor,
        }

    @property
    def basic(self) -> basic_convertor:
        # Получение конвертора простых типов
        return self._basic_convertor

    @property
    def datetime(self) -> datetime_convertor:
        # Получение конвертора типов даты/времени
        return self._datetime_convertor

    @property
    def reference(self) -> reference_convertor:
        # Получение конвертора ссылочных типов
        return self._reference_convertor

    def create(self, item_or_type: any) -> abstract_convertor:
        # Фабричный метод получения конвертора через словарь маппинга
        target_type = (
            item_or_type if isinstance(item_or_type, type) else type(item_or_type)
        )

        # Прямой поиск в словаре
        if target_type in self._mapping:
            return self._mapping[target_type]

        # Поиск с учетом иерархии типов
        for registered_type, convertor in self._mapping.items():
            if issubclass(target_type, registered_type):
                return convertor

        # По умолчанию для всех ссылочных объектов - ссылочный конвертор
        return self._reference_convertor

    def convert(self, item: any = None, visited: Optional[set] = None) -> any:
        # Формирование набора словарей согласно исходной структуры любого переданного объекта
        if not isinstance(self, convert_factory):
            actual_item = self
            return convert_factory().convert(actual_item)

        if item is None:
            return None

        # Инициализация множества для предотвращения рекурсии
        if visited is None:
            visited = set()

        # Коллекции (списки и кортежи)
        if isinstance(item, (list, tuple)):
            return [self.convert(x, visited) for x in item]

        # Словари
        if isinstance(item, dict):
            return {k: self.convert(v, visited) for k, v in item.items()}

        # Проверка циклических ссылок для составных объектов
        item_id = id(item)
        if item_id in visited:
            return None
        visited.add(item_id)

        # Для простого типа или DateTime используем конвертор из маппинга
        target_type = type(item)
        if target_type in self._mapping:
            return self._mapping[target_type].convert(item)

        # Для составного объекта извлекаем поля и подбираем конвертор по каждому полю через фабрику
        fields = abstract_convertor._extract_fields(item)
        if fields:
            result = {}
            for key, val in fields.items():
                if val is None:
                    result[key] = None
                elif isinstance(val, (list, tuple)):
                    result[key] = [self.convert(elem, visited) for elem in val]
                else:
                    convertor = self.create(val)
                    result.update(convertor.convert(val, key))
            return result

        # Если у объекта нет полей, подбираем конвертор по его типу
        convertor = self.create(item)
        return convertor.convert(item)
