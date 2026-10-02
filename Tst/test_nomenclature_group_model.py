import pytest
from Src.Core.exceptions import argument_exception
from Src.Models.nomenclature_group_model import nomenclature_group_model


# 1. Успешное создание группы
def test_group_model_init_success():
    # Подготовка
    group_name = "Сырье"

    # Действие
    group = nomenclature_group_model(group_name)

    # Проверка
    assert group.name == "Сырье"
    assert len(group.unique_code) > 0


# 2. Смена наименования группы через сеттер
def test_group_model_set_name_success():
    # Подготовка
    group = nomenclature_group_model("Сырье")
    new_name = "Полуфабрикаты"

    # Действие
    group.name = new_name

    # Проверка
    assert group.name == new_name


# 3. Ошибка: пустое имя группы
def test_group_model_empty_name_raises_exception():
    # Подготовка
    empty_name = ""

    # Действие и проверка
    with pytest.raises(argument_exception):
        nomenclature_group_model(empty_name)


# 4. Ошибка: имя группы длиннее 50 символов
def test_group_model_name_too_long_raises_exception():
    # Подготовка
    long_name = "Г" * 51

    # Действие и проверка
    with pytest.raises(argument_exception):
        nomenclature_group_model(long_name)