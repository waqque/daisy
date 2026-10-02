import pytest
from Src.Core.exceptions import argument_exception
from Src.Models.storage_model import storage_model


# 1. Успешное создание склада
def test_storage_model_init_success():
    # Подготовка
    storage_name = "Основной склад"

    # Действие
    storage = storage_model(storage_name)

    # Проверка
    assert storage.name == storage_name
    assert storage.id != ""


# 2. Смена имени склада через сеттер
def test_storage_model_change_name_success():
    # Подготовка
    storage = storage_model("Склад 1")
    new_name = "Холодильник мяса"

    # Действие
    storage.name = new_name

    # Проверка
    assert storage.name == new_name


# 3. Ошибка: пустое имя склада
def test_storage_model_empty_name_raises_exception():
    # Подготовка
    empty_name = "   "

    # Действие и проверка
    with pytest.raises(argument_exception):
        storage_model(empty_name)


# 4. Ошибка: склад с именем длиннее 50 символов
def test_storage_model_name_too_long_raises_exception():
    # Подготовка
    long_name = "С" * 51

    # Действие и проверка
    with pytest.raises(argument_exception):
        storage_model(long_name)