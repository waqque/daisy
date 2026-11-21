from typing import Any, Optional
from Src.Core.abstract_convert_factory import abstract_convert_factory
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.abstract_model import base_model
from Src.Models.osv_row_model import osv_row_model


class osv_convertor(abstract_convertor):
    # Конвертор для перевода строки ОСВ в словарь для JSON-ответа
    _factory: Optional[abstract_convert_factory] = None

    def __init__(self, factory: Optional[abstract_convert_factory] = None) -> None:
        self._factory = factory

    @property
    def factory(self) -> abstract_convert_factory:
        # Если фабрику не передали явно, создаем ее при первом обращении
        if self._factory is None:
            from Src.Logics.convert_factory import convert_factory
            self._factory = convert_factory()
        return self._factory

    def convert(self, item: Any, field_name: Optional[str] = None) -> dict:
        # Разворачиваем поля строки ОСВ, вложенные модели отдаем фабрике конверторов
        if item is None:
            key = field_name if field_name else "value"
            return {key: None}

        if not isinstance(item, osv_row_model):
            return {}

        res = {}
        for key, value in self._extract_fields(item).items():
            if isinstance(value, base_model):
                res[key] = self.factory.convert(value)
            else:
                res[key] = value

        if field_name:
            return {field_name: res}
        return res
