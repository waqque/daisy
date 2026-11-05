import json
import os
import pytest

from Src.Core.exceptions import argument_exception
from Src.Logics.convert_factory import convert_factory
from Src.Logics.deserialize_factory import deserialize_factory
from Src.Logics.storage_manager import storage_manager
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.organization_model import organization_model
from Src.Models.range_model import range_model
from Src.Models.recipe_model import recipe_model
from Src.Models.recipe_row_model import recipe_row_model
from Src.Models.storage_model import storage_model


# 1. Проверка десериализации базовой единицы измерения
def test_deserialize_factory_range_base_unit_success():
    # Подготовка
    factory = deserialize_factory()
    data = {
        "id": "1",
        "name": "грамм",
        "conversion_factor": 1.0,
        "base_range": None,
    }

    # Действие
    result = factory.deserialize(data, range_model)

    # Проверка
    assert isinstance(result, range_model)
    assert result.id == "1"
    assert result.name == "грамм"
    assert result.conversion_factor == 1.0
    assert result.base_range is None


# 2. Проверка рекурсивной десериализации производной единицы измерения (килограмм с базовым граммом)
def test_deserialize_factory_range_derived_unit_recursive_success():
    # Подготовка
    factory = deserialize_factory()
    data = {
        "id": "2",
        "name": "кг",
        "conversion_factor": 1000.0,
        "base_range": {
            "id": "1",
            "name": "грамм",
            "conversion_factor": 1.0,
            "base_range": None,
        },
    }

    # Действие
    result = factory.deserialize(data, range_model)

    # Проверка
    assert isinstance(result, range_model)
    assert result.name == "кг"
    assert result.conversion_factor == 1000.0
    assert result.base_range is not None
    assert result.base_range.name == "грамм"
    assert result.base_range.id == "1"
    assert result.to_base(2.0) == 2000.0


# 3. Проверка десериализации группы номенклатуры
def test_deserialize_factory_nomenclature_group_success():
    # Подготовка
    factory = deserialize_factory()
    data = {"id": "10", "name": "Сырье"}

    # Действие
    result = factory.deserialize(data, nomenclature_group_model)

    # Проверка
    assert isinstance(result, nomenclature_group_model)
    assert result.id == "10"
    assert result.name == "Сырье"


# 4. Проверка десериализации склада
def test_deserialize_factory_storage_model_success():
    # Подготовка
    factory = deserialize_factory()
    data = {"id": "20", "name": "Основной склад"}

    # Действие
    result = factory.deserialize(data, storage_model)

    # Проверка
    assert isinstance(result, storage_model)
    assert result.id == "20"
    assert result.name == "Основной склад"


# 5. Проверка десериализации организации со всеми реквизитами
def test_deserialize_factory_organization_success():
    # Подготовка
    factory = deserialize_factory()
    data = {
        "id": "30",
        "name": "Ромашка",
        "inn": "1234567890",
        "bic": "123456789",
        "account": "12345678901234567890",
        "ownership_form": "ООО",
    }

    # Действие
    result = factory.deserialize(data, organization_model)

    # Проверка
    assert isinstance(result, organization_model)
    assert result.id == "30"
    assert result.name == "Ромашка"
    assert result.inn == "1234567890"
    assert result.bic == "123456789"
    assert result.account == "12345678901234567890"
    assert result.ownership_form == "ООО"


# 6. Проверка рекурсивной десериализации номенклатуры (включая группу и меру)
def test_deserialize_factory_nomenclature_recursive_success():
    # Подготовка
    factory = deserialize_factory()
    data = {
        "id": "100",
        "name": "Сахар",
        "full_name": "Сахар белый ГОСТ",
        "group": {
            "id": "10",
            "name": "Сырье",
        },
        "range": {
            "id": "2",
            "name": "кг",
            "conversion_factor": 1000.0,
            "base_range": {
                "id": "1",
                "name": "грамм",
                "conversion_factor": 1.0,
                "base_range": None,
            },
        },
    }

    # Действие
    result = factory.deserialize(data, nomenclature_model)

    # Проверка
    assert isinstance(result, nomenclature_model)
    assert result.id == "100"
    assert result.name == "Сахар"
    assert result.full_name == "Сахар белый ГОСТ"
    assert isinstance(result.group, nomenclature_group_model)
    assert result.group.name == "Сырье"
    assert isinstance(result.range, range_model)
    assert result.range.name == "кг"
    assert result.range.base_range.name == "грамм"


