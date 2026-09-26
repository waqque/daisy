# Ошибки предметной области приложения


class argument_exception(Exception):
  # Ошибка валидации переданных параметров
  __stack_trace: str = ""
  __message: str = ""
  __field: str = ""

  def __init__(self, field: str, message: str, stack_trace: str = "") -> None:
    self.__field = str(field).strip()
    self.__message = str(message).strip()
    self.__stack_trace = str(stack_trace).strip()
    super().__init__(self.__str__())

  def __str__(self) -> str:
    return (
        f"Error: incorrect argument {self.__field}!\n"
        f" {self.__message}\n{self.__stack_trace}"
    )


class operation_exception(Exception):
  # Ошибка нарушения бизнес-логики
  pass