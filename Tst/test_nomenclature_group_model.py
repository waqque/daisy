import pytest
from Src.Core.exceptions import argument_exception
from Src.Models.nomenclature_group_model import nomenclature_group_model


# Успешное создание группы
def test_group_model_init_success():
  group = nomenclature_group_model("Сырье")
  assert group.name == "Сырье"
  assert len(group.unique_code) > 0


# Смена наименования группы через сеттер
def test_group_model_set_name_success():
  group = nomenclature_group_model("Сырье")
  group.name = "Полуфабрикаты"
  assert group.name == "Полуфабрикаты"


# Ошибка: пустое имя группы
def test_group_model_empty_name_raises_exception():
  with pytest.raises(argument_exception):
    nomenclature_group_model("")


# Ошибка: имя группы длиннее 50 символов
def test_group_model_name_too_long_raises_exception():
  with pytest.raises(argument_exception):
    nomenclature_group_model("Г" * 51)