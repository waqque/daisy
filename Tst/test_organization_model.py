import pytest
from Src.Core.exceptions import argument_exception
from Src.Models.organization_model import organization_model


# 1. Успешное создание организации с 10-значным ИНН (юрлицо)
def test_organization_model_inn_10_digits_success():
    # Подготовка
    name = "ООО Ромашка"
    inn = "7701234567"
    bic = "044525225"
    account = "40702810938000012345"
    ownership_form = "ООО"

    # Действие
    org = organization_model(
        name=name,
        inn=inn,
        bic=bic,
        account=account,
        ownership_form=ownership_form,
    )

    # Проверка
    assert org.inn == "7701234567"
    assert org.bic == "044525225"
    assert org.account == "40702810938000012345"
    assert org.ownership_form == "ООО"


# 2. Успешное создание организации с 12-значным ИНН (ИП/физлицо)
def test_organization_model_inn_12_digits_success():
    # Подготовка
    name = "ИП Иванов"
    inn = "770123456789"
    bic = "044525225"
    account = "40702810938000012345"
    ownership_form = "ИП"

    # Действие
    org = organization_model(
        name=name,
        inn=inn,
        bic=bic,
        account=account,
        ownership_form=ownership_form,
    )

    # Проверка
    assert org.inn == "770123456789"


# 3. Ошибка: ИНН содержит буквы
def test_organization_model_inn_letters_raises_exception():
    # Подготовка
    invalid_inn = "770123456A"

    # Действие и проверка
    with pytest.raises(argument_exception):
        organization_model("ООО Тест", invalid_inn, "044525225", "4" * 20, "ООО")


# 4. Ошибка: ИНН неверной длины
def test_organization_model_inn_invalid_length_raises_exception():
    # Подготовка
    invalid_inn = "123456789"

    # Действие и проверка
    with pytest.raises(argument_exception):
        organization_model("ООО Тест", invalid_inn, "044525225", "4" * 20, "ООО")


# 5. Ошибка: БИК не 9 цифр
def test_organization_model_bic_invalid_length_raises_exception():
    # Подготовка
    invalid_bic = "12345"

    # Действие и проверка
    with pytest.raises(argument_exception):
        organization_model("ООО Тест", "10" * 5, invalid_bic, "4" * 20, "ООО")


# 6. Ошибка: БИК содержит не цифры
def test_organization_model_bic_non_digits_raises_exception():
    # Подготовка
    invalid_bic = "04452522A"

    # Действие и проверка
    with pytest.raises(argument_exception):
        organization_model("ООО Тест", "10" * 5, invalid_bic, "4" * 20, "ООО")


# 7. Ошибка: счет не 20 цифр
def test_organization_model_account_invalid_length_raises_exception():
    # Подготовка
    invalid_account = "4" * 19

    # Действие и проверка
    with pytest.raises(argument_exception):
        organization_model("ООО Тест", "10" * 5, "044525225", invalid_account, "ООО")


# 8. Ошибка: пустая форма собственности
def test_organization_model_empty_ownership_raises_exception():
    # Подготовка
    empty_ownership = "   "

    # Действие и проверка
    with pytest.raises(argument_exception):
        organization_model("ООО Тест", "10" * 5, "044525225", "4" * 20, empty_ownership)