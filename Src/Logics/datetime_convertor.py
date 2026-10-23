import datetime
from typing import Optional
from Src.Core.abstract_convertor import abstract_convertor


class datetime_convertor(abstract_convertor):
    # Конвертор типов даты и времени (DateTime)

    def convert(self, item: any, field_name: Optional[str] = None) -> dict:
        # Формирование словаря по типу DateTime в формате строки ISO
        if item is None:
            return {}

        # Поддержка переменного порядка аргументов convert(field_name, item)
        if isinstance(item, str) and field_name is not None and not isinstance(field_name, str):
            field_name, item = item, field_name

        # Конвертация одиночного объекта даты/времени
        if isinstance(item, (datetime.datetime, datetime.date, datetime.time)):
            key = field_name if field_name else "value"
            return {key: item.isoformat()}

        # Извлечение полей DateTime из переданного объекта
        fields = self._extract_fields(item)
        result = {}
        for key, value in fields.items():
            if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
                result[key] = value.isoformat()

        return result
