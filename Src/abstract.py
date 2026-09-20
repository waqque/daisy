from abc import ABC
import uuid
class base_model(ABC):
    __name: str = ""

    def __init__(self) -> None:
        self._id: str = str(uuid.uuid4()) # генерация айдишников

    @property
    def id(self) -> int: #получение кода(айди) сущности
        return self.__id

    @property
    def name(self) -> str:# получение наименования сущности
        return self.__name

    @name.setter
    def name(self, value: str) -> None: #установка наименования сущности

        if not isinstance(value, str):
            raise ValueError("Наименование должно быть строкой.")
        
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("Наименование не может быть пустым.")

        self.__name = normalized_value
