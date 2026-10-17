from typing import Optional
from Src.Core.abstract_model import base_model
from Src.Core.exceptions import argument_exception


class report_result_model(base_model):
    # Доменная модель результата построения отчета
    __text: str = ""
    __binary: list

    def __init__(self, text: str = "", binary: Optional[list] = None) -> None:
        super().__init__()
        binary_list = binary if binary is not None else []
        if not isinstance(text, str):
            raise argument_exception("text", "Текст отчета должен быть строкой.")
        if not isinstance(binary_list, list):
            raise argument_exception("binary", "Бинарные данные должны быть списком.")

        self.__text = text if len(binary_list) == 0 else ""
        self.__binary = binary_list if len(text.strip()) == 0 else []

    @property
    def text(self) -> str:
        # Текстовое содержимое отчета
        return self.__text

    @text.setter
    def text(self, value: str) -> None:
        # Установка текстового содержимого
        if not isinstance(value, str):
            raise argument_exception("text", "Значение должно быть строкой.")
        self.__text = value
        self.__binary = []

    @property
    def binary(self) -> list:
        # Бинарные данные отчета
        return list(self.__binary)

    @binary.setter
    def binary(self, value: list) -> None:
        # Установка бинарного содержимого
        if not isinstance(value, list):
            raise argument_exception("binary", "Значение должно быть списком.")
        if len(value) > 0:
            self.__text = ""
            self.__binary = list(value)