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

    def get_dependencies(self, entity: base_model) -> list:
        # Поиск всех доменных сущностей в хранилище, которые ссылаются на данную сущность
        if not isinstance(entity, base_model):
            return []

        dependencies = []
        target_id = entity.id

        # 1. Проверяем единицы измерения (ranges) - на них могут ссылаться другие ranges (base_range)
        for r in self.__data.get("ranges", []):
            if r is not entity and r.base_range is not None and r.base_range.id == target_id:
                dependencies.append(r)

        # 2. Проверяем номенклатуру (nomenclatures) - ссылается на groups и ranges
        for nom in self.__data.get("nomenclatures", []):
            if nom is not entity:
                if nom.group is not None and nom.group.id == target_id:
                    dependencies.append(nom)
                if nom.range is not None and nom.range.id == target_id:
                    dependencies.append(nom)

        # 3. Проверяем рецепты (recipes) - ссылаются на nomenclature (dish) и в строках на nomenclature и nested_recipe
        for rec in self.__data.get("recipes", []):
            if rec is not entity:
                if rec.dish is not None and rec.dish.id == target_id:
                    dependencies.append(rec)
                for row in rec.rows:
                    if row.nomenclature is not None and row.nomenclature.id == target_id:
                        dependencies.append(rec)
                    if row.nested_recipe is not None and row.nested_recipe.id == target_id:
                        dependencies.append(rec)

        return dependencies

    def delete_entity(self, key_or_type: str, code_or_id: str) -> None:
        # Удаление сущности с предварительной проверкой целостности и связей
        entity, err_msg, status_code = self.get_entity(key_or_type, code_or_id)
        if err_msg or entity is None:
            raise operation_exception(f"Сущность не найдена: {err_msg}")

        norm_type = str(key_or_type).lower().strip()
        key = self.__type_aliases.get(norm_type)
        if not key or key not in self.__data:
            raise operation_exception(f"Неподдерживаемый тип сущности: {key_or_type}")

        # Проверка связности: запрещено удалять сущность, если на нее ссылаются другие объекты
        deps = self.get_dependencies(entity)
        if deps:
            dep_names = ", ".join(f"'{d.name}' ({d.type})" for d in deps)
            raise operation_exception(
                f"Невозможно удалить сущность '{entity.name}' ({entity.type}), так как на нее ссылаются: {dep_names}."
            )

        self.__data[key].remove(entity)

    def update_entity(self, key_or_type: str, code_or_id: str, new_entity: base_model) -> None:
        # Обновление сущности с контролем целостности, связей и неизменности уникального кода
        entity, err_msg, status_code = self.get_entity(key_or_type, code_or_id)
        if err_msg or entity is None:
            raise operation_exception(f"Сущность не найдена: {err_msg}")

        norm_type = str(key_or_type).lower().strip()
        key = self.__type_aliases.get(norm_type)
        if not key or key not in self.__data:
            raise operation_exception(f"Неподдерживаемый тип сущности: {key_or_type}")

        expected_type = self.__allowed_types[key]
        if not isinstance(new_entity, expected_type):
            raise argument_exception(
                "new_entity",
                f"Новый объект должен иметь тип {expected_type.__name__}, получен {type(new_entity).__name__}."
            )

        deps = self.get_dependencies(entity)
        # Если сущность связана с другими, запрещено менять её уникальный код (id)
        if new_entity.id != entity.id:
            if deps:
                dep_names = ", ".join(f"'{d.name}' ({d.type})" for d in deps)
                raise operation_exception(
                    f"Запрещено изменять код (id) сущности '{entity.name}', так как она связана с: {dep_names}."
                )

        # Проверка уникальности имени среди остальных объектов коллекции
        for item in self.__data[key]:
            if item is not entity:
                if item.name.strip().lower() == new_entity.name.strip().lower():
                    raise operation_exception(
                        f"Элемент с наименованием '{new_entity.name}' уже существует в коллекции '{key}'."
                    )
                if item.id == new_entity.id:
                    raise operation_exception(
                        f"Элемент с идентификатором '{new_entity.id}' уже существует в коллекции '{key}'."
                    )

        # Замена элемента в коллекции
        idx = self.__data[key].index(entity)
        self.__data[key][idx] = new_entity

        # Обновление ссылок в зависимых объектах для сохранения консистентности графа объектов
        for r in self.__data.get("ranges", []):
            if r.base_range is not None and r.base_range.id == new_entity.id:
                r.base_range = new_entity
        for nom in self.__data.get("nomenclatures", []):
            if nom.group is not None and nom.group.id == new_entity.id:
                nom.group = new_entity
            if nom.range is not None and nom.range.id == new_entity.id:
                nom.range = new_entity
        for rec in self.__data.get("recipes", []):
            if rec.dish is not None and rec.dish.id == new_entity.id:
                rec.dish = new_entity
            for row in rec.rows:
                if row.nomenclature is not None and row.nomenclature.id == new_entity.id:
                    row.nomenclature = new_entity
                if row.nested_recipe is not None and row.nested_recipe.id == new_entity.id:
                    row.nested_recipe = new_entity
