from typing import Optional, Union
from Src.Core.abstract_model import base_model
from Src.Core.exceptions import argument_exception, operation_exception
from Src.Logics.deserialize_factory import deserialize_factory
from Src.Logics.storage_manager import storage_manager
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_model import recipe_model


class storage_service:
    # Сервис управления доменными сущностями в хранилище (CRUD и контроль ссылочной целостности, SRP)
    __storage: storage_manager

    def __init__(self, storage: Optional[storage_manager] = None) -> None:
        # Инициализация сервиса с привязкой к экземпляру хранилища
        self.__storage = storage if storage is not None else storage_manager()

    @property
    def storage(self) -> storage_manager:
        # Доступ к обслуживаемому хранилищу
        return self.__storage

    def _ensure_loaded(self) -> None:
        # Гарантия первичной инициализации хранилища перед выполнением операций
        if not self.__storage.is_loaded:
            self.__storage.start()

    def get_list(self, entity_type: str) -> list:
        # Получение списка всех сущностей указанного типа
        self._ensure_loaded()
        key = self.__storage.resolve_key(entity_type)
        if not key:
            raise argument_exception("entity_type", f"Неподдерживаемый тип сущности: {entity_type}")
        return self.__storage.data.get(key, [])

    def get_entity(self, entity_type: str, entity_code: str):
        # Поиск сущности по типу и уникальному коду или наименованию
        self._ensure_loaded()
        key = self.__storage.resolve_key(entity_type)
        if not key:
            return None, f"Неподдерживаемый тип сущности: {entity_type}", 400

        entity = self.__storage.get_by_code(key, entity_code)
        if entity is not None:
            return entity, None, 200

        return None, f"Сущность типа '{entity_type}' с кодом '{entity_code}' не найдена.", 404

    def create_entity(self, entity_type: str, data: dict) -> base_model:
        # Десериализация и добавление новой сущности в хранилище
        self._ensure_loaded()
        key = self.__storage.resolve_key(entity_type)
        model_cls = self.__storage.get_model_type(entity_type)
        if not key or model_cls is None:
            raise argument_exception("entity_type", f"Неподдерживаемый тип сущности: {entity_type}")

        factory = deserialize_factory()
        entity = factory.deserialize(data, target_type=model_cls)
        self.__storage.add_entity(key, entity)
        return entity

    @staticmethod
    def _is_recipe_dependent(recipe: recipe_model, target_id: str) -> bool:
        # Проверка зависимости рецепта или его строк от целевого идентификатора
        if recipe.dish is not None and recipe.dish.id == target_id:
            return True
        return any(
            (row.nomenclature is not None and row.nomenclature.id == target_id)
            or (row.nested_recipe is not None and row.nested_recipe.id == target_id)
            for row in recipe.rows
        )

    def get_dependencies(self, entity: base_model) -> list:
        # Поиск всех доменных сущностей в хранилище, которые ссылаются на данную сущность
        if not isinstance(entity, base_model):
            return []

        target_id = entity.id
        dependencies = []

        if isinstance(entity, range_model):
            dependencies.extend(
                r for r in self.__storage.ranges
                if r is not entity and r.base_range is not None and r.base_range.id == target_id
            )
            dependencies.extend(
                nom for nom in self.__storage.nomenclatures
                if nom.range is not None and nom.range.id == target_id
            )
        elif isinstance(entity, nomenclature_group_model):
            dependencies.extend(
                nom for nom in self.__storage.nomenclatures
                if nom.group is not None and nom.group.id == target_id
            )
        elif isinstance(entity, (nomenclature_model, recipe_model)):
            dependencies.extend(
                rec for rec in self.__storage.recipes
                if rec is not entity and self._is_recipe_dependent(rec, target_id)
            )

        return dependencies

    def delete_entity(self, key_or_type: str, code_or_id: str) -> None:
        # Удаление сущности с предварительной проверкой целостности и связей
        entity, err_msg, _ = self.get_entity(key_or_type, code_or_id)
        if err_msg or entity is None:
            raise operation_exception(f"Сущность не найдена: {err_msg}")

        key = self.__storage.resolve_key(key_or_type)
        deps = self.get_dependencies(entity)
        if deps:
            dep_names = ", ".join(f"'{d.name}' ({d.type})" for d in deps)
            raise operation_exception(
                f"Невозможно удалить сущность '{entity.name}' ({entity.type}), так как на нее ссылаются: {dep_names}."
            )

        self.__storage.remove_entity(key, entity)

    @staticmethod
    def _update_recipe_rows(rows: list, new_entity: base_model) -> None:
        # Обновление ссылок на номенклатуру или вложенный рецепт в строках техкарты
        for row in rows:
            if row.nomenclature is not None and row.nomenclature.id == new_entity.id:
                row.nomenclature = new_entity
            if row.nested_recipe is not None and row.nested_recipe.id == new_entity.id:
                row.nested_recipe = new_entity

    def _update_single_dependency(self, dep: base_model, new_entity: base_model) -> None:
        # Обновление ссылки в одном зависимом объекте
        if isinstance(dep, range_model):
            if dep.base_range is not None and dep.base_range.id == new_entity.id:
                dep.base_range = new_entity
        elif isinstance(dep, nomenclature_model):
            if dep.group is not None and dep.group.id == new_entity.id:
                dep.group = new_entity
            if dep.range is not None and dep.range.id == new_entity.id:
                dep.range = new_entity
        elif isinstance(dep, recipe_model):
            if dep.dish is not None and dep.dish.id == new_entity.id:
                dep.dish = new_entity
            self._update_recipe_rows(dep.rows, new_entity)

    def _update_references(self, dependencies: list, new_entity: base_model) -> None:
        # Точечное обновление ссылок только в найденных зависимых объектах
        for dep in dependencies:
            self._update_single_dependency(dep, new_entity)

    def update_entity(
        self,
        key_or_type: str,
        code_or_id: str,
        new_data_or_entity: Union[dict, base_model],
    ) -> base_model:
        # Обновление сущности с контролем целостности, связей и неизменности уникального кода
        entity, err_msg, _ = self.get_entity(key_or_type, code_or_id)
        if err_msg or entity is None:
            raise operation_exception(f"Сущность не найдена: {err_msg}")

        key = self.__storage.resolve_key(key_or_type)
        expected_type = self.__storage.get_model_type(key)
        if not key or expected_type is None:
            raise operation_exception(f"Неподдерживаемый тип сущности: {key_or_type}")

        if isinstance(new_data_or_entity, dict):
            req_data = dict(new_data_or_entity)
            if "id" not in req_data and "unique_code" not in req_data:
                req_data["id"] = entity.id
            new_entity = deserialize_factory().deserialize(req_data, target_type=expected_type)
        else:
            new_entity = new_data_or_entity

        if not isinstance(new_entity, expected_type):
            raise argument_exception(
                "new_entity",
                f"Новый объект должен иметь тип {expected_type.__name__}, получен {type(new_entity).__name__}.",
            )

        deps = self.get_dependencies(entity)
        if new_entity.id != entity.id and deps:
            dep_names = ", ".join(f"'{d.name}' ({d.type})" for d in deps)
            raise operation_exception(
                f"Запрещено изменять код (id) сущности '{entity.name}', так как она связана с: {dep_names}."
            )

        self.__storage.replace_entity(key, entity, new_entity)
        self._update_references(deps, new_entity)
        return new_entity
