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

    def load(self, file_name: str = "") -> bool:
        # Инициализация хранилища с загрузкой настроек из файла (Liskov Substitution Principle)
        manager = settings_manager()
        manager.load(file_name)
        self.start(manager.settings)
        return self._is_loaded

    def init_data(self, settings: Optional[settings_model] = None) -> None:
        # Формирование первичных данных (делегирование seeder в соответствии с SRP)
        from Src.Logics.storage_seeder import storage_seeder

        seeder = storage_seeder()
        seeder.seed(self, settings)


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

    __type_aliases = {
        "nomenclatures": "nomenclatures",
        "nomenclature": "nomenclatures",
        "номенклатура": "nomenclatures",
        "ranges": "ranges",
        "range": "ranges",
        "единица измерения": "ranges",
        "единица_измерения": "ranges",
        "recipes": "recipes",
        "recipe": "recipes",
        "рецепт": "recipes",
        "groups": "groups",
        "group": "groups",
        "группа": "groups",
        "storages": "storages",
        "storage": "storages",
        "склад": "storages",
        "organizations": "organizations",
        "organization": "organizations",
        "организация": "organizations",
    }

    def is_valid_type(self, entity_type: str) -> bool:
        # Проверка поддержки типа сущности
        norm_type = str(entity_type).lower().strip()
        return norm_type in self.__type_aliases

    def get_by_code(self, entity_type: str, code: str) -> Optional[base_model]:
        # Поиск сущности по типу коллекции и уникальному коду (или наименованию)
        if not self._is_loaded:
            self.start()

        norm_type = str(entity_type).lower().strip()
        key = self.__type_aliases.get(norm_type)
        if not key or key not in self.__data:
            return None

        c = str(code).strip().lower()
        for item in self.__data[key]:
            if str(item.unique_code).lower() == c or str(item.id).lower() == c or str(item.name).strip().lower() == c:
                return item

        return None

    def get_entity(self, entity_type: str, entity_code: str):
        # Поиск сущности по типу и уникальному коду или наименованию для REST API
        if not self._is_loaded:
            self.start()

        norm_type = str(entity_type).lower().strip()
        key = self.__type_aliases.get(norm_type)
        if not key or key not in self.__data:
            return None, f"Неподдерживаемый тип сущности: {entity_type}", 400

        c = str(entity_code).strip()
        for item in self.__data[key]:
            if (
                str(item.id).lower() == c.lower()
                or str(item.unique_code).lower() == c.lower()
                or item.name.lower() == c.lower()
            ):
                return item, None, 200

        return None, f"Сущность типа '{entity_type}' с кодом '{entity_code}' не найдена.", 404