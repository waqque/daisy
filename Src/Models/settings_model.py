from Src.Core.exceptions import argument_exception
from Src.Models.organization_model import organization_model


class settings_model(organization_model):
  # Модель настроек приложения с параметрами организации и флагом первого старта
  __is_first_start: bool = True

  def __init__(self) -> None:
    # Инициализация организации значениями по умолчанию
    super().__init__(
        name="ООО Ромашка",
        inn="7701234567",
        bic="044525225",
        account="40702810938000012345",
        ownership_form="ООО",
    )
    self.__is_first_start = True

  @property
  def is_first_start(self) -> bool:
    # Флаг первого запуска системы
    return self.__is_first_start

  @is_first_start.setter
  def is_first_start(self, value: bool) -> None:
    # Валидация типа булевого флага
    if not isinstance(value, bool):
      raise argument_exception(
          "is_first_start", "Флаг первого запуска должен быть типа bool."
      )
    self.__is_first_start = value