# 7. Проверка рекурсивной десериализации рецепта с ингредиентами
def test_deserialize_factory_recipe_recursive_success():
    # Подготовка
    factory = deserialize_factory()
    data = {
        "id": "50",
        "name": "Рецепт блинчиков",
        "dish": {
            "id": "30",
            "name": "Блинчики",
            "full_name": "Блинчики порционные",
            "group": {"id": "10", "name": "Кулинария"},
            "range": {"id": "3", "name": "шт", "conversion_factor": 1.0},
        },
        "rows": [
            {
                "id": "40",
                "name": "Мука",
                "gross_weight": 200.0,
                "net_weight": 200.0,
                "nested_recipe": None,
                "nomenclature": {
                    "id": "20",
                    "name": "Мука",
                    "full_name": "Мука пшеничная в/с",
                    "group": {"id": "10", "name": "Сырье"},
                    "range": {"id": "1", "name": "грамм", "conversion_factor": 1.0},
                },
            }
        ],
    }

    # Действие
    result = factory.deserialize(data, recipe_model)

    # Проверка
    assert isinstance(result, recipe_model)
    assert result.name == "Рецепт блинчиков"
    assert result.dish.name == "Блинчики"
    assert len(result.rows) == 1
    assert result.rows[0].nomenclature.name == "Мука"
    assert result.gross_weight == 200.0


# 8. Проверка кэширования экземпляров (Identity Map) и сохранения ссылочной целостности
def test_deserialize_factory_preserves_object_identity_and_shared_instances():
    # Подготовка
    factory = deserialize_factory()
    gram_data = {
        "id": "1",
        "name": "грамм",
        "conversion_factor": 1.0,
        "base_range": None,
    }
    kg_data = {
        "id": "2",
        "name": "кг",
        "conversion_factor": 1000.0,
        "base_range": gram_data,
    }

    # Действие
    gram_obj = factory.deserialize(gram_data, range_model)
    kg_obj = factory.deserialize(kg_data, range_model)

    # Проверка
    assert kg_obj.base_range is gram_obj
    assert id(kg_obj.base_range) == id(gram_obj)


# 9. Проверка десериализации из строки JSON
def test_deserialize_factory_from_json_string_success():
    # Подготовка
    factory = deserialize_factory()
    json_str = json.dumps({"name": "Сырье", "id": "10"})

    # Действие
    result = factory.deserialize(json_str, nomenclature_group_model)

    # Проверка
    assert isinstance(result, nomenclature_group_model)
    assert result.name == "Сырье"


# 10. Проверка десериализации списка объектов
def test_deserialize_factory_list_of_entities_success():
    # Подготовка
    factory = deserialize_factory()
    data_list = [
        {"name": "Сырье", "id": "10"},
        {"name": "Упаковка", "id": "11"},
    ]

    # Действие
    result = factory.deserialize(data_list, nomenclature_group_model)

    # Проверка
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0].name == "Сырье"
    assert result[1].name == "Упаковка"


# 11. Проверка обработки None и уже готового объекта
def test_deserialize_factory_none_and_already_instantiated_model():
    # Подготовка
    factory = deserialize_factory()
    existing_model = nomenclature_group_model("Тара")

    # Действие и проверка
    assert factory.deserialize(None) is None
    assert factory.deserialize(existing_model) is existing_model


# 12. Проверка ошибки при некорректных входных данных
def test_deserialize_factory_invalid_input_type_raises_exception():
    # Подготовка
    factory = deserialize_factory()

    # Действие и проверка
    with pytest.raises(argument_exception):
        factory.deserialize(12345)


