from typing import Optional
from Src.Core.abstract_manager import abstract_manager
from Src.Core.abstract_model import base_model
from Src.Core.exceptions import argument_exception, operation_exception
from Src.Logics.settings_manager import settings_manager
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.organization_model import organization_model
from Src.Models.range_model import range_model
from Src.Models.settings_model import settings_model
from Src.Models.storage_model import storage_model


class storage_manager(abstract_manager):
    # Хранилище сущностей с контролем бизнес-уникальности по имени и поддержкой первичного наполнения

    __allowed_types = {
        "ranges": range_model,
        "groups": nomenclature_group_model,
        "nomenclatures": nomenclature_model,
        "storages": storage_model,
        "organizations": organization_model,
    }

    def __new__(cls):
        # Обеспечение единственного экземпляра класса (Singleton)
        if not hasattr(cls, "instance"):
            cls.instance = super(storage_manager, cls).__new__(cls)
            cls.instance.__init_state()
        return cls.instance

    def __init_state(self) -> None:
        # Инициализация состояния экземпляра
        super().__init__()
        self.__data: dict = {
            "ranges": [],
            "groups": [],
            "nomenclatures": [],
            "storages": [],
            "organizations": [],
        }

    def clear(self) -> None:
        # Очистка всех списков репозитория
        self.__data = {
            "ranges": [],
            "groups": [],
            "nomenclatures": [],
            "storages": [],
            "organizations": [],
        }
        self._is_loaded = False

    def start(self, settings: Optional[settings_model] = None) -> None:
        # Явный запуск хранилища с передачей или загрузкой настроек
        if settings is None:
            manager = settings_manager()
            if not manager.is_loaded:
                manager.load()
            settings = manager.settings

        if settings is not None and settings.is_first_start:
            self.init_data(settings)
        else:
            self._is_loaded = True

    def add_entity(self, key: str, entity: base_model) -> None:
        # Добавление элемента с проверкой типа коллекции и бизнес-уникальности по наименованию
        if key not in self.__allowed_types:
            raise argument_exception("key", f"Неизвестная коллекция данных: {key}")

        expected_type = self.__allowed_types[key]
        if not isinstance(entity, expected_type):
            raise argument_exception(
                "entity",
                f"Элемент коллекции '{key}' должен иметь тип {expected_type.__name__}, получен {type(entity).__name__}.",
            )

        # Проверка бизнес-уникальности по наименованию и по уникальному коду
        for item in self.__data[key]:
            if item.unique_code == entity.unique_code or item.name.strip().lower() == entity.name.strip().lower():
                raise operation_exception(
                    f"Элемент с наименованием '{entity.name}' уже существует в коллекции '{key}'."
                )

        self.__data[key].append(entity)

    def convert(self, data: dict) -> None:
        # Заполнение хранилища из словаря доменных сущностей
        if not isinstance(data, dict):
            raise argument_exception(
                "data", "Входные данные должны быть словарем (dict)."
            )

        for key, items in data.items():
            if key in self.__allowed_types and isinstance(items, list):
                for item in items:
                    self.add_entity(key, item)

        self._is_loaded = True

    def init_data(self, settings: Optional[settings_model] = None) -> None:
        # Формирование первичных данных (seed data) при первом старте системы
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

        # 3. Номенклатура (согласована с рецептом ТТК)
        sugar = nomenclature_model("Сахар", "Сахар белый ГОСТ", group_raw, kg_unit)
        milk = nomenclature_model(
            "Молоко 3.2%", "Молоко пастеризованное 3.2%", group_dairy, g_unit
        )
        flour = nomenclature_model("Мука", "Мука пшеничная в/с", group_raw, g_unit)
        egg = nomenclature_model("Яйцо", "Яйцо куриное", group_raw, pcs_unit)
        salt = nomenclature_model("Соль", "Соль поваренная", group_raw, g_unit)
        oil = nomenclature_model(
            "Масло растительное", "Масло растительное рафинированное", group_raw, g_unit
        )
        for nom in (sugar, milk, flour, egg, salt, oil):
            self.add_entity("nomenclatures", nom)

        # 4. Склады
        main_storage = storage_model("Главный склад")
        cold_storage = storage_model("Холодильная камера")
        for st in (main_storage, cold_storage):
            self.add_entity("storages", st)

        # 5. Организация (композиция из настроек или дефолтная модель)
        if settings is None:
            manager = settings_manager()
            settings = manager.settings

        if settings is not None and settings.organization is not None:
            self.add_entity("organizations", settings.organization)
        else:
            org = organization_model(
                name="ООО Ромашка",
                inn="7701234567",
                bic="044525225",
                account="40702810938000012345",
                ownership_form="ООО",
            )
            self.add_entity("organizations", org)

        self._is_loaded = True

    @property
    def data(self) -> dict:
        # Получение копии словаря данных для защиты от несанкционированной модификации
        return {k: list(v) for k, v in self.__data.items()}

    @property
    def ranges(self) -> list:
        # Копия списка единиц измерения
        return list(self.__data["ranges"])

    @property
    def groups(self) -> list:
        # Копия списка групп номенклатуры
        return list(self.__data["groups"])

    @property
    def nomenclatures(self) -> list:
        # Копия списка номенклатуры
        return list(self.__data["nomenclatures"])

    @property
    def storages(self) -> list:
        # Копия списка складов
        return list(self.__data["storages"])

    @property
    def organizations(self) -> list:
        # Копия списка организаций
        return list(self.__data["organizations"])