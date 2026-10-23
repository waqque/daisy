import datetime
from typing import Optional
from Src.Core.abstract_convertor import abstract_convertor


class reference_convertor(abstract_convertor):
    # Конвертор ссылочных типов (Reference) с делегированием фабрике
    _factory: Optional[object] = None

    def __init__(self, factory=None) -> None:
        # Инициализация с возможностью передачи фабрики
        self._factory = factory

    @property
    def factory(self):
        # Ленивое получение фабрики конверторов для исключения циклического импорта
        if self._factory is None:
            from Src.Logics.convert_factory import convert_factory
            self._factory = convert_factory()
        return self._factory

    def convert(
        self,
        item: any,
        field_name: Optional[str] = None,
        is_nested: bool = False,
    ) -> dict:
        # Формирование словаря по ссылочным типам (Reference)
        if item is None:
            return {}

        # Поддержка переменного порядка аргументов convert(field_name, item)
        if isinstance(item, str) and field_name is not None and not isinstance(field_name, str):
            field_name, item = item, field_name

        # Простые типы и DateTime не являются ссылочными
        if isinstance(
            item,
            (int, float, str, bool, datetime.datetime, datetime.date, datetime.time),
        ):
            return {}

        # Обработка одиночной ссылки с явным именем поля: convert(item, "group")
        if field_name is not None:
            return {field_name: self.factory.convert(item)}

        # Извлечение полей объекта и поиск ссылочных типов
        fields = self._extract_fields(item)
        result = {}
        has_reference_field = False

        for key, value in fields.items():
            # Пропуск простых типов и типов даты/времени
            if isinstance(
                value,
                (int, float, str, bool, datetime.datetime, datetime.date, datetime.time),
            ):
                continue

            # Обработка обнаруженного ссылочного поля
            has_reference_field = True
            if value is None:
                result[key] = None
            elif isinstance(value, (list, tuple)):
                result[key] = [self.factory.convert(elem) for elem in value]
            else:
                result[key] = self.factory.convert(value)

        # Конвертация базовых полей одиночной сущности при прямом вызове
        if not has_reference_field and not is_nested and fields:
            res = {}
            res.update(self.factory.basic.convert(item))
            res.update(self.factory.datetime.convert(item))
            return res

        return result
