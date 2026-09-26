import pytest
from Src.Core.exceptions import argument_exception
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model


# Успешное создание номенклатуры со всеми полями
def test_nomenclature_model_init_success():
  group = nomenclature_group_model("Бакалея")
  unit = range_model("кг", 1000.0)
  item = nomenclature_model(
      name="Сахар", full_name="Сахар-песок ГОСТ", group=group, range_unit=unit
  )
  assert item.name == "Сахар"
  assert item.full_name == "Сахар-песок ГОСТ"
  assert item.group == group
  assert item.range == unit


# Граничное значение: имя ровно 50 символов
def test_nomenclature_model_name_exact_50_chars_success():
  group = nomenclature_group_model("Тест")
  unit = range_model("шт", 1.0)
  name_50 = "N" * 50
  item = nomenclature_model(name_50, "Полное имя", group, unit)
  assert item.name == name_50


# Ошибка: краткое имя длиннее 50 символов
def test_nomenclature_model_name_51_chars_raises_exception():
  group = nomenclature_group_model("Тест")
  unit = range_model("шт", 1.0)
  with pytest.raises(argument_exception):
    nomenclature_model("N" * 51, "Полное имя", group, unit)


# Граничное значение: полное имя ровно 255 символов
def test_nomenclature_model_full_name_exact_255_chars_success():
  group = nomenclature_group_model("Тест")
  unit = range_model("шт", 1.0)
  full_255 = "F" * 255
  item = nomenclature_model("Короткое", full_255, group, unit)
  assert item.full_name == full_255


# Ошибка: полное имя длиннее 255 символов
def test_nomenclature_model_full_name_256_chars_raises_exception():
  group = nomenclature_group_model("Тест")
  unit = range_model("шт", 1.0)
  with pytest.raises(argument_exception):
    nomenclature_model("Короткое", "F" * 256, group, unit)


# Ошибка: пустое полное имя
def test_nomenclature_model_empty_full_name_raises_exception():
  group = nomenclature_group_model("Тест")
  unit = range_model("шт", 1.0)
  with pytest.raises(argument_exception):
    nomenclature_model("Короткое", "   ", group, unit)


# Ошибка: полное имя не строка
def test_nomenclature_model_non_string_full_name_raises_exception():
  group = nomenclature_group_model("Тест")
  unit = range_model("шт", 1.0)
  with pytest.raises(argument_exception):
    nomenclature_model("Короткое", 12345, group, unit)


# Ошибка: вместо группы передан некорректный объект
def test_nomenclature_model_invalid_group_raises_exception():
  unit = range_model("шт", 1.0)
  with pytest.raises(argument_exception):
    nomenclature_model("Короткое", "Полное", "не группа", unit)


# Ошибка: вместо единицы измерения передан некорректный объект
def test_nomenclature_model_invalid_range_raises_exception():
  group = nomenclature_group_model("Тест")
  with pytest.raises(argument_exception):
    nomenclature_model("Короткое", "Полное", group, "не единица")