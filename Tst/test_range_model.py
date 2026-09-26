import pytest
from Src.Core.exceptions import argument_exception
from Src.Models.range_model import range_model


# Успешное создание базовой единицы
def test_range_model_init_base_unit_success():
  unit = range_model("грамм", 1.0)
  assert unit.name == "грамм"
  assert unit.conversion_factor == 1.0
  assert unit.base_range is None
  assert unit.id != ""


# Успешное создание производной единицы с коэффициентом
def test_range_model_init_derived_unit_success():
  base = range_model("грамм", 1.0)
  kg = range_model("кг", 1000.0, base)
  assert kg.name == "кг"
  assert kg.conversion_factor == 1000.0
  assert kg.base_range == base


# Точный пересчет в базовую единицу
def test_range_model_to_base_calculation():
  base = range_model("грамм", 1.0)
  kg = range_model("кг", 1000.0, base)
  assert kg.to_base(2.5) == 2500.0
  assert kg.to_base(0.1) == pytest.approx(100.0)


# Пересчет базовой единицы самой в себя
def test_range_model_to_base_self():
  base = range_model("грамм", 1.0)
  assert base.to_base(500) == 500.0


# Сеттер коэффициента: смена значения на корректное
def test_range_model_conversion_factor_setter_success():
  unit = range_model("шт", 1.0)
  unit.conversion_factor = 12.0
  assert unit.conversion_factor == 12.0


# Ошибка: коэффициент равен нулю
def test_range_model_zero_factor_raises_exception():
  with pytest.raises(argument_exception):
    range_model("кг", 0.0)


# Ошибка: отрицательный коэффициент
def test_range_model_negative_factor_raises_exception():
  with pytest.raises(argument_exception):
    range_model("кг", -5.0)


# Ошибка: коэффициент не число
def test_range_model_string_factor_raises_exception():
  with pytest.raises(argument_exception):
    range_model("кг", "тысяча")


# Ошибка: базовая единица не является range_model
def test_range_model_invalid_base_range_type_raises_exception():
  with pytest.raises(argument_exception):
    range_model("кг", 1000.0, base_range="не объект")


# Ошибка: пересчет нечислового количества
def test_range_model_to_base_invalid_amount_raises_exception():
  unit = range_model("кг", 1000.0)
  with pytest.raises(argument_exception):
    unit.to_base("два килограмма")