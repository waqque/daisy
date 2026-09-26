from abc import ABC
import uuid
from Src.Core.exceptions import argument_exception


class base_model(ABC):
  # Базовый абстрактный класс для всех сущностей
  __name: str = ""
  __unique_code: str = ""

  def __init__(self) -> None:
    # При создании сразу генерируем уникальный строковый UUID
    self.__unique_code = str(uuid.uuid4())

  @property
  def unique_code(self) -> str:
    # Получение уникального кода
    return self.__unique_code

  @unique_code.setter
  def unique_code(self, value: str) -> None:
    # Валидация и установка уникального кода
    if not isinstance(value, str):
      raise argument_exception(
          "unique_code", "Уникальный код должен быть строкой."
      )

    normalized_value = value.strip()
    if not normalized_value:
      raise argument_exception(
          "unique_code", "Уникальный код не может быть пустым."
      )

    self.__unique_code = normalized_value

  @property
  def id(self) -> str:
    # Синоним к unique_code (возвращает str)
    return self.unique_code

  @id.setter
  def id(self, value: str) -> None:
    # Прокидываем id в сеттер unique_code
    self.unique_code = value

  @property
  def name(self) -> str:
    # Получение обычного наименования
    return self.__name

  @name.setter
  def name(self, value: str) -> None:
    # Проверка типа, непустоты и ограничения длины в 50 символов
    if not isinstance(value, str):
      raise argument_exception("name", "Наименование должно быть строкой.")

    normalized_value = value.strip()
    if not normalized_value:
      raise argument_exception("name", "Наименование не может быть пустым.")

    if len(normalized_value) > 50:
      raise argument_exception(
          "name", "Длина наименования не должна превышать 50 символов."
      )

    self.__name = normalized_value

  def __eq__(self, other: object) -> bool:
    # Сравнение моделей по уникальному коду
    if not isinstance(other, base_model):
      return False
    return self.unique_code == other.unique_code