import pytest
from Src.Core.exceptions import argument_exception
from Src.Dtos.filter_dto import filter_dto, filter_item_dto
from Src.Dtos.filter_type_enum import filter_type_enum
from Src.Logics.prototype import prototype
from Src.Logics.storage_manager import storage_manager
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.range_model import range_model
from Src.Models.settings_model import settings_model


def test_contains_data_prototype():
    # Проверяем фильтрацию складских транзакций по единице измерения
    settings = settings_model()
    settings.is_first_start = True
    manager = storage_manager()
    manager.clear()
    manager.build()

    dto = filter_dto()
    item = filter_item_dto("name", "eq", "кг")
    dto.filters = [item]

    pr = prototype(manager.data[storage_manager.transaction_key()])
    result = pr.clone(dto)

    assert len(result.data) > 0


def test_prototype_filter_nomenclature_equals_and_like():
    manager = storage_manager()
    manager.init_data()
    proto = prototype(manager.nomenclatures)

    f_eq = filter_dto()
    f_eq.add("name", filter_type_enum.EQUALS, "Сахар")
    res_eq = proto.clone(f_eq)
    assert len(res_eq.data) == 1
    assert res_eq.data[0].name == "Сахар"

    f_like = filter_dto()
    f_like.add("name", filter_type_enum.LIKE, "масло")
    res_like = proto.clone(f_like)
    assert len(res_like.data) == 1
    assert "масло" in res_like.data[0].name.lower()


def test_prototype_filter_by_unique_code():
    manager = storage_manager()
    manager.init_data()
    nomenclatures = manager.nomenclatures
    target = nomenclatures[0]

    proto = prototype(nomenclatures)
    f = filter_dto()
    f.add("unique_code", filter_type_enum.EQUALS, target.unique_code)

    res = proto.clone(f)
    assert len(res.data) == 1
    assert res.data[0].unique_code == target.unique_code


def test_prototype_nested_search_range_base_range():
    # Поиск единицы измерения по имени ее базовой единицы
    g_unit = range_model.create_gram("грамм")
    kg_unit = range_model.create_kilogram("кг", base_range=g_unit)
    pcs_unit = range_model("шт", 1.0)

    proto = prototype([kg_unit, pcs_unit])

    f = filter_dto()
    f.add("name", filter_type_enum.EQUALS, "грамм")
    res = proto.clone(f)

    assert len(res.data) == 1
    assert res.data[0].name == "кг"


def test_prototype_nested_search_group_parent_group():
    # Поиск группы по родительской группе и проверка защиты от цикла
    parent = nomenclature_group_model.create("Пищевое сырье")
    child = nomenclature_group_model.create("Сахар и подсластители", parent_group=parent)
    other = nomenclature_group_model.create("Хозтовары")

    proto = prototype([child, other])

    f = filter_dto()
    f.add("name", filter_type_enum.EQUALS, "Пищевое сырье")
    res = proto.clone(f)

    assert len(res.data) == 1
    assert res.data[0].name == "Сахар и подсластители"

    with pytest.raises(argument_exception):
        parent.parent_group = child


def test_prototype_nested_search_nomenclature_group_and_range():
    manager = storage_manager()
    manager.init_data()
    proto = prototype(manager.nomenclatures)

    f_group = filter_dto()
    f_group.add("name", filter_type_enum.EQUALS, "Молочная продукция")
    res_group = proto.clone(f_group)
    assert len(res_group.data) > 0
    assert all(item.group.name == "Молочная продукция" for item in res_group.data)

    f_base = filter_dto()
    f_base.add("name", filter_type_enum.EQUALS, "грамм")
    res_base = proto.clone(f_base)
    assert len(res_base.data) > 0


def test_prototype_nested_search_recipe_rows_and_dish():
    manager = storage_manager()
    manager.init_data()
    proto = prototype(manager.recipes)

    f_dish = filter_dto()
    f_dish.add("name", filter_type_enum.LIKE, "Блинчики")
    res_dish = proto.clone(f_dish)
    assert len(res_dish.data) == 1

    f_ing = filter_dto()
    f_ing.add("name", filter_type_enum.EQUALS, "Сахар")
    res_ing = proto.clone(f_ing)
    assert len(res_ing.data) == 1
    assert res_ing.data[0].name == "Блинчики классические"


def test_prototype_dotted_path_matching():
    # Фильтрация по явному вложенному пути через точку
    manager = storage_manager()
    manager.init_data()
    proto = prototype(manager.nomenclatures)

    f = filter_dto()
    f.add("range.base_range.name", filter_type_enum.EQUALS, "грамм")
    res = proto.clone(f)
    assert len(res.data) > 0
    assert any(nom.name == "Сахар" for nom in res.data)


def test_prototype_none_field_does_not_match_empty_string():
    pcs_unit = range_model("шт", 1.0)
    proto = prototype([pcs_unit])

    f = filter_dto()
    f.add("base_range", filter_type_enum.EQUALS, "")
    assert len(proto.clone(f).data) == 0


def test_prototype_empty_filter_returns_all_data():
    items = [1, 2, 3]
    proto = prototype(items)
    assert proto.clone(None).data == items
    assert proto.clone(filter_dto()).data == items
