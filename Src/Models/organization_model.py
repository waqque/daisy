from Src.Core.abstract_model import base_model
from Src.Core.exceptions import argument_exception


class organization_model(base_model):
  # Организация со всеми финансовыми реквизитами
  __inn: str = ""
  __bic: str = ""
  __account: str = ""
  __ownership_form: str = ""

  def __init__(
      self, name: str, inn: str, bic: str, account: str, ownership_form: str
  ) -> None:
    super().__init__()
    self.name = name
    self.inn = inn
    self.bic = bic
    self.account = account
    self.ownership_form = ownership_form

  @property
  def inn(self) -> str:
    # Получение ИНН
    return self.__inn

  @inn.setter
  def inn(self, value: str) -> None:
    # ИНН: строго строка из 10 или 12 цифр
    if not isinstance(value, str):
      raise argument_exception("inn", "ИНН должен быть строкой.")
    cleaned = value.strip()
    if not cleaned.isdigit() or len(cleaned) not in (10, 12):
      raise argument_exception(
          "inn", "ИНН должен содержать ровно 10 или 12 цифр."
      )
    self.__inn = cleaned

  @property
  def bic(self) -> str:
    # Получение БИК банка
    return self.__bic

  @bic.setter
  def bic(self, value: str) -> None:
    # БИК: строка из 9 цифр
    if not isinstance(value, str):
      raise argument_exception("bic", "БИК должен быть строкой.")
    cleaned = value.strip()
    if not cleaned.isdigit() or len(cleaned) != 9:
      raise argument_exception("bic", "БИК должен содержать ровно 9 цифр.")
    self.__bic = cleaned

  @property
  def account(self) -> str:
    # Получение расчетного счета
    return self.__account

  @account.setter
  def account(self, value: str) -> None:
    # Расчетный счет: строго строка из 20 цифр
    if not isinstance(value, str):
      raise argument_exception("account", "Расчетный счет должен быть строкой.")
    cleaned = value.strip()
    if not cleaned.isdigit() or len(cleaned) != 20:
      raise argument_exception(
          "account", "Расчетный счет должен содержать ровно 20 цифр."
      )
    self.__account = cleaned

  @property
  def ownership_form(self) -> str:
    # Получение формы собственности (ООО, ПАО, ИП)
    return self.__ownership_form

  @ownership_form.setter
  def ownership_form(self, value: str) -> None:
    # Форма не должна быть пустой
    if not isinstance(value, str):
      raise argument_exception(
          "ownership_form", "Форма собственности должна быть строкой."
      )
    cleaned = value.strip()
    if not cleaned:
      raise argument_exception(
          "ownership_form", "Форма собственности не может быть пустой."
      )
    self.__ownership_form = cleaned