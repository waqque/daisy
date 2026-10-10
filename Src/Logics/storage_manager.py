from typing import Optional
from Src.Core.abstract_manager import abstract_manager
from Src.Core.abstract_model import base_model
from Src.Core.exceptions import argument_exception, operation_exception
from Src.Logics.settings_manager import settings_manager
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.organization_model import organization_model
from Src.Models.range_model import range_model
from Src.Models.recipe_model import recipe_model
from Src.Models.recipe_row_model import recipe_row_model
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
        "recipes": recipe_model,
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
            "recipes": [],
        }

    def clear(self) -> None:
        # Очистка всех списков репозитория
        self.__data = {
            "ranges": [],
            "groups": [],
            "nomenclatures": [],
            "storages": [],
            "organizations": [],
            "recipes": [],
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

        # Бизнес-правило "1 блюдо - 1 техкарта"
        if key == "recipes" and hasattr(entity, "dish"):
            for item in self.__data[key]:
                if hasattr(item, "dish") and item.dish == entity.dish:
                    raise operation_exception(
                        f"Технологическая карта для блюда '{entity.dish.name}' уже существует."
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
        # Формирование первичных данных (seed data) при первом старте системы с использованием фабричных методов
        self.clear()

        # 1. Единицы измерения (фабричные методы)
        g_unit = range_model.create_gram("грамм")
        kg_unit = range_model.create_kilogram("кг")
        pcs_unit = range_model("шт", 1.0)
        for unit in (g_unit, kg_unit, pcs_unit):
            self.add_entity("ranges", unit)

        # 2. Группы номенклатуры (фабричные методы)
        group_raw = nomenclature_group_model.create("Сырье")
        group_dairy = nomenclature_group_model.create("Молочная продукция")
        group_pack = nomenclature_group_model.create("Упаковка")
        for group in (group_raw, group_dairy, group_pack):
            self.add_entity("groups", group)

        # 3. Номенклатура (сырье, упаковка и готовое блюдо, согласованы с рецептом ТТК)
        sugar = nomenclature_model.create("Сахар", "Сахар белый ГОСТ", group_raw, kg_unit)
        milk = nomenclature_model.create(
            "Молоко 3.2%", "Молоко пастеризованное 3.2%", group_dairy, g_unit
        )
        flour = nomenclature_model.create("Мука", "Мука пшеничная в/с", group_raw, g_unit)
        egg = nomenclature_model.create("Яйцо", "Яйцо куриное", group_raw, pcs_unit)
        salt = nomenclature_model.create("Соль", "Соль поваренная", group_raw, g_unit)
        oil = nomenclature_model.create(
            "Масло растительное", "Масло растительное рафинированное", group_raw, g_unit
        )
        box = nomenclature_model.create(
            "Контейнер", "Контейнер пищевой картонный для блинчиков", group_pack, pcs_unit
        )
        pancakes_dish = nomenclature_model.create(
            "Блинчики", "Блинчики классические (порция 2 шт.)", group_dairy, pcs_unit
        )
        for nom in (sugar, milk, flour, egg, salt, oil, box, pancakes_dish):
            self.add_entity("nomenclatures", nom)

        # 4. Склады (фабричные методы)
        main_storage = storage_model.create("Главный склад")
        cold_storage = storage_model.create("Холодильная камера")
        for st in (main_storage, cold_storage):
            self.add_entity("storages", st)

        # 5. Организация (композиция из настроек или дефолтная модель через фабричный метод)
        if settings is None:
            manager = settings_manager()
            settings = manager.settings

        if settings is not None and settings.organization is not None:
            self.add_entity("organizations", settings.organization)
        else:
            org = organization_model.create(
                name="ООО Ромашка",
                inn="7701234567",
                bic="044525225",
                account="40702810938000012345",
                ownership_form="ООО",
            )
            self.add_entity("organizations", org)

        # 6. Технологические карты (1 блюдо - 1 техкарта, рецепт с упаковкой по Docs/Recipe.md)
        row_milk = recipe_row_model.create(milk, 100.0, 100.0)
        row_flour = recipe_row_model.create(flour, 50.0, 50.0)
        row_egg = recipe_row_model.create(egg, 1.0, 1.0)
        row_sugar = recipe_row_model.create(sugar, 10.0, 10.0)
        row_salt = recipe_row_model.create(salt, 2.0, 2.0)
        row_oil = recipe_row_model.create(oil, 10.0, 10.0)
        row_box = recipe_row_model.create(box, 15.0, 0.0)

        pancakes_recipe = recipe_model.create(
            name="Блинчики классические",
            dish=pancakes_dish,
            rows=[row_milk, row_flour, row_egg, row_sugar, row_salt, row_oil, row_box],
        )
        self.add_entity("recipes", pancakes_recipe)

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

    @property
    def recipes(self) -> list:
        # Копия списка технологических карт (рецептов)
        return list(self.__data["recipes"])