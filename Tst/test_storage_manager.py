import pytest
from Src.Core.exceptions import argument_exception
from Src.Logics.storage_manager import storage_manager
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.range_model import range_model
from Src.Models.storage_model import storage_model


# Проверка реализации шаблона Singleton для storage_manager
def test_storage_manager_singleton_same_instance():
    # Подготовка и Действие
    manager1 = storage_manager()
    manager2 = storage_manager()

    # Проверки
    assert manager1 is manager2
    assert manager1 == manager2


# Проверка наличия всех ключевых секций в словаре данных хранилища
def test_storage_manager_data_all_sections_exist():
    # Подготовка
    manager = storage_manager()

    # Действие
    data = manager.data

    # Проверки
    assert "ranges" in data
    assert "groups" in data
    assert "nomenclatures" in data
    assert "storages" in data
    assert "organizations" in data


# Проверка уникальности сохраняемых объектов по unique_code
def test_storage_manager_add_entity_ignore_duplicate_code():
    # Подготовка
    manager = storage_manager()
    manager.clear()
    unit1 = range_model("грамм", 1.0)
    unit2 = range_model("грамм", 1.0)
    unit2.unique_code = unit1.unique_code

    # Действие
    manager.add_entity("ranges", unit1)
    manager.add_entity("ranges", unit2)

    # Проверки
    assert len(manager.ranges) == 1
    assert manager.ranges[0] == unit1


# Проверка ошибки добавления сущности с неизвестным ключом коллекции
def test_storage_manager_add_entity_invalid_key_raises_exception():
    manager = storage_manager()
    unit = range_model("грамм", 1.0)
    with pytest.raises(argument_exception):
        manager.add_entity("unknown_category_123", unit)


# Проверка ошибки добавления объекта, не являющегося наследником base_model
def test_storage_manager_add_entity_invalid_entity_raises_exception():
    manager = storage_manager()
    with pytest.raises(argument_exception):
        manager.add_entity("ranges", "не_сущность_модели")


# Проверка очистки всех списков в хранилище
def test_storage_manager_clear_success():
    manager = storage_manager()
    manager.init_data()
    assert len(manager.ranges) > 0

    manager.clear()
    assert len(manager.ranges) == 0
    assert len(manager.groups) == 0
    assert len(manager.nomenclatures) == 0
    assert len(manager.storages) == 0
    assert len(manager.organizations) == 0


# Проверка метода convert для наполнения коллекций хранилища из словаря
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

    # Проверки
    assert len(manager.storages) == 1
    assert len(manager.groups) == 1
    assert manager.storages[0].name == "Склад бара"
    assert manager.groups[0].name == "Напитки"


# Проверка ошибки метода convert при передаче невалидного типа данных
def test_storage_manager_convert_invalid_source_type_raises_exception():
    # Подготовка
    manager = storage_manager()
    invalid_source = "строка_вместо_словаря"

    # Действие и Проверки
    with pytest.raises(argument_exception):
        manager.convert(invalid_source)


# Проверка корректности состава первичных данных (seed data) при первом старте
def test_storage_manager_init_data_seed_entities_on_first_start():
    # Подготовка
    manager = storage_manager()

    # Действие
    manager.init_data()

    # Проверки
    assert len(manager.ranges) >= 3
    assert len(manager.groups) >= 2
    assert len(manager.nomenclatures) >= 2
    assert len(manager.storages) >= 2
    assert len(manager.organizations) >= 1

    # Проверка связей созданной номенклатуры
    sugar = next(item for item in manager.nomenclatures if item.name == "Сахар")
    assert sugar.range.name == "кг"
    assert sugar.range.conversion_factor == 1000.0
    assert sugar.group.name == "Сырье"