import pytest
from Src.Core.exceptions import argument_exception, operation_exception
from Src.Logics.storage_manager import storage_manager
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.organization_model import organization_model
from Src.Models.range_model import range_model
from Src.Models.settings_model import settings_model
from Src.Models.storage_model import storage_model


# 1. Проверка реализации шаблона Singleton для storage_manager
def test_storage_manager_singleton_same_instance():
    # Подготовка и Действие
    manager1 = storage_manager()
    manager2 = storage_manager()

    # Проверка
    assert manager1 is manager2


# 2. Проверка наличия всех ключевых секций в словаре данных хранилища
def test_storage_manager_data_all_sections_exist():
    # Подготовка
    manager = storage_manager()

    # Действие
    data = manager.data

    # Проверка
    assert "ranges" in data
    assert "groups" in data
    assert "nomenclatures" in data
    assert "storages" in data
    assert "organizations" in data


# 3. Проверка, что добавление сущности с уже существующим наименованием вызывает operation_exception
def test_storage_manager_add_entity_duplicate_name_raises_exception():
    # Подготовка
    manager = storage_manager()
    manager.clear()
    unit1 = range_model("грамм", 1.0)
    unit2 = range_model("грамм", 1.0)
    manager.add_entity("ranges", unit1)

    # Действие и проверка
    with pytest.raises(operation_exception):
        manager.add_entity("ranges", unit2)


# 4. Проверка, что дублирование уникального кода также вызывает исключение
def test_storage_manager_add_entity_duplicate_code_raises_exception():
    # Подготовка
    manager = storage_manager()
    manager.clear()
    unit1 = range_model("грамм", 1.0)
    unit2 = range_model("миллиграмм", 0.001)
    unit2.unique_code = unit1.unique_code
    manager.add_entity("ranges", unit1)

    # Действие и проверка
    with pytest.raises(operation_exception):
        manager.add_entity("ranges", unit2)


# 5. Проверка запрета добавления модели неподходящего типа в коллекцию
def test_storage_manager_add_entity_mismatched_type_raises_exception():
    # Подготовка
    manager = storage_manager()
    manager.clear()
    wrong_entity = storage_model("Склад сырья")

    # Действие и проверка
    with pytest.raises(argument_exception):
        manager.add_entity("ranges", wrong_entity)


# 6. Проверка ошибки добавления сущности с неизвестным ключом коллекции
def test_storage_manager_add_entity_invalid_key_raises_exception():
    # Подготовка
    manager = storage_manager()
    unit = range_model("грамм", 1.0)
    invalid_key = "unknown_category_123"

    # Действие и проверка
    with pytest.raises(argument_exception):
        manager.add_entity(invalid_key, unit)


# 7. Проверка ошибки добавления объекта, не являющегося наследником base_model
def test_storage_manager_add_entity_invalid_entity_raises_exception():
    # Подготовка
    manager = storage_manager()
    invalid_entity = "не_сущность_модели"

    # Действие и проверка
    with pytest.raises(argument_exception):
        manager.add_entity("ranges", invalid_entity)


# 8. Проверка инкапсуляции: внешняя модификация возвращаемого списка не ломает хранилище
def test_storage_manager_properties_return_copies():
    # Подготовка
    manager = storage_manager()
    manager.clear()
    unit = range_model("грамм", 1.0)
    manager.add_entity("ranges", unit)

    # Действие: попытка добавить элемент в возвращенный список
    manager.ranges.append(range_model("кг", 1000.0))

    # Проверка
    assert len(manager.ranges) == 1


# 9. Проверка переключения флага is_loaded при инициализации данных
def test_storage_manager_is_loaded_state():
    # Подготовка
    manager = storage_manager()
    manager.clear()
    initial_loaded = manager.is_loaded

    # Действие
    manager.init_data()

    # Проверка
    assert initial_loaded is False
    assert manager.is_loaded is True


# 10. Проверка полной очистки всех списков в хранилище
def test_storage_manager_clear_success():
    # Подготовка
    manager = storage_manager()
    manager.init_data()
    has_data_before = len(manager.ranges) > 0

    # Действие
    manager.clear()

    # Проверка
    assert has_data_before is True
    assert len(manager.ranges) == 0
    assert len(manager.groups) == 0
    assert len(manager.nomenclatures) == 0
    assert len(manager.storages) == 0
    assert len(manager.organizations) == 0
    assert manager.is_loaded is False


# 11. Проверка метода convert для наполнения коллекций хранилища из словаря
def test_storage_manager_convert_populate_from_dict():
    # Подготовка
    manager = storage_manager()
    manager.clear()
    sample_data = {
        "storages": [storage_model("Склад бара")],
        "groups": [nomenclature_group_model("Напитки")],
    }

    # Действие
    manager.convert(sample_data)

    # Проверка
    assert len(manager.storages) == 1
    assert len(manager.groups) == 1
    assert manager.storages[0].name == "Склад бара"
    assert manager.groups[0].name == "Напитки"
    assert manager.is_loaded is True


# 12. Проверка ошибки метода convert при передаче невалидного типа данных
def test_storage_manager_convert_invalid_source_type_raises_exception():
    # Подготовка
    manager = storage_manager()
    invalid_data = "строка_вместо_словаря"

    # Действие и проверка
    with pytest.raises(argument_exception):
        manager.convert(invalid_data)


