import datetime
from typing import Any, Dict, List, Optional, Union
from Src.Core.exceptions import argument_exception
from Src.Dtos.filter_type_enum import filter_type_enum


# Служебные ключи JSON, которые не считаются именами полей модели
_RESERVED_KEYS = {
    "domain_type",
    "entity_type",
    "filters",
    "field_name",
    "field",
    "filter_type",
    "type",
    "value",
    "start_period",
    "end_period",
}


class filter_item_dto:
    # Одно условие фильтрации: по какому полю, как и с чем сравнивать
    __field_name: str = ""
    __filter_type: filter_type_enum = filter_type_enum.EQUALS
    __value: Any = ""

    def __init__(
        self,
        field_name: str = "",
        filter_type: Union[filter_type_enum, str] = filter_type_enum.EQUALS,
        value: Any = "",
    ) -> None:
        self.__field_name = ""
        self.__filter_type = filter_type_enum.EQUALS
        self.__value = ""
        self.field_name = field_name
        self.filter_type = filter_type
        self.value = value

    @property
    def field_name(self) -> str:
        # Имя поля (можно указывать путь через точку)
        return self.__field_name

    @field_name.setter
    def field_name(self, value: str) -> None:
        if value is None:
            self.__field_name = ""
            return
        if not isinstance(value, str):
            raise argument_exception("field_name", "Имя поля должно быть строкой.")
        self.__field_name = value.strip()

    @property
    def filter_type(self) -> filter_type_enum:
        # Тип сравнения (EQUALS или LIKE)
        return self.__filter_type

    @filter_type.setter
    def filter_type(self, value: Union[filter_type_enum, str]) -> None:
        self.__filter_type = filter_type_enum.from_value(value)

    @property
    def value(self) -> Any:
        # Значение, с которым сравниваем
        return self.__value

    @value.setter
    def value(self, value: Any) -> None:
        self.__value = value

    def to_dict(self) -> Dict[str, Any]:
        # Сериализация условия в словарь
        return {
            "field_name": self.field_name,
            "filter_type": self.filter_type.name,
            "value": self.value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "filter_item_dto":
        # Разбор одного условия из словаря запроса
        if not isinstance(data, dict):
            return cls()
        field_name = data.get("field_name", data.get("field", ""))
        ft = data.get("filter_type", data.get("type", filter_type_enum.EQUALS))
        val = data.get("value", "")
        return cls(field_name=field_name, filter_type=ft, value=val)


class filter_dto:
    # DTO с набором условий фильтрации и опциональным периодом для ОСВ
    __filters: List[filter_item_dto]
    __domain_type: str = ""
    __start_period: Optional[datetime.datetime] = None
    __end_period: Optional[datetime.datetime] = None

    def __init__(
        self,
        filters: Optional[List[filter_item_dto]] = None,
        domain_type: str = "",
        start_period: Optional[Union[datetime.datetime, str]] = None,
        end_period: Optional[Union[datetime.datetime, str]] = None,
    ) -> None:
        self.__filters = []
        self.__domain_type = ""
        self.__start_period = None
        self.__end_period = None
        if filters is not None:
            self.filters = filters
        self.domain_type = domain_type
        self.start_period = start_period
        self.end_period = end_period

    @staticmethod
    def _parse_period(
        field_name: str,
        value: Optional[Union[datetime.datetime, str]],
    ) -> Optional[datetime.datetime]:
        # Разбираем дату периода из datetime или ISO-строки
        if value is None or value == "":
            return None
        if isinstance(value, datetime.datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.datetime.fromisoformat(value)
            except ValueError:
                raise argument_exception(field_name, "Некорректный формат даты периода.")
        raise argument_exception(field_name, "Период должен быть датой или ISO-строкой.")

    @property
    def filters(self) -> List[filter_item_dto]:
        # Копия списка условий фильтрации
        return list(self.__filters)

    @filters.setter
    def filters(self, value: List[filter_item_dto]) -> None:
        if not isinstance(value, (list, tuple)):
            raise argument_exception("filters", "Критерии фильтрации должны быть списком.")
        normalized = []
        for item in value:
            if isinstance(item, filter_item_dto):
                normalized.append(item)
            elif isinstance(item, dict):
                normalized.append(filter_item_dto.from_dict(item))
            else:
                raise argument_exception("filters", "Элемент фильтра должен быть filter_item_dto или dict.")
        self.__filters = normalized

    @property
    def domain_type(self) -> str:
        # Тип доменной модели, если передан в DTO
        return self.__domain_type

    @domain_type.setter
    def domain_type(self, value: str) -> None:
        if value is None:
            self.__domain_type = ""
            return
        if not isinstance(value, str):
            raise argument_exception("domain_type", "Тип доменной модели должен быть строкой.")
        self.__domain_type = value.strip()

    @property
    def start_period(self) -> Optional[datetime.datetime]:
        # Начало периода для расчета оборотов
        return self.__start_period

    @start_period.setter
    def start_period(self, value: Optional[Union[datetime.datetime, str]]) -> None:
        self.__start_period = self._parse_period("start_period", value)

    @property
    def end_period(self) -> Optional[datetime.datetime]:
        # Конец периода для расчета оборотов
        return self.__end_period

    @end_period.setter
    def end_period(self, value: Optional[Union[datetime.datetime, str]]) -> None:
        self.__end_period = self._parse_period("end_period", value)

    def add_filter(self, item: filter_item_dto) -> "filter_dto":
        # Добавить готовое условие фильтрации
        if not isinstance(item, filter_item_dto):
            raise argument_exception("item", "Элемент должен быть filter_item_dto.")
        self.__filters.append(item)
        return self

    def add(
        self,
        field_name: str,
        filter_type: Union[filter_type_enum, str] = filter_type_enum.EQUALS,
        value: Any = "",
    ) -> "filter_dto":
        # Удобный способ добавить условие без ручного создания filter_item_dto
        return self.add_filter(filter_item_dto(field_name, filter_type, value))

    def to_dict(self) -> Dict[str, Any]:
        # Переводим DTO в словарь
        result: Dict[str, Any] = {
            "domain_type": self.domain_type,
            "filters": [f.to_dict() for f in self.__filters],
        }
        if self.__start_period is not None:
            result["start_period"] = self.__start_period.isoformat()
        if self.__end_period is not None:
            result["end_period"] = self.__end_period.isoformat()
        return result

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "filter_dto":
        # Собираем filter_dto из входящего JSON (список filters, field_name/value или короткие поля)
        result = cls()
        if not data or not isinstance(data, dict):
            return result

        result.domain_type = str(data.get("domain_type", data.get("entity_type", "")))
        result.start_period = data.get("start_period")
        result.end_period = data.get("end_period")
        default_ft = data.get("filter_type", filter_type_enum.EQUALS)

        if "filters" in data and isinstance(data["filters"], list):
            for item_data in data["filters"]:
                if isinstance(item_data, dict):
                    result.add_filter(filter_item_dto.from_dict(item_data))
                elif isinstance(item_data, filter_item_dto):
                    result.add_filter(item_data)
        elif "field_name" in data and "value" in data:
            result.add(str(data["field_name"]), default_ft, data["value"])

        # Остальные ключи в словаре (например name или unique_code) тоже превращаем в фильтры
        existing_fields = {f.field_name for f in result.filters}
        for key, val in data.items():
            if key not in _RESERVED_KEYS and key not in existing_fields:
                result.add(str(key), default_ft, val)

        return result

    def __iter__(self):
        return iter(self.__filters)

    def __len__(self) -> int:
        return len(self.__filters)


__all__ = ["filter_type_enum", "filter_item_dto", "filter_dto"]
