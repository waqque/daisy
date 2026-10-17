class report_result_dto:
    # DTO представления результата построения отчета
    __text: str = ""
    __data: bytes = b""

    def __init__(self, text: str = "", data: bytes = b"") -> None:
        self.__text = text
        self.__data = data if data else (text.encode("utf-8") if text else b"")

    @property
    def text(self) -> str:
        # Текстовое содержимое отчета
        return self.__text

    @text.setter
    def text(self, value: str) -> None:
        # Установка текстового содержимого отчета
        self.__text = str(value)
        self.__data = self.__text.encode("utf-8")

    @property
    def data(self) -> bytes:
        # Бинарное содержимое отчета
        return self.__data

    @data.setter
    def data(self, value: bytes) -> None:
        # Установка бинарного содержимого отчета
        self.__data = bytes(value)

    @property
    def binary(self) -> list:
        # Бинарное содержимое отчета в виде списка
        return list(self.__data)

    @binary.setter
    def binary(self, value: list) -> None:
        # Установка бинарного содержимого
        if isinstance(value, (list, bytes, bytearray)):
            self.__data = bytes(value)
            if len(self.__data) > 0:
                self.__text = ""

