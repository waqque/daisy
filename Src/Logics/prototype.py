import datetime
from enum import Enum
from typing import Any, Iterator, List, Optional, Set
from Src.Core.abstract_prototype import abstract_prototype
from Src.Dtos.filter_dto import filter_dto, filter_item_dto
from Src.Dtos.filter_type_enum import filter_type_enum


# Простые типы, внутрь которых не нужно заходить при рекурсивном поиске
_SCALAR_TYPES = (
    int,
    float,
    str,
    bool,
    bytes,
    datetime.datetime,
    datetime.date,
    datetime.time,
    Enum,
)


class prototype(abstract_prototype):
    # Универсальный прототип для фильтрации коллекций любых доменных моделей
    __data: List[Any]

    def __init__(self, data: Optional[List[Any]] = None) -> None:
        self.__data = list(data) if data is not None else []

    @property
    def data(self) -> List[Any]:
        # Возвращаем копию списка, чтобы не сломать внутренние данные снаружи
        return list(self.__data)

    def clone(self, filter: Optional[filter_dto] = None) -> "prototype":
        # Клонируем прототип, оставляя только подходящие под фильтр элементы
        if filter is None or len(filter.filters) == 0:
            return prototype(self.__data)

        filtered = [
            item
            for item in self.__data
            if self._match_all(item, filter.filters)
        ]
        return prototype(filtered)

    @classmethod
    def _match_all(cls, item: Any, filters: List[filter_item_dto]) -> bool:
        # Элемент подходит, только если совпали все условия из фильтра
        return all(cls._match_single(item, f) for f in filters)

    @classmethod
    def _match_single(cls, item: Any, filter_item: filter_item_dto) -> bool:
        # Проверка одного условия: либо по явному пути через точку, либо рекурсивно
        field_name = filter_item.field_name.strip()
        if not field_name:
            return False

        if "." in field_name:
            return cls._match_dotted_path(
                item,
                field_name.split("."),
                filter_item.value,
                filter_item.filter_type,
            )

        return cls._match_recursive(item, filter_item, set())

    @classmethod
    def _check_scalar_match(cls, val: Any, target: Any, ftype: filter_type_enum) -> bool:
        # Сравниваем значения без учета регистра и лишних пробелов
        if val is None:
            return target is None

        val_str = str(val).strip().lower()
        target_str = str(target).strip().lower()

        if ftype == filter_type_enum.EQUALS:
            return val_str == target_str
        if ftype == filter_type_enum.LIKE:
            return target_str in val_str
        return False

    @staticmethod
    def _is_scalar(value: Any) -> bool:
        return value is None or isinstance(value, _SCALAR_TYPES)

    @classmethod
    def _iter_nested_objects(cls, obj: Any) -> Iterator[Any]:
        # Достаем все вложенные объекты и элементы коллекций без привязки к именам полей
        if not hasattr(obj, "__dict__"):
            return

        for val in vars(obj).values():
            if val is None or cls._is_scalar(val):
                continue
            if isinstance(val, (list, tuple, set)):
                for elem in val:
                    if elem is not None and not cls._is_scalar(elem):
                        yield elem
            elif isinstance(val, dict):
                for elem in val.values():
                    if elem is not None and not cls._is_scalar(elem):
                        yield elem
            elif hasattr(val, "__dict__"):
                yield val

    @classmethod
    def _match_recursive(
        cls,
        current: Any,
        filter_item: filter_item_dto,
        visited: Set[int],
    ) -> bool:
        # Ищем совпадение на текущем объекте и при необходимости спускаемся во вложенные
        if current is None:
            return False

        # Защита от зацикливания, если объекты ссылаются друг на друга
        obj_id = id(current)
        if obj_id in visited:
            return False
        visited.add(obj_id)

        field_name = filter_item.field_name.strip()
        target_value = filter_item.value
        ftype = filter_item.filter_type

        if hasattr(current, field_name):
            val = getattr(current, field_name)
            if cls._is_scalar(val):
                if cls._check_scalar_match(val, target_value, ftype):
                    return True
            elif cls._match_recursive(val, filter_item, visited):
                return True

        for nested in cls._iter_nested_objects(current):
            if cls._match_recursive(nested, filter_item, visited):
                return True

        return False

    @classmethod
    def _match_dotted_path(
        cls,
        current: Any,
        parts: List[str],
        target: Any,
        ftype: filter_type_enum,
    ) -> bool:
        # Пошаговый проход по пути вида "range.base_range.name"
        if current is None or not parts:
            return False

        # Если на пути попался список (например строки рецепта), проверяем каждый элемент
        if isinstance(current, (list, tuple, set)):
            return any(
                cls._match_dotted_path(elem, parts, target, ftype)
                for elem in current
            )

        attr = parts[0]
        if not hasattr(current, attr):
            return False

        next_val = getattr(current, attr)
        if len(parts) == 1:
            return cls._check_scalar_match(next_val, target, ftype)

        return cls._match_dotted_path(next_val, parts[1:], target, ftype)

    def __iter__(self):
        return iter(self.__data)

    def __len__(self) -> int:
        return len(self.__data)