# 13. Сравнение десериализованных из Json моделей с моделями в storage_manager
def test_deserialize_factory_matches_storage_manager_models():
    # 1. Инициализируем оригинальное хранилище демонстрационными данными
    manager = storage_manager()
    manager.clear()
    manager.init_data()

    # 2. Сериализуем всё хранилище через convert_factory в JSON
    c_factory = convert_factory()
    serialized_storage = c_factory.convert(manager.data)

    # 3. Десериализуем полученные данные через deserialize_factory
    d_factory = deserialize_factory()
    restored_dict = d_factory.deserialize(serialized_storage)

    # 4. Сравнение секции единиц измерения (ranges)
    orig_ranges = manager.ranges
    rest_ranges = restored_dict["ranges"]
    assert len(rest_ranges) == len(orig_ranges)
    for orig, rest in zip(orig_ranges, rest_ranges):
        assert rest.id == orig.id
        assert rest.name == orig.name
        assert rest.conversion_factor == orig.conversion_factor
        if orig.base_range is not None:
            assert rest.base_range is not None
            assert rest.base_range.id == orig.base_range.id
            assert rest.base_range.name == orig.base_range.name

    # 5. Сравнение секции групп номенклатуры (groups)
    orig_groups = manager.groups
    rest_groups = restored_dict["groups"]
    assert len(rest_groups) == len(orig_groups)
    for orig, rest in zip(orig_groups, rest_groups):
        assert rest.id == orig.id
        assert rest.name == orig.name

    # 6. Сравнение секции номенклатуры (nomenclatures)
    orig_noms = manager.nomenclatures
    rest_noms = restored_dict["nomenclatures"]
    assert len(rest_noms) == len(orig_noms)
    for orig, rest in zip(orig_noms, rest_noms):
        assert rest.id == orig.id
        assert rest.name == orig.name
        assert rest.full_name == orig.full_name
        assert rest.group.id == orig.group.id
        assert rest.range.id == orig.range.id

    # 7. Сравнение секции складов (storages)
    orig_storages = manager.storages
    rest_storages = restored_dict["storages"]
    assert len(rest_storages) == len(orig_storages)
    for orig, rest in zip(orig_storages, rest_storages):
        assert rest.id == orig.id
        assert rest.name == orig.name

    # 8. Сравнение секции организаций (organizations)
    orig_orgs = manager.organizations
    rest_orgs = restored_dict["organizations"]
    assert len(rest_orgs) == len(orig_orgs)
    for orig, rest in zip(orig_orgs, rest_orgs):
        assert rest.id == orig.id
        assert rest.name == orig.name
        assert rest.inn == orig.inn
        assert rest.bic == orig.bic
        assert rest.account == orig.account
        assert rest.ownership_form == orig.ownership_form

    # 9. Сравнение секции рецептов (recipes)
    orig_recipes = manager.recipes
    rest_recipes = restored_dict["recipes"]
    assert len(rest_recipes) == len(orig_recipes)
    for orig, rest in zip(orig_recipes, rest_recipes):
        assert rest.id == orig.id
        assert rest.name == orig.name
        assert rest.dish.id == orig.dish.id
        assert len(rest.rows) == len(orig.rows)
        assert rest.gross_weight == pytest.approx(orig.gross_weight)
        assert rest.net_weight == pytest.approx(orig.net_weight)

    # 10. Проверка ссылочной целостности десериализованного графа:
    # Базовый грамм в ranges[0] и base_range у килограмма - это один и тот же объект в памяти
    rest_gram = next(u for u in rest_ranges if u.name == "грамм")
    rest_kg = next(u for u in rest_ranges if u.name == "кг")
    assert rest_kg.base_range is rest_gram

    # Единица измерения у Сахара ссылается на этот же килограмм
    rest_sugar = next(n for n in rest_noms if n.name == "Сахар")
    assert rest_sugar.range is rest_kg


# 14. Проверка десериализации прямо из существующего файла Json/storage.json
def test_deserialize_factory_from_storage_json_file_matches_storage():
    # Подготовка
    json_path = os.path.join(os.path.dirname(__file__), "..", "Json", "storage.json")
    assert os.path.exists(json_path)

    manager = storage_manager()
    manager.clear()
    manager.init_data()

    # Действие
    factory = deserialize_factory()
    loaded_storage = factory.deserialize_file(json_path)

    # Проверка
    assert "ranges" in loaded_storage
    assert "nomenclatures" in loaded_storage
    assert "recipes" in loaded_storage
    assert len(loaded_storage["ranges"]) == len(manager.ranges)
    assert len(loaded_storage["nomenclatures"]) == len(manager.nomenclatures)
    assert len(loaded_storage["recipes"]) == len(manager.recipes)


# 15. Проверка заполнения существующего storage_manager методом deserialize_storage
def test_deserialize_factory_deserialize_storage_populates_manager():
    # Подготовка
    json_path = os.path.join(os.path.dirname(__file__), "..", "Json", "storage.json")
    manager = storage_manager()
    manager.clear()
    assert len(manager.ranges) == 0

    factory = deserialize_factory()

    # Действие
    factory.deserialize_storage(json_path, target_storage=manager)

    # Проверка
    assert len(manager.ranges) > 0
    assert len(manager.nomenclatures) > 0
    assert len(manager.recipes) > 0
    assert len(manager.storages) > 0
    assert len(manager.organizations) > 0
