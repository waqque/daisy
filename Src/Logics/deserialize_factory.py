import json
import os
from typing import Any, Callable, Dict, List, Optional

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
    # Фабрика, которая превращает словари и JSON обратно в объекты моделей

    _instances: Dict[str, base_model]
    _handlers: Dict[Any, Callable[[dict], Any]]
    _names_map: Dict[str, Any]

    # Таблица сигнатур: какие характерные поля какому классу принадлежат
    _signatures = [
        ({"inn", "bic", "account"}, organization_model),
        ({"dish", "rows"}, recipe_model),
        ({"gross_weight", "net_weight"}, recipe_row_model),
        ({"full_name"}, nomenclature_model),
        ({"conversion_factor", "base_range"}, range_model),
    ]

    def __init__(self) -> None:
        # Словарь созданных объектов по их id (чтобы не создавать дубликаты одного и того же объекта)
        self._instances = {}

        # Таблица соответствия: какому типу модели какая функция создания соответствует
        self._handlers = {
            range_model: self._create_range,
            nomenclature_group_model: self._create_group,
            storage_model: self._create_storage,
            organization_model: self._create_organization,
            nomenclature_model: self._create_nomenclature,
            recipe_row_model: self._create_recipe_row,
            recipe_model: self._create_recipe,
            "storage_dict": self._create_storage_dict,
        }

        # Таблица соответствия строковых названий секций типам моделей
        self._names_map = {
            "ranges": range_model,
            "groups": nomenclature_group_model,
            "nomenclatures": nomenclature_model,
            "storages": storage_model,
            "organizations": organization_model,
            "recipes": recipe_model,
            "recipe_rows": recipe_row_model,
            "storage_dict": "storage_dict",
        }

    def clear_cache(self) -> None:
        # Очистить память ранее созданных объектов
        self._instances.clear()

    @property
    def instances(self) -> Dict[str, base_model]:
        # Посмотреть все сохраненные в памяти объекты
        return dict(self._instances)

    def deserialize(self, data: Any, target_type: Optional[Any] = None) -> Any:
        # Главная точка входа: разбирает входные данные любого вида (словарь, список, строка, файл)
        if data is None:
            return None

        # Если нам уже передали готовую модель, просто возвращаем ее
        if isinstance(data, base_model):
            return data

        # Если передали строку: это либо путь к файлу на диске, либо JSON строка
        if isinstance(data, str):
            clean_str = data.strip()
            if os.path.isfile(clean_str):
                return self.deserialize_file(clean_str, target_type)
            try:
                return self.deserialize(json.loads(clean_str), target_type)
            except Exception as exc:
                raise argument_exception(
                    "data", f"Не удалось прочитать JSON строку: {exc}"
                )

        # Если передан список или кортеж — рекурсивно превращаем каждый элемент в модель
        if isinstance(data, (list, tuple)):
            return [self.deserialize(item, target_type) for item in data]

        if not isinstance(data, dict):
            raise argument_exception(
                "data",
                f"Ожидался словарь или JSON, но получен {type(data).__name__}.",
            )

        # Если объект с таким id мы уже создавали раньше, возвращаем его из памяти (сохраняем одну ссылку)
        item_id = data.get("id")
        if item_id and isinstance(item_id, str) and item_id in self._instances:
            return self._instances[item_id]

        # Определяем, в какую именно модель нужно превратить этот словарь
        resolved_type = self._resolve_target_type(data, target_type)

        # Находим нужную функцию создания из таблицы
        handler = self._handlers.get(resolved_type)
        if handler is None:
            raise argument_exception(
                "target_type",
                f"Не удалось понять, в какую модель превратить словарь с ключами: {list(data.keys())}",
            )

        # Создаем объект модели
        model = handler(data)

        # Если у объекта есть id, восстанавливаем его и запоминаем объект в памяти
        if item_id and isinstance(model, base_model):
            model.id = str(item_id)
            self._instances[model.id] = model

        return model

    def deserialize_file(self, file_path: str, target_type: Optional[Any] = None) -> Any:
        # Читаем JSON файл с диска и десериализуем его содержимое
        if not isinstance(file_path, str) or not file_path.strip():
            raise argument_exception("file_path", "Путь к файлу должен быть непустой строкой.")

        if not os.path.exists(file_path):
            raise argument_exception("file_path", f"Файл не найден: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return self.deserialize(data, target_type)

    def deserialize_storage(self, data: Any, target_storage: Optional[Any] = None) -> Any:
        # Загрузка полного хранилища (все 6 секций: единицы, группы, номенклатура, склады, организации, рецепты)
        storage_dict = self.deserialize(data, target_type="storage_dict")

        # Если передали конкретный менеджер хранилища (например, storage_manager), наполняем его
        if target_storage is not None:
            if hasattr(target_storage, "clear"):
                target_storage.clear()

            # Добавляем данные в строгом порядке, чтобы сначала появились единицы и группы, а потом рецепты
            for sec_key in ["ranges", "groups", "nomenclatures", "storages", "organizations", "recipes"]:
                for entity in storage_dict.get(sec_key, []):
                    target_storage.add_entity(sec_key, entity)

            return target_storage

        return storage_dict

    def _resolve_target_type(self, data: dict, target_type: Optional[Any]) -> Any:
        # Понять, в какую модель нужно превратить словарь: по явному указанию или по таблице сигнатур
        if target_type is not None:
            if isinstance(target_type, str):
                return self._names_map.get(target_type.strip().lower(), target_type)
            return target_type

        keys = set(data.keys())

        # Если в словаре есть секции хранилища (например, ranges и nomenclatures) — это всё хранилище
        if len(keys & {"ranges", "groups", "nomenclatures", "storages", "organizations", "recipes"}) >= 2:
            return "storage_dict"

        # Проверяем совпадение по таблице характерных полей без каскада if
        for marker_keys, model_cls in self._signatures:
            if marker_keys & keys:
                return model_cls

        # Если в словаре есть только name — по умолчанию считаем группой
        return nomenclature_group_model if "name" in keys else None

    def _create_range(self, data: dict) -> range_model:
        # Создание единицы измерения (рекурсивно восстанавливаем базовую единицу, если она есть)
        base = self.deserialize(data.get("base_range"), range_model)
        return range_model(
            name=data.get("name", ""),
            conversion_factor=float(data.get("conversion_factor", 1.0)),
            base_range=base,
        )

    def _create_group(self, data: dict) -> nomenclature_group_model:
        # Создание группы номенклатуры (например, "Сырье" или "Упаковка")
        return nomenclature_group_model(name=data.get("name", ""))

    def _create_storage(self, data: dict) -> storage_model:
        # Создание склада (например, "Основной склад")
        return storage_model(name=data.get("name", ""))

    def _create_organization(self, data: dict) -> organization_model:
        # Создание организации со всеми реквизитами
        return organization_model(
            name=data.get("name", ""),
            inn=data.get("inn", ""),
            bic=data.get("bic", ""),
            account=data.get("account", ""),
            ownership_form=data.get("ownership_form", ""),
        )

    def _create_nomenclature(self, data: dict) -> nomenclature_model:
        # Создание товара/ингредиента (рекурсивно восстанавливаем связанную группу и единицу измерения)
        group = self.deserialize(data.get("group"), nomenclature_group_model)
        range_unit = self.deserialize(data.get("range"), range_model)
        return nomenclature_model(
            name=data.get("name", ""),
            full_name=data.get("full_name", data.get("name", "")),
            group=group,
            range_unit=range_unit,
        )

    def _create_recipe_row(self, data: dict) -> recipe_row_model:
        # Создание строки рецепта (рекурсивно восстанавливаем ингредиент и возможный вложенный полуфабрикат)
        nom = self.deserialize(data.get("nomenclature"), nomenclature_model)
        nested = self.deserialize(data.get("nested_recipe"), recipe_model)
        return recipe_row_model(
            nomenclature=nom,
            gross_weight=float(data.get("gross_weight", 0.0)),
            net_weight=float(data.get("net_weight", 0.0)),
            nested_recipe=nested,
        )

    def _create_recipe(self, data: dict) -> recipe_model:
        # Создание рецепта (рекурсивно восстанавливаем готовое блюдо и все строки ингредиентов)
        dish = self.deserialize(data.get("dish"), nomenclature_model)
        rows = [self.deserialize(r, recipe_row_model) for r in data.get("rows", [])]
        return recipe_model(name=data.get("name", ""), dish=dish, rows=rows)

    def _create_storage_dict(self, data: dict) -> Dict[str, List[base_model]]:
        # Создание словаря со всеми 6 секциями хранилища
        sections = {
            "ranges": range_model,
            "groups": nomenclature_group_model,
            "nomenclatures": nomenclature_model,
            "storages": storage_model,
            "organizations": organization_model,
            "recipes": recipe_model,
        }
        return {
            sec: [self.deserialize(item, model_cls) for item in data.get(sec, [])]
            for sec, model_cls in sections.items()
        }
