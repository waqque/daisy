import importlib
import inspect
import json
import os
from typing import Any, Dict, List, Optional, Type, Union, get_args, get_origin, ForwardRef

from Src.Core.abstract_deserialize_factory import abstract_deserialize_factory
from Src.Core.abstract_model import base_model
from Src.Core.exceptions import argument_exception


class deserialize_factory(abstract_deserialize_factory):
    # Фабрика создания объектов моделей из словарей и JSON файлов

    _instances: Dict[str, base_model]

    def __init__(self) -> None:
        # Словарь созданных объектов по их id для исключения дублирования
        self._instances = {}

    @classmethod
    def _get_models(cls) -> Dict[str, Type]:
        # Сбор всех классов моделей через рефлексию
        models_dir = os.path.join(os.path.dirname(__file__), "..", "Models")
        discovered: Dict[str, Type] = {}
        if os.path.exists(models_dir):
            for file_name in os.listdir(models_dir):
                if file_name.endswith(".py") and not file_name.startswith("__"):
                    module_name = file_name[:-3]
                    mod = importlib.import_module(f"Src.Models.{module_name}")
                    for attr_name, attr_val in inspect.getmembers(mod, inspect.isclass):
                        if attr_val.__module__ == mod.__name__ and attr_name.endswith("_model"):
                            discovered[attr_name] = attr_val

        def get_all_subclasses(c: Type[base_model]) -> set:
            res = set(c.__subclasses__())
            for sc in list(res):
                res.update(get_all_subclasses(sc))
            return res

        for m in get_all_subclasses(base_model):
            discovered[m.__name__] = m

        return discovered

    @property
    def models(self) -> Dict[str, Type[base_model]]:
        # Словарь доступных классов моделей по их имени
        return self._get_models()

    def clear_cache(self) -> None:
        # Очистить кэш созданных объектов
        self._instances.clear()

    @property
    def instances(self) -> Dict[str, base_model]:
        # Получить копию словаря созданных объектов
        return dict(self._instances)

    def deserialize(self, data: Any, target_type: Optional[Any] = None) -> Any:
        # Универсальный метод десериализации любых данных (модель, список или словарь)
        if data is None:
            return None

        # Если передан готовый объект модели, возвращаем его
        if isinstance(data, base_model):
            return data

        # Если передана строка (путь к файлу или JSON-строка)
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

        # Если передан список: десериализуем каждый элемент списка
        if isinstance(data, (list, tuple)):
            return [self.deserialize(item, target_type) for item in data]

        # Входные данные должны быть словарем
        if not isinstance(data, dict):
            raise argument_exception(
                "data",
                f"Входные данные должны быть словарем или JSON, получен {type(data).__name__}.",
            )

        # Проверка кэша по id для уже созданных ранее объектов
        item_id = data.get("id")
        if item_id and isinstance(item_id, str) and item_id in self._instances:
            return self._instances[item_id]

        # Определяем класс модели
        model_cls = self._resolve_model_class(data, target_type)

        # Если это модель, создаем и заполняем её
        if model_cls is not None:
            return self._deserialize_model(data, model_cls)

        # Универсальная обработка контейнеров и словарей: рекурсивно десериализуем значения
        return {key: self.deserialize(val) for key, val in data.items()}

    def deserialize_file(self, file_path: str, target_type: Optional[Any] = None) -> Any:
        # Чтение JSON файла с диска
        if not isinstance(file_path, str) or not file_path.strip():
            raise argument_exception("file_path", "Путь к файлу должен быть непустой строкой.")

        if not os.path.exists(file_path):
            raise argument_exception("file_path", f"Файл не найден: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return self.deserialize(data, target_type)

    def deserialize_storage(self, data: Any, target_storage: Optional[Any] = None) -> Any:
        # Загрузка данных и опциональное наполнение хранилища
        storage_dict = self.deserialize(data)

        if target_storage is not None:
            if hasattr(target_storage, "clear"):
                target_storage.clear()

            # Порядок добавления сущностей в хранилище для сохранения зависимостей
            preferred_order = [
                "ranges",
                "groups",
                "nomenclatures",
                "storages",
                "organizations",
                "recipes",
            ]
            ordered_keys = [k for k in preferred_order if k in storage_dict] + [
                k for k in storage_dict if k not in preferred_order
            ]
            for sec_key in ordered_keys:
                items = storage_dict.get(sec_key, [])
                if isinstance(items, list) and hasattr(target_storage, "add_entity"):
                    for entity in items:
                        target_storage.add_entity(sec_key, entity)

            return target_storage

        return storage_dict

    def _resolve_model_class(self, data: dict, target_type: Optional[Any]) -> Optional[Type]:
        # Определение класса модели по переданному типу или по полю type из словаря
        models = self.models

        # 1. По явно переданному типу целевой модели
        if target_type is not None:
            if inspect.isclass(target_type) and (
                issubclass(target_type, base_model) or target_type.__name__ in models
            ):
                return target_type
            if isinstance(target_type, str):
                normalized = target_type.strip().lower()
                for name, cls in models.items():
                    if name.lower() == normalized or name.lower().replace("_model", "") == normalized:
                        return cls

        # 2. По имени типа из сериализованных данных JSON (поле type)
        type_name = data.get("type")
        if type_name and isinstance(type_name, str):
            if type_name in models:
                return models[type_name]
            for name, cls in models.items():
                if name.lower() == type_name.strip().lower():
                    return cls

        return None

    def _deserialize_model(self, data: dict, model_cls: Type) -> Any:
        # Универсальное создание и заполнение объекта любой модели
        if issubclass(model_cls, base_model):
            instance = model_cls.__new__(model_cls)
            base_model.__init__(instance)
        else:
            instance = model_cls()

        # Инициализация списка строк для рецепта
        if hasattr(model_cls, "add_row"):
            setattr(instance, f"_{model_cls.__name__}__rows", [])

        # Запоминаем id и регистрируем в кэше
        item_id = data.get("id")
        if item_id and issubclass(model_cls, base_model):
            instance.id = str(item_id)
            self._instances[instance.id] = instance

        # Заполнение свойств объекта из данных
        for key, val in data.items():
            if key in ("id", "unique_code", "type"):
                continue

            prop = getattr(model_cls, key, None)
            if not isinstance(prop, property):
                continue

            if val is None:
                if prop.fset is not None:
                    setattr(instance, key, None)
            elif isinstance(val, dict):
                # Для вложенного объекта определяем тип из самого объекта или сигнатуры свойства
                nested_cls = None
                if "type" in val:
                    nested_cls = self.models.get(val["type"])
                if nested_cls is None:
                    nested_cls = self._extract_type_from_property(prop, model_cls)
                nested_obj = self.deserialize(val, target_type=nested_cls)
                if prop.fset is not None:
                    setattr(instance, key, nested_obj)
            elif isinstance(val, (list, tuple)):
                # Для коллекций строк рецепта используем метод add_row
                if hasattr(instance, "add_row"):
                    row_type = self._extract_collection_item_type(instance, "add_row")
                    for item in val:
                        row_obj = self.deserialize(item, target_type=row_type)
                        instance.add_row(row_obj)
            else:
                # Для скалярных значений (числа, строки)
                if prop.fset is not None:
                    setattr(instance, key, val)

        return instance

    def _extract_type_from_property(self, prop: property, owner_cls: Type[base_model]) -> Optional[Type[base_model]]:
        # Определение типа свойства через аннотацию возвращаемого значения геттера
        if not prop.fget:
            return None

        ret = prop.fget.__annotations__.get("return")
        if ret is None:
            return None

        # Разворачивание Optional[...]
        if get_origin(ret) is Union:
            args = [a for a in get_args(ret) if a is not type(None)]
            ret = args[0] if args else None

        # Разворачивание строковых аннотаций ForwardRef
        if isinstance(ret, (str, ForwardRef)):
            ref_name = ret.__forward_arg__ if isinstance(ret, ForwardRef) else ret
            if ref_name in self.models:
                return self.models[ref_name]
            if ref_name == owner_cls.__name__:
                return owner_cls

        if inspect.isclass(ret) and issubclass(ret, base_model):
            return ret

        return None

    def _extract_collection_item_type(self, instance: Any, method_name: str) -> Optional[Type[base_model]]:
        # Определение типа элемента коллекции через аннотацию метода
        method = getattr(instance, method_name, None)
        if not method:
            return None
        sig = inspect.signature(method)
        for param in sig.parameters.values():
            if param.name == "self":
                continue
            ann = param.annotation
            if inspect.isclass(ann) and issubclass(ann, base_model):
                return ann
            if isinstance(ann, str) and ann in self.models:
                return self.models[ann]
        return None
