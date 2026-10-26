from abc import ABC, abstractmethod
from typing import Optional


class abstract_convertor(ABC):
    # Абстрактный класс конвертора объектов в словарь (ключ - имя поля, значение - данные поля)

    @abstractmethod
    def convert(self, item: any, field_name: Optional[str] = None) -> dict:
        # Абстрактный метод конвертации любого объекта в словарь
        pass

    @staticmethod
    def _extract_fields(item: any) -> dict:
        # Вспомогательный метод извлечения полей и их значений из переданного объекта
        if item is None:
            return {}

        if isinstance(item, dict):
            return dict(item)

        fields = {}

        # Извлечение полей из словаря атрибутов объекта с деманглингом приватных полей
        if hasattr(item, "__dict__"):
            for key, val in item.__dict__.items():
                if key.startswith("_"):
                    parts = key.split("__", 1)
                    field_name = parts[1] if len(parts) == 2 else key.lstrip("_")
                else:
                    field_name = key

                # Получение актуального значения через геттер свойства при его наличии
                cls_prop = getattr(type(item), field_name, None)
                if isinstance(cls_prop, property):
                    try:
                        val = getattr(item, field_name)
                    except Exception:
                        pass
                fields[field_name] = val

        # Извлечение свойств объекта, если __dict__ пуст
        if not fields:
            for attr_name in dir(type(item)):
                if attr_name.startswith("_"):
                    continue
                attr = getattr(type(item), attr_name, None)
                if isinstance(attr, property):
                    try:
                        fields[attr_name] = getattr(item, attr_name)
                    except Exception:
                        pass

        return fields
