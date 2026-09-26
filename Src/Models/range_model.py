from typing import Optional
from Src.Core.abstract_model import base_model
from Src.Core.exceptions import argument_exception


class range_model(base_model):
  # Единица измерения с коэффициентом пересчета и базовой мерой
  __conversion_factor: float = 1.0
  __base_range: Optional["range_model"] = None

  def __init__(
      self,
      name: str,
      conversion_factor: float = 1.0,
      base_range: Optional["range_model"] = None,
  ) -> None:
    super().__init__()
    self.name = name
    self.conversion_factor = conversion_factor
    self.base_range = base_range

  @property
  def conversion_factor(self) -> float:
    # Возвращаем числовой коэффициент
    return self.__conversion_factor

  @conversion_factor.setter
  def conversion_factor(self, value: float) -> None:
    # Коэффициент должен быть числом больше нуля
    if not isinstance(value, (int, float)):
      raise argument_exception(
          "conversion_factor", "Коэффициент пересчета должен быть числом."
      )
    if value <= 0:
      raise argument_exception(
          "conversion_factor", "Коэффициент пересчета должен быть больше нуля."
      )
    self.__conversion_factor = float(value)

  @property
  def base_range(self) -> Optional["range_model"]:
    # Базовая единица (для кг базой будет грамм)
    return self.__base_range

  @base_range.setter
  def base_range(self, value: Optional["range_model"]) -> None:
    # Проверяем, что передали либо range_model, либо None
    if value is not None and not isinstance(value, range_model):
      raise argument_exception(
          "base_range", "Базовая единица должна быть объектом range_model."
      )
    self.__base_range = value

  def to_base(self, amount: float) -> float:
    # Пересчет текущего количества в базовую единицу
    if not isinstance(amount, (int, float)):
      raise argument_exception(
          "amount", "Количество для пересчета должно быть числом."
      )
    return float(amount) * self.__conversion_factor