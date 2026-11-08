import inspect
import json
import os
from typing import Any, Dict, List, Optional, Type, Union, get_args, get_origin, ForwardRef

from Src.Core.abstract_deserialize_factory import abstract_deserialize_factory
from Src.Core.abstract_model import base_model
from Src.Core.exceptions import argument_exception
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.organization_model import organization_model
from Src.Models.range_model import range_model
from Src.Models.recipe_model import recipe_model
from Src.Models.recipe_row_model import recipe_row_model
from Src.Models.storage_model import storage_model


class deserialize_factory(abstract_deserialize_factory):
    # Фабрика создания объектов моделей из словарей и JSON файлов

    _instances: Dict[str, base_model]

    # Список всех моделей программы
    _models: List[Type[base_model]] = [
        organization_model,
        recipe_model,
        recipe_row_model,
        nomenclature_model,
        range_model,
        storage_model,
        nomenclature_group_model,
    ]

    # Какие модели лежат в каких секциях хранилища
    _storage_sections: Dict[str, Type[base_model]] = {
        "ranges": range_model,
        "groups": nomenclature_group_model,
        "nomenclatures": nomenclature_model,
        "storages": storage_model,
        "organizations": organization_model,
        "recipes": recipe_model,
    }

    def __init__(self) -> None:
        # Словарь созданных объектов по их id (чтобы не дублировать одинаковые объекты в памяти)
        self._instances = {}

    def clear_cache(self) -> None:
        # Очистить память созданных объектов
        self._instances.clear()

    @property
    def instances(self) -> Dict[str, base_model]:
        # Получить копию словаря созданных объектов
        return dict(self._instances)

    def deserialize(self, data: Any, target_type: Optional[Any] = None) -> Any:
        # Главный метод: принимает словарь, список, JSON строку или путь к файлу
        if data is None:
            return None

        # Если нам уже передали готовый объект, просто возвращаем его
        if isinstance(data, base_model):
            return data

        # Если передана строка: читаем файл с диска или разбираем JSON строку
        if isinstance(data, str):
            clean_str = data.strip()
            if os.path.isfile(clean_str):
                return self.deserialize_file(clean_str, target_type)
            try:
                parsed_json = json.loads(clean_str)
                return self.deserialize(parsed_json, target_type)
            except Exception as exc:
                raise argument_exception(
                    "data", f"Не удалось прочитать JSON-строку: {exc}"
                )

        # Если передан список: превращаем каждый элемент списка в объект
        if isinstance(data, (list, tuple)):
            return [self.deserialize(item, target_type) for item in data]

        if not isinstance(data, dict):
            raise argument_exception(
                "data",
                f"Входные данные должны быть словарем или JSON, получен {type(data).__name__}.",
            )

        # Если объект с таким id уже создавался раньше, возвращаем его из памяти
        item_id = data.get("id")
        if item_id and isinstance(item_id, str) and item_id in self._instances:
            return self._instances[item_id]

        # Если переданы данные всего хранилища, загружаем все секции
        if target_type == "storage_dict" or (
            target_type is None and len(set(data.keys()) & set(self._storage_sections.keys())) >= 2
        ):
            return self._deserialize_storage_dict(data)

        # Если класс модели не указан, определяем его по свойствам объекта
        model_cls = self._resolve_model_class(data, target_type)
        if model_cls is None:
            raise argument_exception(
                "target_type",
                f"Не удалось определить класс модели для словаря: {list(data.keys())}",
            )

        # Создаем и заполняем объект модели
        return self._deserialize_model(data, model_cls)

    def deserialize_file(self, file_path: str, target_type: Optional[Any] = None) -> Any:
        # Читаем JSON файл с диска
        if not isinstance(file_path, str) or not file_path.strip():
            raise argument_exception("file_path", "Путь к файлу должен быть непустой строкой.")

        if not os.path.exists(file_path):
            raise argument_exception("file_path", f"Файл не найден: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return self.deserialize(data, target_type)

    def deserialize_storage(self, data: Any, target_storage: Optional[Any] = None) -> Any:
        # Загружаем все данные и при необходимости заполняем хранилище
        storage_dict = self.deserialize(data, target_type="storage_dict")

        if target_storage is not None:
            if hasattr(target_storage, "clear"):
                target_storage.clear()

            # Добавляем данные в порядке: сначала единицы и группы, потом рецепты
            for sec_key in ["ranges", "groups", "nomenclatures", "storages", "organizations", "recipes"]:
                for entity in storage_dict.get(sec_key, []):
                    target_storage.add_entity(sec_key, entity)

            return target_storage

        return storage_dict

    def _resolve_model_class(self, data: dict, target_type: Optional[Any]) -> Optional[Type[base_model]]:
        # Находим подходящий класс модели
        if target_type is not None:
            if isinstance(target_type, str):
                normalized = target_type.strip().lower()
                # Поиск по имени секции хранилища (например, "ranges")
                if normalized in self._storage_sections:
                    return self._storage_sections[normalized]
                # Поиск по имени класса (например, "range_model")
                for m in self._models:
                    if m.__name__.lower() == normalized:
                        return m
            elif inspect.isclass(target_type) and issubclass(target_type, base_model):
                return target_type

        # Сравниваем ключи словаря со свойствами моделей и берем модель с наибольшим совпадением
        data_keys = set(data.keys())

        def get_model_props(cls: Type[base_model]) -> set:
            return {
                name for name, val in inspect.getmembers(cls)
                if isinstance(val, property) and name not in ("id", "unique_code")
            }

        best_model = max(
            self._models,
            key=lambda m: (len(data_keys & get_model_props(m)), len(get_model_props(m)))
        )

        if not (data_keys & get_model_props(best_model)):
            return None

        return best_model

    def _deserialize_model(self, data: dict, model_cls: Type[base_model]) -> base_model:
        # Универсальное создание и заполнение объекта любой модели
        instance = model_cls.__new__(model_cls)
        base_model.__init__(instance)

        # Для рецепта создаем пустой список строк ингредиентов
        if issubclass(model_cls, recipe_model) or model_cls is recipe_model:
            setattr(instance, "_recipe_model__rows", [])

        # Запоминаем id и сохраняем объект в памяти
        item_id = data.get("id")
        if item_id:
            instance.id = str(item_id)
            self._instances[instance.id] = instance

        # Проходим по всем полям словаря и записываем их в свойства объекта
        for key, val in data.items():
            if key in ("id", "unique_code"):
                continue

            # Проверяем, есть ли такое свойство у класса
            prop = getattr(model_cls, key, None)
            if not isinstance(prop, property):
                continue

            if val is None:
                if prop.fset is not None:
                    setattr(instance, key, None)
            elif isinstance(val, dict):
                # Для вложенного объекта узнаем тип из описания свойства и создаем его
                nested_cls = self._extract_type_from_property(prop, model_cls)
                nested_obj = self.deserialize(val, target_type=nested_cls)
                if prop.fset is not None:
                    setattr(instance, key, nested_obj)
            elif isinstance(val, (list, tuple)):
                # Для строк рецепта создаем каждый ингредиент и добавляем через add_row
                if hasattr(instance, "add_row"):
                    for item in val:
                        row_obj = self.deserialize(item, target_type=recipe_row_model)
                        instance.add_row(row_obj)
            else:
                # Для простых значений (числа, строки) просто записываем значение в свойство
                if prop.fset is not None:
                    setattr(instance, key, val)

        return instance

    def _extract_type_from_property(self, prop: property, owner_cls: Type[base_model]) -> Optional[Type[base_model]]:
        # Узнаем тип вложенной модели из подсказки типа в геттере свойства
        if not prop.fget:
            return None

        ret = prop.fget.__annotations__.get("return")
        if ret is None:
            return None

        # Разворачиваем Optional[...]
        if get_origin(ret) is Union:
            args = [a for a in get_args(ret) if a is not type(None)]
            ret = args[0] if args else None

        # Разворачиваем строковые ссылки ForwardRef
        if isinstance(ret, (str, ForwardRef)):
            ref_name = ret.__forward_arg__ if isinstance(ret, ForwardRef) else ret
            for m in self._models:
                if m.__name__ == ref_name:
                    return m
            if ref_name == owner_cls.__name__:
                return owner_cls

        if inspect.isclass(ret) and issubclass(ret, base_model):
            return ret

        return None

    def _deserialize_storage_dict(self, data: dict) -> Dict[str, List[base_model]]:
        # Загружаем каждую секцию хранилища
        result: Dict[str, List[base_model]] = {}
        for sec_key, model_cls in self._storage_sections.items():
            items = data.get(sec_key, [])
            result[sec_key] = [self.deserialize(item, target_type=model_cls) for item in items]
        return result
