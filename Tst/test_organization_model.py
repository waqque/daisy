import pytest
from Src.Core.exceptions import argument_exception
from Src.Models.organization_model import organization_model


# Успешное создание организации с 10-значным ИНН (юрлицо)
def test_organization_model_inn_10_digits_success():
  org = organization_model(
      name="ООО Ромашка",
      inn="7701234567",
      bic="044525225",
      account="40702810938000012345",
      ownership_form="ООО",
  )
  assert org.inn == "7701234567"
  assert org.bic == "044525225"
  assert org.account == "40702810938000012345"
  assert org.ownership_form == "ООО"


# Успешное создание организации с 12-значным ИНН (ИП/физлицо)
def test_organization_model_inn_12_digits_success():
  org = organization_model(
      name="ИП Иванов",
      inn="770123456789",
      bic="044525225",
      account="40702810938000012345",
      ownership_form="ИП",
  )
  assert org.inn == "770123456789"


# Ошибка: ИНН содержит буквы
def test_organization_model_inn_letters_raises_exception():
  with pytest.raises(argument_exception):
    organization_model("ООО Тест", "770123456A", "044525225", "4" * 20, "ООО")


# Ошибка: ИНН неверной длины
def test_organization_model_inn_invalid_length_raises_exception():
  with pytest.raises(argument_exception):
    organization_model("ООО Тест", "123456789", "044525225", "4" * 20, "ООО")


# Ошибка: БИК не 9 цифр
def test_organization_model_bic_invalid_length_raises_exception():
  with pytest.raises(argument_exception):
    organization_model("ООО Тест", "10" * 5, "12345", "4" * 20, "ООО")


# Ошибка: БИК содержит не цифры
def test_organization_model_bic_non_digits_raises_exception():
  with pytest.raises(argument_exception):
    organization_model("ООО Тест", "10" * 5, "04452522A", "4" * 20, "ООО")


# Ошибка: счет не 20 цифр
def test_organization_model_account_invalid_length_raises_exception():
  with pytest.raises(argument_exception):
    organization_model("ООО Тест", "10" * 5, "044525225", "4" * 19, "ООО")


# Ошибка: пустая форма собственности
def test_organization_model_empty_ownership_raises_exception():
  with pytest.raises(argument_exception):
    organization_model("ООО Тест", "10" * 5, "044525225", "4" * 20, "   ")