from Src.Core.abstract_manager import abstract_manager
from Src.Core.abstract_model import base_model
from Src.Core.exceptions import argument_exception
from Src.Logics.settings_manager import settings_manager
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.organization_model import organization_model
from Src.Models.range_model import range_model
from Src.Models.storage_model import storage_model


class storage_manager(abstract_manager):
  # словарь сущностей с поддержкой уникальности и первичного наполнения
  __data: dict = {}

  def __new__(cls):
    # Обеспечение единственного экземпляра класса
    if not hasattr(cls, "instance"):
      cls.instance = super(storage_manager, cls).__new__(cls)
      cls.instance.clear()
      cls.instance.__load_from_settings()
    return cls.instance

  def clear(self) -> None:
    # Очистка всех списков репозитория
    self.__data = {
        "ranges": [],
        "groups": [],
        "nomenclatures": [],
        "storages": [],
        "organizations": [],
    }

  def __load_from_settings(self) -> None:
    # Проверка флага первого старта из менеджера настроек
    manager = settings_manager()
    if not manager.is_loaded:
      manager.load()

    if manager.settings and manager.settings.is_first_start:
      self.init_data()

  def add_entity(self, key: str, entity: base_model) -> None:
    # Добавление элемента с сохранением уникальности по идентификатору
    if key not in self.__data:
      raise argument_exception("key", f"Неизвестная коллекция данных: {key}")
    if not isinstance(entity, base_model):
      raise argument_exception(
          "entity", "Элемент должен быть наследником base_model."
      )

    # Проверка на дублирование по unique_code
    for item in self.__data[key]:
      if item == entity:
        return

    self.__data[key].append(entity)

  def convert(self, source_data: dict) -> None:
    # Заполнение хранилища из словаря доменных сущностей
    if not isinstance(source_data, dict):
      raise argument_exception(
          "source_data", "Входные данные должны быть словарем."
      )

    for key, items in source_data.items():
      if key in self.__data and isinstance(items, list):
        for item in items:
          if isinstance(item, base_model):
            self.add_entity(key, item)

  def init_data(self) -> None:
    # Формирование первичных данных при первом старте
    self.clear()

    # 1. Единицы измерения
    g_unit = range_model("грамм", 1.0)
    kg_unit = range_model("кг", 1000.0, g_unit)
    pcs_unit = range_model("шт", 1.0)
    for unit in (g_unit, kg_unit, pcs_unit):
      self.add_entity("ranges", unit)

    # 2. Группы номенклатуры
    group_raw = nomenclature_group_model("Сырье")
    group_dairy = nomenclature_group_model("Молочная продукция")
    for group in (group_raw, group_dairy):
      self.add_entity("groups", group)

    # 3. Номенклатура
    sugar = nomenclature_model("Сахар", "Сахар белый ГОСТ", group_raw, kg_unit)
    milk = nomenclature_model(
        "Молоко 3.2%", "Молоко пастеризованное", group_dairy, pcs_unit
    )
    for nom in (sugar, milk):
      self.add_entity("nomenclatures", nom)

    # 4. Склады
    main_storage = storage_model("Главный склад")
    cold_storage = storage_model("Холодильная камера")
    for st in (main_storage, cold_storage):
      self.add_entity("storages", st)

    # 5. Организация
    manager = settings_manager()
    if manager.settings is not None:
      self.add_entity("organizations", manager.settings)
    else:
      org = organization_model(
          name="ООО Ромашка",
          inn="7701234567",
          bic="044525225",
          account="40702810938000012345",
          ownership_form="ООО",
      )
      self.add_entity("organizations", org)

  @property
  def data(self) -> dict:
    return self.__data

  @property
  def ranges(self) -> list:
    return self.__data["ranges"]

  @property
  def groups(self) -> list:
    return self.__data["groups"]

  @property
  def nomenclatures(self) -> list:
    return self.__data["nomenclatures"]

  @property
  def storages(self) -> list:
    return self.__data["storages"]

  @property
  def organizations(self) -> list:
    return self.__data["organizations"]