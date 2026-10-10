import pytest
from Src.Core.exceptions import argument_exception
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_model import recipe_model
from Src.Models.recipe_row_model import recipe_row_model


@pytest.fixture
def sample_data():
    # Фикстура базовых сущностей для тестирования рецептов
    g_unit = range_model.create_gram("грамм")
    pcs_unit = range_model("шт", 1.0)

    group_raw = nomenclature_group_model.create("Сырье")
    group_dish = nomenclature_group_model.create("Готовая продукция")
    group_pack = nomenclature_group_model.create("Упаковка")

    milk = nomenclature_model.create(
        "Молоко 3.2%", "Молоко пастеризованное", group_raw, g_unit
    )
    flour = nomenclature_model.create("Мука", "Мука пшеничная в/с", group_raw, g_unit)
    egg = nomenclature_model.create("Яйцо", "Яйцо куриное", group_raw, pcs_unit)
    pancakes_dish = nomenclature_model.create(
        "Блинчики", "Блинчики классические (порция 2 шт.)", group_dish, pcs_unit
    )
    box = nomenclature_model.create(
        "Ланч-бокс", "Контейнер пищевой картонный", group_pack, pcs_unit
    )

    return {
        "g_unit": g_unit,
        "pcs_unit": pcs_unit,
        "milk": milk,
        "flour": flour,
        "egg": egg,
        "pancakes_dish": pancakes_dish,
        "box": box,
    }


# 1. Успешное создание строки рецепта через конструктор и фабричный метод
def test_recipe_row_model_init_success(sample_data):
    # Подготовка
    flour = sample_data["flour"]

    # Действие
    row1 = recipe_row_model(flour, 50.0, 50.0)
    row2 = recipe_row_model.create(flour, 60.0, 50.0)

    # Проверка
    assert row1.nomenclature is flour
    assert row1.gross_weight == 50.0
    assert row1.net_weight == 50.0
    assert row1.name == flour.name
    assert row1.range is flour.range
    assert row1.id != ""

    assert row2.gross_weight == 60.0
    assert row2.net_weight == 50.0


# 2. Ошибка: неверный тип номенклатуры в строке рецепта
def test_recipe_row_model_invalid_nomenclature_raises_exception():
    # Подготовка
    invalid_nom = "не объект номенклатуры"

    # Действие и проверка
    with pytest.raises(argument_exception):
        recipe_row_model(invalid_nom, 100.0, 100.0)


# 3. Ошибка: отрицательный вес брутто или нетто в строке рецепта
def test_recipe_row_model_negative_weights_raise_exception(sample_data):
    # Подготовка
    milk = sample_data["milk"]

    # Действие и проверка
    with pytest.raises(argument_exception):
        recipe_row_model(milk, -10.0, 10.0)

    with pytest.raises(argument_exception):
        recipe_row_model(milk, 10.0, -5.0)


# 4. Ошибка: вес нетто превышает вес брутто в строке рецепта
def test_recipe_row_model_net_greater_than_gross_raises_exception(sample_data):
    # Подготовка
    milk = sample_data["milk"]

    # Действие и проверка
    with pytest.raises(argument_exception):
        recipe_row_model(milk, 50.0, 60.0)


# 5. Успешное создание технологической карты (рецепта) с расчетом брутто и нетто
def test_recipe_model_init_and_weight_calculation_success(sample_data):
    # Подготовка
    milk = sample_data["milk"]
    flour = sample_data["flour"]
    egg = sample_data["egg"]
    dish = sample_data["pancakes_dish"]

    row_milk = recipe_row_model.create(milk, 100.0, 100.0)
    row_flour = recipe_row_model.create(flour, 50.0, 50.0)
    row_egg = recipe_row_model.create(egg, 1.0, 1.0)

    # Действие
    recipe = recipe_model.create(
        name="Блинчики классические",
        dish=dish,
        rows=[row_milk, row_flour, row_egg],
    )

    # Проверка
    assert recipe.name == "Блинчики классические"
    assert recipe.dish is dish
    assert len(recipe.rows) == 3
    assert recipe.gross_weight == 151.0
    assert recipe.net_weight == 151.0


