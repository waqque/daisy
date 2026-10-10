import pytest
from Src.Core.exceptions import argument_exception
from Src.Models.range_model import range_model


# 1. Успешное создание базовой единицы
def test_range_model_init_base_unit_success():
    # Подготовка
    name = "грамм"
    factor = 1.0

    # Действие
    unit = range_model(name, factor)

    # Проверка
    assert unit.name == "грамм"
    assert unit.conversion_factor == 1.0
    assert unit.base_range is None
    assert unit.id != ""


# 2. Успешное создание производной единицы с коэффициентом
def test_range_model_init_derived_unit_success():
    # Подготовка
    base = range_model("грамм", 1.0)

    # Действие
    kg = range_model("кг", 1000.0, base)

    # Проверка
    assert kg.name == "кг"
    assert kg.conversion_factor == 1000.0
    assert kg.base_range == base


# 3. Точный пересчет в базовую единицу
def test_range_model_to_base_calculation():
    # Подготовка
    base = range_model("грамм", 1.0)
    kg = range_model("кг", 1000.0, base)

    # Действие
    result_1 = kg.to_base(2.5)
    result_2 = kg.to_base(0.1)

    # Проверка
    assert result_1 == 2500.0
    assert result_2 == pytest.approx(100.0)


# 4. Пересчет базовой единицы самой в себя
def test_range_model_to_base_self():
    # Подготовка
    base = range_model("грамм", 1.0)

    # Действие
    result = base.to_base(500)

    # Проверка
    assert result == 500.0


# 5. Сеттер коэффициента: смена значения на корректное
def test_range_model_conversion_factor_setter_success():
    # Подготовка
    unit = range_model("шт", 1.0)
    new_factor = 12.0

    # Действие
    unit.conversion_factor = new_factor

    # Проверка
    assert unit.conversion_factor == 12.0


# 6. Ошибка: коэффициент равен нулю
def test_range_model_zero_factor_raises_exception():
    # Подготовка
    zero_factor = 0.0

    # Действие и проверка
    with pytest.raises(argument_exception):
        range_model("кг", zero_factor)


# 7. Ошибка: отрицательный коэффициент
def test_range_model_negative_factor_raises_exception():
    # Подготовка
    negative_factor = -5.0

    # Действие и проверка
    with pytest.raises(argument_exception):
        range_model("кг", negative_factor)


# 8. Ошибка: коэффициент не число
def test_range_model_string_factor_raises_exception():
    # Подготовка
    string_factor = "тысяча"

    # Действие и проверка
    with pytest.raises(argument_exception):
        range_model("кг", string_factor)


# 9. Ошибка: базовая единица не является range_model
def test_range_model_invalid_base_range_type_raises_exception():
    # Подготовка
    invalid_base = "не объект"

    # Действие и проверка
    with pytest.raises(argument_exception):
        range_model("кг", 1000.0, base_range=invalid_base)


# 10. Ошибка: пересчет нечислового количества
def test_range_model_to_base_invalid_amount_raises_exception():
    # Подготовка
    unit = range_model("кг", 1000.0)
    invalid_amount = "два килограмма"

    # Действие и проверка
    with pytest.raises(argument_exception):
        unit.to_base(invalid_amount)


# 11. Многоуровневый пересчет через цепочку базовых единиц
def test_range_model_to_base_multilevel_calculation():
    # Подготовка
    base = range_model("грамм", 1.0)
    kg = range_model("кг", 1000.0, base)
    tonne = range_model("тонна", 1000.0, kg)

    # Действие
    result = tonne.to_base(2.5)

    # Проверка
    assert result == 2_500_000.0


# 12. Проверка фабричного метода создания килограмма по умолчанию
def test_range_model_factory_kilogram_default_success():
    # Действие
    kg = range_model.create_kilogram()

    # Проверка
    assert kg.name == "кг"
    assert kg.conversion_factor == 1000.0
    assert kg.base_range is not None
    assert kg.base_range.name == "грамм"
    assert kg.base_range.conversion_factor == 1.0
    assert kg.to_base(1.5) == 1500.0


# 13. Проверка фабричного метода создания килограмма с кастомным именем
def test_range_model_factory_kilogram_custom_name_success():
    # Действие
    kg = range_model.create_kilogram("килограмм")

    # Проверка
    assert kg.name == "килограмм"
    assert kg.conversion_factor == 1000.0
    assert kg.base_range.name == "грамм"
    assert kg.to_base(2) == 2000.0