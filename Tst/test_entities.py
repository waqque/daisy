import pytest
from Src.Core.abstract_model import base_model
from Src.Core.exceptions import argument_exception


# Тестовый наследник для проверки абстрактного класса
class test_entity(base_model):
  pass


# 1. Проверяем генерацию непустого идентификатора
def test_base_model_id_not_null():
  entity = test_entity()
  result = entity.id

  assert result != ""
  assert result is not None


# 2. Проверяем, что два объекта получают разные уникальные коды
def test_base_model_unique_codes_are_different():
  entity_1 = test_entity()
  entity_2 = test_entity()

  assert entity_1.unique_code != entity_2.unique_code
  assert entity_1.unique_code != ""
  assert entity_2.unique_code != ""


# 3. Проверяем установку одинакового кода 
def test_base_model_entities_have_same_code():
  entity_1 = test_entity()
  entity_2 = test_entity()
  target_code = "aaa123lol"

  entity_1.unique_code = target_code
  entity_2.unique_code = target_code

  assert entity_1.unique_code == entity_2.unique_code
  assert entity_1.unique_code == target_code
  # Проверяем работу оператора равенства __eq__
  assert entity_1 == entity_2


# 4. Проверяем ошибку при установке пустого наименования
def test_base_model_empty_name_raises_exception():
  entity = test_entity()

  with pytest.raises(argument_exception):
    entity.name = ""


# 5. Проверяем ошибку при установке пустого уникального кода
def test_base_model_empty_code_raises_exception():
  entity = test_entity()

  with pytest.raises(argument_exception):
    entity.unique_code = "   "