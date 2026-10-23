import datetime
from typing import Optional
from Src.Core.abstract_convertor import abstract_convertor
from Src.Logics.basic_convertor import basic_convertor
from Src.Logics.datetime_convertor import datetime_convertor
from Src.Logics.reference_convertor import reference_convertor


class convert_factory:
    # Фабрика конверторов по шаблону "Фабрика" (Factory)
    _basic_convertor: basic_convertor
    _datetime_convertor: datetime_convertor
    _reference_convertor: reference_convertor

    def __init__(self) -> None:
        # Инициализация экземпляров конверторов
        self._basic_convertor = basic_convertor()
        self._datetime_convertor = datetime_convertor()
        self._reference_convertor = reference_convertor(factory=self)

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
        # Фабричный метод получения конвертора по типу данных или переданному объекту
        target_type = (
            item_or_type if isinstance(item_or_type, type) else type(item_or_type)
        )

        if issubclass(target_type, (int, float, str, bool)):
            return self._basic_convertor

        if issubclass(
            target_type, (datetime.datetime, datetime.date, datetime.time)
        ):
            return self._datetime_convertor

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

        # Одиночные простые типы и типы DateTime подбираются через фабрику
        if isinstance(
            item,
            (int, float, str, bool, datetime.datetime, datetime.date, datetime.time),
        ):
            convertor = self.create(item)
            return convertor.convert(item)

        # Конвертация элементов коллекции
        if isinstance(item, (list, tuple)):
            return [self.convert(x, visited) for x in item]

        # Рекурсивная конвертация словаря
        if isinstance(item, dict):
            return {k: self.convert(v, visited) for k, v in item.items()}

        # Проверка циклических ссылок
        item_id = id(item)
        if item_id in visited:
            return None
        visited.add(item_id)

        # Извлечение полей объекта и подбор конвертора для каждого поля через фабрику
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
