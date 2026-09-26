from Src.Core.abstract_model import base_model
from Src.Core.exceptions import argument_exception
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.range_model import range_model


class nomenclature_model(base_model):
  # Номенклатура: короткое имя (до 50 симв), полное имя (до 255 симв), группа и мера
  __full_name: str = ""
  __group: nomenclature_group_model
  __range: range_model

  def __init__(
      self,
      name: str,
      full_name: str,
      group: nomenclature_group_model,
      range_unit: range_model,
  ) -> None:
    super().__init__()
    self.name = name
    self.full_name = full_name
    self.group = group
    self.range = range_unit

  @property
  def full_name(self) -> str:
    # Полное наименование товара/сырья
    return self.__full_name

  @full_name.setter
  def full_name(self, value: str) -> None:
    # Проверка строки, непустоты и ограничения в 255 символов
    if not isinstance(value, str):
      raise argument_exception(
          "full_name", "Полное наименование должно быть строкой."
      )
    normalized_value = value.strip()
    if not normalized_value:
      raise argument_exception(
          "full_name", "Полное наименование не может быть пустым."
      )
    if len(normalized_value) > 255:
      raise argument_exception(
          "full_name",
          "Длина полного наименования не должна превышать 255 символов.",
      )
    self.__full_name = normalized_value

  @property
  def group(self) -> nomenclature_group_model:
    # Группа к которой относится товар
    return self.__group

  @group.setter
  def group(self, value: nomenclature_group_model) -> None:
    # Проверка принадлежности к типу nomenclature_group_model
    if not isinstance(value, nomenclature_group_model):
      raise argument_exception(
          "group", "Группа должна быть объектом nomenclature_group_model."
      )
    self.__group = value

  @property
  def range(self) -> range_model:
    # Единица измерения позиции
    return self.__range

  @range.setter
  def range(self, value: range_model) -> None:
    # Проверка принадлежности к типу range_model
    if not isinstance(value, range_model):
      raise argument_exception(
          "range", "Единица измерения должна быть объектом range_model."
      )
    self.__range = value