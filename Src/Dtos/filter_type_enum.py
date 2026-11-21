from enum import Enum
from Src.Core.exceptions import argument_exception


class filter_type_enum(Enum):
    # Варианты сравнения при фильтрации
    EQUALS = "EQUALS"
    LIKE = "LIKE"

    @classmethod
    def from_value(cls, value: object) -> "filter_type_enum":
        # Приводим строку или enum к значению перечисления
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            norm = value.strip().upper()
            aliases = {
                "EQUALS": cls.EQUALS,
                "EQ": cls.EQUALS,
                "EQUAL": cls.EQUALS,
                "LIKE": cls.LIKE,
                "CONTAINS": cls.LIKE,
                "IN": cls.LIKE,
            }
            if norm in aliases:
                return aliases[norm]
        raise argument_exception("filter_type", f"Неподдерживаемый тип фильтрации: {value}")
