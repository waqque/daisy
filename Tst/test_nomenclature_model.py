import pytest
from Src.Core.exceptions import argument_exception
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model


# 1. Успешное создание номенклатуры со всеми полями
def test_nomenclature_model_init_success():
    # Подготовка
    group = nomenclature_group_model("Бакалея")
    unit = range_model("кг", 1000.0)

    # Действие
    item = nomenclature_model(
        name="Сахар", full_name="Сахар-песок ГОСТ", group=group, range_unit=unit
    )

    # Проверка
    assert item.name == "Сахар"
    assert item.full_name == "Сахар-песок ГОСТ"
    assert item.group == group
    assert item.range == unit


# 2. Граничное значение: имя ровно 50 символов
def test_nomenclature_model_name_exact_50_chars_success():
    # Подготовка
    group = nomenclature_group_model("Тест")
    unit = range_model("шт", 1.0)
    name_50 = "N" * 50

    # Действие
    item = nomenclature_model(name_50, "Полное имя", group, unit)

    # Проверка
    assert item.name == name_50


# 3. Ошибка: краткое имя длиннее 50 символов
def test_nomenclature_model_name_51_chars_raises_exception():
    # Подготовка
    group = nomenclature_group_model("Тест")
    unit = range_model("шт", 1.0)
    long_name = "N" * 51

    # Действие и проверка
    with pytest.raises(argument_exception):
        nomenclature_model(long_name, "Полное имя", group, unit)


# 4. Граничное значение: полное имя ровно 255 символов
def test_nomenclature_model_full_name_exact_255_chars_success():
    # Подготовка
    group = nomenclature_group_model("Тест")
    unit = range_model("шт", 1.0)
    full_255 = "F" * 255

    # Действие
    item = nomenclature_model("Короткое", full_255, group, unit)

    # Проверка
    assert item.full_name == full_255


# 5. Ошибка: полное имя длиннее 255 символов
def test_nomenclature_model_full_name_256_chars_raises_exception():
    # Подготовка
    group = nomenclature_group_model("Тест")
    unit = range_model("шт", 1.0)
    long_full_name = "F" * 256

    # Действие и проверка
    with pytest.raises(argument_exception):
        nomenclature_model("Короткое", long_full_name, group, unit)


# 6. Ошибка: пустое полное имя
def test_nomenclature_model_empty_full_name_raises_exception():
    # Подготовка
    group = nomenclature_group_model("Тест")
    unit = range_model("шт", 1.0)
    empty_full_name = "   "

    # Действие и проверка
    with pytest.raises(argument_exception):
        nomenclature_model("Короткое", empty_full_name, group, unit)


# 7. Ошибка: полное имя не строка
def test_nomenclature_model_non_string_full_name_raises_exception():
    # Подготовка
    group = nomenclature_group_model("Тест")
    unit = range_model("шт", 1.0)
    non_string_full_name = 12345

    # Действие и проверка
    with pytest.raises(argument_exception):
        nomenclature_model("Короткое", non_string_full_name, group, unit)


# 8. Ошибка: вместо группы передан некорректный объект
def test_nomenclature_model_invalid_group_raises_exception():
    # Подготовка
    unit = range_model("шт", 1.0)
    invalid_group = "не группа"

    # Действие и проверка
    with pytest.raises(argument_exception):
        nomenclature_model("Короткое", "Полное", invalid_group, unit)


# 9. Ошибка: вместо единицы измерения передан некорректный объект
def test_nomenclature_model_invalid_range_raises_exception():
    # Подготовка
    group = nomenclature_group_model("Тест")
    invalid_range = "не единица"

    # Действие и проверка
    with pytest.raises(argument_exception):
        nomenclature_model("Короткое", "Полное", group, invalid_range)