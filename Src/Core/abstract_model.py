from abc import ABC
import uuid
from Src.Core.exceptions import argument_exception


class base_model(ABC):
  # Базовый абстрактный класс для всех сущностей
  __name: str = ""
  __id: str = ""

  def __init__(self) -> None:
    # При создании сразу генерируем уникальный строковый UUID
    self.__id = str(uuid.uuid4())

  @property
  def id(self) -> str:
    # Получение уникального идентификатора
    return self.__id

  @id.setter
  def id(self, value: str) -> None:
    # Валидация и установка уникального идентификатора
    if not isinstance(value, str):
      raise argument_exception(
          "id", "Уникальный код должен быть строкой."
      )

    normalized_value = value.strip()
    if not normalized_value:
      raise argument_exception(
          "id", "Уникальный код не может быть пустым."
      )

    self.__id = normalized_value

  @property
  def unique_code(self) -> str:
    # Синоним к id для обратной совместимости
    return self.id

  @unique_code.setter
  def unique_code(self, value: str) -> None:
    # Установка id через синоним unique_code
    self.id = value

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
    # Сравнение моделей по уникальному идентификатору
    if not isinstance(other, base_model):
      return False
    return self.id == other.id

  def __hash__(self) -> int:
    # Хеширование модели по уникальному идентификатору
    return hash(self.id)