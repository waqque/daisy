from typing import Dict, Optional, Set, Tuple, Type, Union
from Src.Core.abstract_model import base_model
from Src.Core.exceptions import argument_exception, operation_exception
from Src.Dtos.filter_dto import filter_dto
from Src.Logics.deserialize_factory import deserialize_factory
from Src.Logics.osv_service import osv_service
from Src.Logics.prototype import prototype
from Src.Logics.storage_manager import storage_manager


class storage_service:
    # Сервис CRUD-операций, фильтрации и контроля ссылочной целостности
    __storage: storage_manager
    __id_index: Dict[Tuple[str, str], base_model]
    __reverse_dependency_index: Dict[str, Set[base_model]]
    _storage_version: int

    def __init__(self, storage: Optional[storage_manager] = None) -> None:
        self.__storage = storage if storage is not None else storage_manager()
        self.__id_index = {}
        self.__reverse_dependency_index = {}
        self._storage_version = -1

    @property
    def storage(self) -> storage_manager:
        return self.__storage

    def _ensure_loaded(self) -> None:
        # Если данные еще не загружены или версия хранилища сменилась, обновляем индексы
        if not self.__storage.is_loaded:
            self.__storage.start()
        current_version = getattr(self.__storage, "version", 0)
        if self._storage_version != current_version:
            self._build_indexes()

    def _build_indexes(self) -> None:
        # Перестраиваем словари быстрого поиска и обратных ссылок
        self.__id_index = {}
        self.__reverse_dependency_index = {}

        for key, items in self.__storage.data.items():
            for item in items:
                self._index_entity(item, key)

        self._storage_version = getattr(self.__storage, "version", 0)

    @classmethod
    def _extract_references(cls, source: object, visited_ids: Optional[Set[int]] = None) -> Set[str]:
        # Находим id всех моделей, на которые ссылается объект
        if visited_ids is None:
            visited_ids = set()
        obj_id = id(source)
        if obj_id in visited_ids:
            return set()
        visited_ids.add(obj_id)

        ref_ids: Set[str] = set()
        if not hasattr(source, "__dict__"):
            return ref_ids

        for val in vars(source).values():
            if isinstance(val, base_model):
                ref_ids.add(val.id)
                ref_ids.update(cls._extract_references(val, visited_ids))
            elif isinstance(val, (list, tuple, set)):
                for elem in val:
                    if isinstance(elem, base_model):
                        ref_ids.add(elem.id)
                    ref_ids.update(cls._extract_references(elem, visited_ids))
        return ref_ids

    def _index_entity(self, entity: base_model, key: str) -> None:
        # Добавляем сущность в индекс поиска и записываем, на кого она ссылается
        c_id = str(entity.id).strip().lower()
        c_code = str(entity.unique_code).strip().lower()

        self.__id_index[(key, c_id)] = entity
        self.__id_index[(key, c_code)] = entity
        # У транзакций имена могут совпадать, поэтому по имени их не индексируем
        if key != self.__storage.transaction_key():
            c_name = str(entity.name).strip().lower()
            self.__id_index[(key, c_name)] = entity

        ref_ids = self._extract_references(entity)
        for ref_id in ref_ids:
            if ref_id != entity.id:
                if ref_id not in self.__reverse_dependency_index:
                    self.__reverse_dependency_index[ref_id] = set()
                self.__reverse_dependency_index[ref_id].add(entity)

    def _unindex_entity(self, entity: base_model, key: str) -> None:
        # Убираем удаленную сущность из индексов
        c_id = str(entity.id).strip().lower()
        c_code = str(entity.unique_code).strip().lower()

        self.__id_index.pop((key, c_id), None)
        self.__id_index.pop((key, c_code), None)
        if key != self.__storage.transaction_key():
            c_name = str(entity.name).strip().lower()
            self.__id_index.pop((key, c_name), None)

        ref_ids = self._extract_references(entity)
        for ref_id in ref_ids:
            if ref_id in self.__reverse_dependency_index:
                self.__reverse_dependency_index[ref_id].discard(entity)
                if not self.__reverse_dependency_index[ref_id]:
                    del self.__reverse_dependency_index[ref_id]

        self.__reverse_dependency_index.pop(entity.id, None)

    def resolve_key(self, entity_type: str) -> Optional[str]:
        # Определяем ключ коллекции в хранилище по имени типа или класса модели
        if not isinstance(entity_type, str):
            return None
        allowed = self.__storage.allowed_types
        norm = entity_type.strip().lower()
        if norm in allowed:
            return norm
        if f"{norm}s" in allowed:
            return f"{norm}s"
        for key, model_cls in allowed.items():
            cls_name = model_cls.__name__.lower()
            if norm in (cls_name, cls_name.replace("_model", "")):
                return key
        return None

    def get_model_type(self, entity_type: str) -> Optional[Type[base_model]]:
        key = self.resolve_key(entity_type)
        return self.__storage.allowed_types.get(key) if key else None

    def is_valid_type(self, entity_type: str) -> bool:
        return self.resolve_key(entity_type) is not None

    def get_by_code(self, entity_type: str, code: str) -> Optional[base_model]:
        self._ensure_loaded()
        key = self.resolve_key(entity_type)
        if not key:
            return None

        c = str(code).strip().lower()
        return self.__id_index.get((key, c))

    def get_list(self, entity_type: str) -> list:
        self._ensure_loaded()
        key = self.resolve_key(entity_type)
        if not key:
            raise argument_exception("entity_type", f"Неподдерживаемый тип сущности: {entity_type}")
        return self.__storage.data.get(key, [])

    def get_entity(self, entity_type: str, entity_code: str):
        self._ensure_loaded()
        key = self.resolve_key(entity_type)
        if not key:
            return None, f"Неподдерживаемый тип сущности: {entity_type}", 400

        entity = self.get_by_code(key, entity_code)
        if entity is not None:
            return entity, None, 200

        return None, f"Сущность типа '{entity_type}' с кодом '{entity_code}' не найдена.", 404

    def get_default_recipe(self, recipe_name: Optional[str] = None) -> Optional[base_model]:
        self._ensure_loaded()
        if recipe_name:
            found = self.get_by_code("recipes", recipe_name)
            if found is not None:
                return found
        recipes = self.__storage.recipes
        return recipes[0] if recipes else None

    def create_entity(self, entity_type: str, data: dict) -> base_model:
        self._ensure_loaded()
        key = self.resolve_key(entity_type)
        model_cls = self.get_model_type(entity_type)
        if not key or model_cls is None:
            raise argument_exception("entity_type", f"Неподдерживаемый тип сущности: {entity_type}")

        factory = deserialize_factory()
        entity = factory.deserialize(data, target_type=model_cls)
        self.__storage.add_entity(key, entity)
        self._index_entity(entity, key)
        self._storage_version = getattr(self.__storage, "version", 0)
        return entity

    def get_dependencies(self, entity: base_model) -> list:
        self._ensure_loaded()
        if not isinstance(entity, base_model):
            return []
        deps = self.__reverse_dependency_index.get(entity.id, set())
        return [item for item in deps if item is not entity]

    def delete_entity(self, key_or_type: str, code_or_id: str) -> None:
        entity, err_msg, _ = self.get_entity(key_or_type, code_or_id)
        if err_msg or entity is None:
            raise operation_exception(f"Сущность не найдена: {err_msg}")

        key = self.resolve_key(key_or_type)
        deps = self.get_dependencies(entity)
        if deps:
            dep_names = ", ".join(f"'{d.name}' ({d.type})" for d in deps)
            raise operation_exception(
                f"Невозможно удалить сущность '{entity.name}' ({entity.type}), так как на нее ссылаются: {dep_names}."
            )

        self.__storage.remove_entity(key, entity)
        self._unindex_entity(entity, key)
        self._storage_version = getattr(self.__storage, "version", 0)

    @classmethod
    def _replace_collection_references(cls, collection: Union[list, tuple, set], new_entity: base_model) -> None:
        for elem in collection:
            cls._replace_references_in_object(elem, new_entity)

    @classmethod
    def _replace_references_in_object(cls, source: object, new_entity: base_model) -> None:
        # Обновление ссылок на измененную сущность в атрибутах объекта
        if not hasattr(source, "__dict__"):
            return

        for attr_name, val in list(vars(source).items()):
            if isinstance(val, base_model) and val.id == new_entity.id:
                setattr(source, attr_name, new_entity)
            elif isinstance(val, (list, tuple, set)):
                cls._replace_collection_references(val, new_entity)

    def _update_references(self, dependencies: list, new_entity: base_model) -> None:
        for dep in dependencies:
            self._replace_references_in_object(dep, new_entity)

    def _validate_uniqueness(self, key: str, old_entity: base_model, new_entity: base_model) -> None:
        check_name = key != self.__storage.transaction_key()
        for item in self.__storage.data.get(key, []):
            if item is not old_entity:
                if check_name and item.name.strip().lower() == new_entity.name.strip().lower():
                    raise operation_exception(
                        f"Элемент с наименованием '{new_entity.name}' уже существует в коллекции '{key}'."
                    )
                if item.id == new_entity.id:
                    raise operation_exception(
                        f"Элемент с идентификатором '{new_entity.id}' уже существует в коллекции '{key}'."
                    )

    def update_entity(
        self,
        key_or_type: str,
        code_or_id: str,
        new_data_or_entity: Union[dict, base_model],
    ) -> base_model:
        entity, err_msg, _ = self.get_entity(key_or_type, code_or_id)
        if err_msg or entity is None:
            raise operation_exception(f"Сущность не найдена: {err_msg}")

        key = self.resolve_key(key_or_type)
        expected_type = self.get_model_type(key)
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

        self._validate_uniqueness(key, entity, new_entity)
        self.__storage.replace_entity(key, entity, new_entity)
        self._update_references(deps, new_entity)
        self._build_indexes()
        return new_entity

    def filter_entities(self, entity_type: str, filter: Optional[filter_dto] = None) -> list:
        # Фильтруем выбранную коллекцию через прототип
        self._ensure_loaded()
        items = self.get_list(entity_type)
        proto = prototype(items)
        if filter is not None:
            return proto.clone(filter).data
        return proto.data

    def get_osv(self, filter: Optional[filter_dto] = None) -> list:
        # Формируем ОСВ с учетом переданного фильтра
        self._ensure_loaded()
        return osv_service(self.__storage).build_osv(filter)
