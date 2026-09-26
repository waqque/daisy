import pytest
from Src.Core.exceptions import argument_exception
from Src.Models.storage_model import storage_model


# Успешное создание склада
def test_storage_model_init_success():
  storage = storage_model("Основной склад")
  assert storage.name == "Основной склад"
  assert storage.id != ""


# Смена имени склада через сеттер
def test_storage_model_change_name_success():
  storage = storage_model("Склад 1")
  storage.name = "Холодильник мяса"
  assert storage.name == "Холодильник мяса"


# Ошибка: пустое имя склада
def test_storage_model_empty_name_raises_exception():
  with pytest.raises(argument_exception):
    storage_model("   ")


# Ошибка: склад с именем длиннее 50 символов
def test_storage_model_name_too_long_raises_exception():
  with pytest.raises(argument_exception):
    storage_model("С" * 51)