# 13. Строгая проверка состава первичных данных (seed data) и ссылочной целостности объектов
def test_storage_manager_init_data_seed_entities_exact():
    # Подготовка
    manager = storage_manager()

    # Действие
    manager.init_data()

    # Проверка количества сущностей
    assert len(manager.ranges) == 3
    assert len(manager.groups) == 3
    assert len(manager.nomenclatures) == 8
    assert len(manager.storages) == 2
    assert len(manager.organizations) == 1
    assert len(manager.recipes) == 1

    # Проверка уникальности наименований в каждой коллекции
    for section_name, items in manager.data.items():
        names = [item.name.lower() for item in items]
        assert len(names) == len(set(names)), f"Обнаружены дубликаты в секции {section_name}"

    # Проверка ссылочной целостности (номенклатура ссылается на те же объекты в памяти)
    g_unit = next(item for item in manager.ranges if item.name == "грамм")
    kg_unit = next(item for item in manager.ranges if item.name == "кг")
    pcs_unit = next(item for item in manager.ranges if item.name == "шт")
    raw_group = next(item for item in manager.groups if item.name == "Сырье")
    dairy_group = next(item for item in manager.groups if item.name == "Молочная продукция")
    pack_group = next(item for item in manager.groups if item.name == "Упаковка")

    sugar = next(item for item in manager.nomenclatures if item.name == "Сахар")
    assert sugar.range is kg_unit
    assert sugar.group is raw_group

    milk = next(item for item in manager.nomenclatures if item.name == "Молоко 3.2%")
    assert milk.range is g_unit
    assert milk.group is dairy_group

    flour = next(item for item in manager.nomenclatures if item.name == "Мука")
    assert flour.range is g_unit

    egg = next(item for item in manager.nomenclatures if item.name == "Яйцо")
    assert egg.range is pcs_unit

    box = next(item for item in manager.nomenclatures if item.name == "Контейнер")
    assert box.group is pack_group
    assert box.range is pcs_unit

    pancakes_dish = next(item for item in manager.nomenclatures if item.name == "Блинчики")
    assert pancakes_dish.group is dairy_group
    assert pancakes_dish.range is pcs_unit


# 14. Проверка ветки первого старта is_first_start = False: данные не должны создаваться
def test_storage_manager_start_with_first_start_false():
    # Подготовка
    manager = storage_manager()
    manager.clear()

    settings = settings_model()
    settings.organization = organization_model(
        name="ООО Ромашка",
        inn="7701234567",
        bic="044525225",
        account="40702810938000012345",
        ownership_form="ООО",
    )
    settings.is_first_start = False

    # Действие
    manager.start(settings)

    # Проверка
    assert manager.is_loaded is True
    assert len(manager.ranges) == 0
    assert len(manager.groups) == 0
    assert len(manager.nomenclatures) == 0
    assert len(manager.storages) == 0
    assert len(manager.recipes) == 0


# 15. Проверка ветки первого старта is_first_start = True: данные успешно формируются
def test_storage_manager_start_with_first_start_true():
    # Подготовка
    manager = storage_manager()
    manager.clear()

    settings = settings_model()
    settings.organization = organization_model(
        name="ООО Ромашка",
        inn="7701234567",
        bic="044525225",
        account="40702810938000012345",
        ownership_form="ООО",
    )
    settings.is_first_start = True

    # Действие
    manager.start(settings)

    # Проверка
    assert manager.is_loaded is True
    assert len(manager.nomenclatures) == 8
    assert len(manager.organizations) == 1
    assert len(manager.recipes) == 1
    assert manager.organizations[0].name == "ООО Ромашка"


# 16. Проверка корректности сформированного рецепта при первом старте (Docs/Recipe.md)
def test_storage_manager_init_data_recipe_exact():
    # Подготовка
    manager = storage_manager()

    # Действие
    manager.init_data()

    # Проверка
    recipe = manager.recipes[0]
    assert recipe.name == "Блинчики классические"
    assert recipe.dish.name == "Блинчики"
    assert len(recipe.rows) == 7
    assert recipe.gross_weight == 188.0
    assert recipe.net_weight == 173.0

    # Проверка ссылочной целостности: сырье и упаковка рецепта совпадают с позициями номенклатуры
    recipe_nomenclatures = {row.nomenclature.name for row in recipe.rows}
    assert "Молоко 3.2%" in recipe_nomenclatures
    assert "Мука" in recipe_nomenclatures
    assert "Яйцо" in recipe_nomenclatures
    assert "Сахар" in recipe_nomenclatures
    assert "Соль" in recipe_nomenclatures
    assert "Масло растительное" in recipe_nomenclatures
    assert "Контейнер" in recipe_nomenclatures


# 17. Проверка инкапсуляции списка рецептов в хранилище
def test_storage_manager_recipes_returns_copy():
    # Подготовка
    manager = storage_manager()
    manager.init_data()
    initial_count = len(manager.recipes)
    dish = manager.recipes[0].dish

    # Действие: попытка добавить рецепт в возвращенный список
    from Src.Models.recipe_model import recipe_model
    manager.recipes.append(recipe_model(name="Левый рецепт", dish=dish))

    # Проверка: оригинальный список не изменился
    assert len(manager.recipes) == initial_count


# 18. Проверка бизнес-правила: 1 блюдо - 1 техкарта (запрет дублирования карты для одного блюда)
def test_storage_manager_one_dish_one_recipe_rule_raises_exception():
    # Подготовка
    manager = storage_manager()
    manager.init_data()
    existing_recipe = manager.recipes[0]
    dish = existing_recipe.dish

    from Src.Models.recipe_model import recipe_model
    second_recipe = recipe_model(name="Блинчики альтернативные", dish=dish)

    # Действие и проверка
    with pytest.raises(operation_exception):
        manager.add_entity("recipes", second_recipe)