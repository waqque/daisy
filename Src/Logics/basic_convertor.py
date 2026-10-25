from typing import Optional
from Src.Core.abstract_convertor import abstract_convertor


class basic_convertor(abstract_convertor):
    # Конвертор простых типов данных (numeric, str, bool)

    def convert(self, item: any, field_name: Optional[str] = None) -> dict:
        # Формирование словаря по простым типам: numeric, str
        if item is None:
            key = field_name if field_name else "value"
            return {key: None}

        # Поддержка переменного порядка аргументов convert(field_name, item)
        if isinstance(item, str) and field_name is not None and not isinstance(field_name, str):
            field_name, item = item, field_name

        # Конвертация одиночного простого значения
        if isinstance(item, (int, float, str, bool)):
            key = field_name if field_name else "value"
            return {key: item}

        # Извлечение полей простых типов из переданного объекта
        fields = self._extract_fields(item)
        result = {}
        for key, value in fields.items():
            if isinstance(value, (int, float, str, bool)):
                result[key] = value

        return result