# 6. Проверка динамического пересчета веса Брутто и Нетто при добавлении ингредиента
def test_recipe_model_add_row_recalculates_weight(sample_data):
    # Подготовка
    flour = sample_data["flour"]
    milk = sample_data["milk"]
    dish = sample_data["pancakes_dish"]

    recipe = recipe_model(
        name="Тесто",
        dish=dish,
        rows=[recipe_row_model.create(flour, 50.0, 50.0)],
    )
    assert recipe.gross_weight == 50.0
    assert recipe.net_weight == 50.0

    # Действие: добавление молока
    recipe.add_row(recipe_row_model.create(milk, 100.0, 95.0))

    # Проверка
    assert len(recipe.rows) == 2
    assert recipe.gross_weight == 150.0
    assert recipe.net_weight == 145.0


# 7. Проверка динамического пересчета веса Брутто и Нетто при исключении ингредиента
def test_recipe_model_delete_row_recalculates_weight(sample_data):
    # Подготовка
    flour = sample_data["flour"]
    milk = sample_data["milk"]
    dish = sample_data["pancakes_dish"]

    row_flour = recipe_row_model.create(flour, 50.0, 50.0)
    row_milk = recipe_row_model.create(milk, 100.0, 95.0)
    recipe = recipe_model(name="Тесто", dish=dish, rows=[row_flour, row_milk])

    # Действие: удаление муки
    recipe.delete_row(row_flour)

    # Проверка
    assert len(recipe.rows) == 1
    assert recipe.gross_weight == 100.0
    assert recipe.net_weight == 95.0


# 8. Ошибка: исключение строки, которой нет в рецепте
def test_recipe_model_delete_nonexistent_row_raises_exception(sample_data):
    # Подготовка
    flour = sample_data["flour"]
    milk = sample_data["milk"]
    dish = sample_data["pancakes_dish"]

    recipe = recipe_model(name="Тесто", dish=dish)
    row_milk = recipe_row_model.create(milk, 100.0, 100.0)

    # Действие и проверка
    with pytest.raises(argument_exception):
        recipe.delete_row(row_milk)


# 9. Инкапсуляция: внешняя модификация возвращаемого списка rows не меняет рецепт
def test_recipe_model_rows_encapsulation(sample_data):
    # Подготовка
    flour = sample_data["flour"]
    milk = sample_data["milk"]
    dish = sample_data["pancakes_dish"]

    recipe = recipe_model(
        name="Тесто",
        dish=dish,
        rows=[recipe_row_model.create(flour, 50.0, 50.0)],
    )

    # Действие: попытка добавить строку в скопированный список
    recipe.rows.append(recipe_row_model.create(milk, 100.0, 100.0))

    # Проверка
    assert len(recipe.rows) == 1


# 10. Рецепт с упаковкой: расчет брутто и нетто с тарой
def test_recipe_model_with_packaging(sample_data):
    # Подготовка
    milk = sample_data["milk"]
    box = sample_data["box"]
    dish = sample_data["pancakes_dish"]

    # Ингредиент: молоко 100г, чистый выход 95г
    row_ingredient = recipe_row_model.create(milk, gross_weight=100.0, net_weight=95.0)
    # Упаковка: вес тары 15г брутто, 0г нетто (упаковка не употребляется в пищу)
    row_pack = recipe_row_model.create(box, gross_weight=15.0, net_weight=0.0)

    # Действие
    packaged_dish_recipe = recipe_model.create(
        name="Блинчики на вынос с упаковкой",
        dish=dish,
        rows=[row_ingredient, row_pack],
    )

    # Проверка: брутто включает упаковку, нетто только съедобную часть
    assert packaged_dish_recipe.gross_weight == 115.0
    assert packaged_dish_recipe.net_weight == 95.0


# 11. Ошибка: некорректный тип блюда при создании рецепта
def test_recipe_model_invalid_dish_raises_exception():
    # Подготовка
    invalid_dish = "строка_вместо_номенклатуры"

    # Действие и проверка
    with pytest.raises(argument_exception):
        recipe_model(name="Рецепт", dish=invalid_dish)
